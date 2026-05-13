"""Telegram-хендлеры: приём видео/аудио/ссылок и прогон через пайплайн."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, FSInputFile, Message

from . import chat, rate_limit
from .media import (
    MediaError,
    MediaInfo,
    cleanup_workdir,
    convert_to_audio,
    download_from_url,
    extract_url,
    is_url,
    make_workdir,
    split_into_chunks,
)
from .summarize import SummarizeError, Summaries, summarize_all_levels
from .transcribe import TranscribeError, transcribe_chunks

logger = logging.getLogger(__name__)
router = Router()

# Глобальный лок: одна задача в момент времени. Защита от перегрева Groq rate limit.
_processing_lock = asyncio.Lock()

# Telegram Bot API без локального сервера — лимит на скачивание файла.
TELEGRAM_FILE_LIMIT_BYTES = 20 * 1024 * 1024

WELCOME = (
    "👋 Привет! Я бот-транскриптор.\n\n"
    "Кидай мне:\n"
    "• 🎥 Видео-файл (до 20 МБ из Telegram)\n"
    "• 🎙 Голосовое или video note\n"
    "• 🔗 Ссылку на YouTube / Reels / TikTok / VK / Rutube / Я.Диск / Google Drive\n\n"
    "В ответ получишь три уровня разбора:\n"
    "🟢 Лёгкий — о чём ролик\n"
    "🟡 Средний — конспект с разбором\n"
    "🔴 Полный — детальный разбор\n\n"
    "Плюс файлом — полная транскрипция.\n\n"
    "💬 После разбора можешь задать мне вопрос про видео — я помню его и отвечу.\n\n"
    "📦 Файл больше 20 МБ? Загрузи на Я.Диск или Google Drive с публичной ссылкой и пришли ссылку.\n\n"
    "Команды:\n"
    "/ask <вопрос> — спросить про последнее видео\n"
    "/forget — забыть последнее видео\n"
    "/limits — сколько минут осталось на сегодня\n"
    "/myid — твой Telegram ID\n"
    "/help — эта справка"
)


@router.message(CommandStart())
async def on_start(msg: Message) -> None:
    await msg.answer(WELCOME)


@router.message(Command("help"))
async def on_help(msg: Message) -> None:
    await msg.answer(WELCOME)


@router.message(Command("myid"))
async def on_myid(msg: Message) -> None:
    await msg.answer(f"Твой Telegram ID: <code>{msg.from_user.id}</code>", parse_mode="HTML")


@router.message(Command("limits"))
async def on_limits(msg: Message) -> None:
    user_id = msg.from_user.id
    used = rate_limit.used_minutes(user_id)
    remaining = rate_limit.remaining_minutes(user_id)
    if remaining == float("inf"):
        await msg.answer("Лимит на пользователя отключён. Используй с умом 🙃")
        return
    await msg.answer(
        f"📊 За последние 24ч:\n"
        f"• Использовано: {used:.1f} мин\n"
        f"• Осталось: {remaining:.1f} мин"
    )


@router.message(Command("ask"))
async def on_ask(msg: Message) -> None:
    """Явная команда: /ask <вопрос>. Альтернатива простому тексту."""
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await msg.answer("Используй: <code>/ask твой вопрос</code>", parse_mode="HTML")
        return
    await _answer_chat_question(msg, parts[1].strip())


@router.message(Command("forget"))
async def on_forget(msg: Message) -> None:
    user_id = msg.from_user.id
    if chat.has_transcript(user_id):
        chat.clear(user_id)
        await msg.answer("🧹 Забыл последнее видео. Кидай новое.")
    else:
        await msg.answer("Мне и так нечего забывать — нового видео не было.")


@router.message(F.video | F.audio | F.voice | F.video_note | F.document)
async def on_media_file(msg: Message, bot: Bot) -> None:
    await _handle(msg, bot, source="file")


@router.message(F.text)
async def on_text(msg: Message, bot: Bot) -> None:
    text = (msg.text or "").strip()
    user_id = msg.from_user.id

    if is_url(text):
        await _handle(msg, bot, source="url")
        return

    # Не ссылка. Если есть сохранённый транскрипт — считаем это вопросом про видео.
    if chat.has_transcript(user_id):
        await _answer_chat_question(msg, text)
        return

    await msg.answer(
        "Не вижу ни файла, ни ссылки. Пришли видео или ссылку — разберу.\n\n"
        "📦 Файл больше 20 МБ? Загрузи на Я.Диск или Google Drive с публичной ссылкой "
        "и пришли мне ссылку — скачаю без ограничения по размеру."
    )


async def _answer_chat_question(msg: Message, question: str) -> None:
    user_id = msg.from_user.id
    if not chat.has_transcript(user_id):
        await msg.answer(
            "У меня нет сохранённого видео для тебя. Пришли сначала ролик или ссылку — потом обсудим."
        )
        return

    thinking = await msg.answer("🤔 Думаю…")
    try:
        answer = await chat.answer_question(user_id, question)
    except chat.ChatError as e:
        await thinking.edit_text(f"❌ {e}")
        return
    except Exception:
        logger.exception("Ошибка чата с транскриптом")
        await thinking.edit_text("❌ Что-то пошло не так. Попробуй ещё раз.")
        return

    # Telegram режет длинные сообщения — отправляем по частям.
    parts = _split_for_telegram(answer)
    if not parts:
        await thinking.edit_text("🤷 Пустой ответ. Перефразируй вопрос.")
        return
    await thinking.edit_text(parts[0])
    for part in parts[1:]:
        await msg.answer(part)


async def _handle(msg: Message, bot: Bot, source: str) -> None:
    user_id = msg.from_user.id

    if rate_limit.is_blacklisted(user_id):
        await msg.answer("🚫 Доступ к боту ограничен.")
        return

    if _processing_lock.locked():
        await msg.answer("⏳ Сейчас обрабатываю другое видео. Жди очереди — отвечу как освобожусь.")

    async with _processing_lock:
        progress = await msg.answer("🔄 Принял. Готовлю…")
        workdir = make_workdir()
        try:
            if source == "url":
                media = await _download_from_url_with_progress(msg, progress, workdir)
            else:
                media = await _download_from_telegram(msg, bot, progress, workdir)

            duration_min = media.duration_seconds / 60
            ok, reason = rate_limit.can_process(user_id, duration_min)
            if not ok:
                await progress.edit_text(reason)
                return

            await progress.edit_text(
                f"🎙 Транскрибирую ({duration_min:.1f} мин аудио)…"
            )
            chunks = await split_into_chunks(media.audio_path, media.duration_seconds, workdir)
            transcription = await transcribe_chunks(chunks)

            if not transcription.text.strip():
                await progress.edit_text("🤷 Не получилось разобрать речь — возможно, в видео нет голоса.")
                return

            rate_limit.record_usage(user_id, duration_min)

            await progress.edit_text("✍️ Делаю три уровня разбора…")
            transcript_text = transcription.text_with_timecodes or transcription.text
            summaries = await summarize_all_levels(transcript_text)

            await _send_results(msg, transcript_text, summaries, media)
            await progress.delete()

            # Сохраняем транскрипт для последующего чата с юзером.
            chat.set_transcript(user_id, transcript_text, media.title)
            await msg.answer(
                "💬 Теперь можешь обсудить это видео — просто напиши мне вопрос.\n"
                "Например: «что главное?», «как это применить?», «что автор имел в виду про X?», "
                "«с чем он не прав?»\n\n"
                "Команды: /ask <вопрос>, /forget — забыть видео."
            )

        except MediaError as e:
            await progress.edit_text(f"❌ {e}")
        except TranscribeError as e:
            await progress.edit_text(f"❌ Транскрипция: {e}")
        except SummarizeError as e:
            await progress.edit_text(f"❌ Пересказ: {e}")
        except Exception:
            logger.exception("Неожиданная ошибка в обработчике")
            await progress.edit_text("❌ Что-то пошло не так. Я записал ошибку, попробуй ещё раз.")
        finally:
            cleanup_workdir(workdir)


async def _download_from_url_with_progress(msg: Message, progress: Message, workdir: Path) -> MediaInfo:
    url = extract_url(msg.text or "")
    if not url:
        raise MediaError("Не нашёл ссылку в сообщении.")
    await progress.edit_text("⬇️ Скачиваю видео по ссылке…")
    return await download_from_url(url, workdir)


async def _download_from_telegram(msg: Message, bot: Bot, progress: Message, workdir: Path) -> MediaInfo:
    file_obj, filename = _pick_file_object(msg)
    if file_obj is None:
        raise MediaError("Это сообщение не похоже на видео или аудио.")

    file_size = getattr(file_obj, "file_size", None) or 0
    if file_size > TELEGRAM_FILE_LIMIT_BYTES:
        raise MediaError(
            "Файл больше 20 МБ — Telegram не отдаёт такие файлы ботам.\n\n"
            "💡 Загрузи видео в облако с публичной ссылкой и пришли её мне:\n"
            "• Яндекс.Диск — кнопка «Поделиться»\n"
            "• Google Drive — доступ «Все, у кого есть ссылка»\n"
            "• YouTube — видимость «По ссылке» или публичное\n"
            "• VK / Rutube / TikTok / Reels — любая публичная ссылка\n\n"
            "По ссылке скачаю без ограничения по размеру."
        )

    await progress.edit_text("⬇️ Скачиваю файл из Telegram…")
    src_path = workdir / (filename or "input.bin")
    tg_file = await bot.get_file(file_obj.file_id)
    await bot.download_file(tg_file.file_path, destination=src_path)

    await progress.edit_text("🎧 Извлекаю аудио…")
    return await convert_to_audio(src_path, workdir)


def _pick_file_object(msg: Message) -> tuple[object | None, str | None]:
    """Возвращает (file_object, suggested_filename) для любого медиа-сообщения."""
    if msg.video:
        return msg.video, f"video_{msg.video.file_unique_id}.mp4"
    if msg.audio:
        return msg.audio, msg.audio.file_name or f"audio_{msg.audio.file_unique_id}.mp3"
    if msg.voice:
        return msg.voice, f"voice_{msg.voice.file_unique_id}.ogg"
    if msg.video_note:
        return msg.video_note, f"vnote_{msg.video_note.file_unique_id}.mp4"
    if msg.document:
        # Документ может быть видео/аудио, прикрепленным как файл.
        mime = (msg.document.mime_type or "").lower()
        if mime.startswith(("video/", "audio/")):
            return msg.document, msg.document.file_name or "document.bin"
        return None, None
    return None, None


async def _send_results(msg: Message, full_transcript: str, summaries: Summaries, media: MediaInfo) -> None:
    title = media.title or "транскрипция"

    # Три уровня — каждый отдельным сообщением (или несколькими, если длинный).
    for body in (summaries.light, summaries.medium, summaries.full):
        for chunk in _split_for_telegram(body):
            await msg.answer(chunk)

    # Полная транскрипция файлом — чтобы не засорять чат.
    transcript_bytes = full_transcript.encode("utf-8")
    safe_name = _safe_filename(title) + ".txt"
    await msg.answer_document(
        BufferedInputFile(transcript_bytes, filename=safe_name),
        caption="📄 Полная транскрипция (с таймкодами)",
    )


def _split_for_telegram(text: str, limit: int = 4000) -> list[str]:
    """Режет длинный текст на части по limit символов, по границам строк."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    remaining = text
    while len(remaining) > limit:
        cut = remaining.rfind("\n", 0, limit)
        if cut <= 0:
            cut = remaining.rfind(" ", 0, limit)
        if cut <= 0:
            cut = limit
        parts.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip()
    if remaining:
        parts.append(remaining)
    return parts


def _safe_filename(name: str) -> str:
    keep = []
    for ch in name[:60]:
        if ch.isalnum() or ch in (" ", "-", "_"):
            keep.append(ch)
        else:
            keep.append("_")
    cleaned = "".join(keep).strip().replace(" ", "_")
    return cleaned or "transcript"
