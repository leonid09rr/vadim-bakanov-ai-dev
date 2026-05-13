"""Чат с транскриптом: после обработки видео юзер может задавать вопросы.

Бот ведёт себя как собеседник, который посмотрел видео вместе с пользователем:
объясняет, что имел в виду автор, делает выводы, предлагает решения, спорит.

Состояние хранится в памяти — последний транскрипт на пользователя + история
последних реплик. При рестарте бота теряется. Это сознательное решение для MVP:
лимит и так "одно видео в памяти", а БД сейчас избыточна.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field

from groq import AsyncGroq, GroqError

logger = logging.getLogger(__name__)


# Лимит контекста Llama 3.3 70B — 128k токенов. Транскрипт + история + промпт.
# 1 русский токен ≈ 2 символа, оставляем запас под ответ.
MAX_TRANSCRIPT_CHARS = 180_000

# Сколько пар (вопрос+ответ) держим в истории чата. Старое выкидываем.
MAX_HISTORY_PAIRS = 10


SYSTEM_PROMPT = """Ты — умный собеседник, который посмотрел видео вместе с пользователем и теперь обсуждает его.

Как ты разговариваешь:
- Думай и предлагай, а не пересказывай. Не цитируй слепо — объясняй смысл, делай выводы, связывай идеи.
- Если пользователь спрашивает "как сделать X" или "что лучше" — давай конкретные шаги, опираясь на видео и здравый смысл. Предлагай варианты "проще / быстрее / надёжнее".
- Если автор сказал что-то неочевидное, туманное или спорное — расшифруй, что он имел в виду, и при чём это к жизни пользователя.
- Если автор противоречит себе или говорит ерунду — отметь это спокойно, без агрессии. Не защищай автора, если он не прав.
- Если в видео нет прямого ответа на вопрос — скажи прямо ("в видео этого нет"), потом предложи свой вариант "в духе того, о чём говорил автор" или из общего знания.
- Не выдумывай факты из видео. Если не уверен — скажи "не помню точно" или "это уже моё мнение, не из видео".
- Не извиняйся за каждое слово. Не пиши "как ИИ я не могу". Не лей воду.
- Стиль: ясный, живой, прямой, на русском. Без канцеляризмов и эмодзи в начале каждого предложения.
- Если можешь — отвечай 3-7 предложениями. Длинно только если вопрос правда требует.

Содержание видео{title_part} (это транскрипция речи, возможно с таймкодами [MM:SS]):

{transcript}"""


@dataclass
class ChatState:
    transcript: str
    title: str | None = None
    history: list[dict] = field(default_factory=list)  # [{"role": "user"|"assistant", "content": ...}]
    updated_at: float = field(default_factory=time.time)


_user_chats: dict[int, ChatState] = {}


def set_transcript(user_id: int, transcript: str, title: str | None) -> None:
    """Сохраняет транскрипт после успешной обработки видео. Сбрасывает историю чата."""
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        logger.warning(
            "Транскрипт для чата %d символов > лимита %d, обрезаю",
            len(transcript), MAX_TRANSCRIPT_CHARS,
        )
        transcript = transcript[:MAX_TRANSCRIPT_CHARS] + "\n\n[…транскрипт обрезан, дальше не вижу…]"
    _user_chats[user_id] = ChatState(transcript=transcript, title=title)


def clear(user_id: int) -> None:
    _user_chats.pop(user_id, None)


def has_transcript(user_id: int) -> bool:
    return user_id in _user_chats


class ChatError(Exception):
    """Ошибки Groq при ответе на вопрос — показываем юзеру."""


def _get_client() -> AsyncGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ChatError("GROQ_API_KEY не задан")
    return AsyncGroq(api_key=api_key)


def _get_model() -> str:
    return os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")


async def answer_question(user_id: int, question: str) -> str:
    """Отвечает на вопрос юзера, помня транскрипт и предыдущие реплики чата."""
    state = _user_chats.get(user_id)
    if state is None:
        raise ChatError("Нет сохранённого видео — пришли сначала ролик или ссылку.")

    title_part = f' "{state.title}"' if state.title else ""
    system = SYSTEM_PROMPT.format(title_part=title_part, transcript=state.transcript)

    messages: list[dict] = [{"role": "system", "content": system}]
    messages.extend(state.history)
    messages.append({"role": "user", "content": question})

    client = _get_client()
    model = _get_model()

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
            max_tokens=1500,
        )
    except GroqError as e:
        msg = str(e)
        if "rate_limit" in msg.lower() or "429" in msg:
            raise ChatError("Groq rate limit. Подожди минуту и спроси ещё раз.") from e
        raise ChatError(f"Groq Llama API: {msg}") from e

    answer = (response.choices[0].message.content or "").strip() if response.choices else ""
    if not answer:
        raise ChatError("Llama вернула пустой ответ. Перефразируй вопрос.")

    state.history.append({"role": "user", "content": question})
    state.history.append({"role": "assistant", "content": answer})
    _trim_history(state)
    state.updated_at = time.time()

    return answer


def _trim_history(state: ChatState) -> None:
    """Держим максимум MAX_HISTORY_PAIRS пар. Старые выкидываем парами (user+assistant)."""
    max_messages = MAX_HISTORY_PAIRS * 2
    if len(state.history) > max_messages:
        excess = len(state.history) - max_messages
        # Удаляем парами, чтобы не сбить чередование ролей.
        if excess % 2 == 1:
            excess += 1
        state.history = state.history[excess:]
