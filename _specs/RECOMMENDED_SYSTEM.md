# Рекомендуемая система Claude Code для новых проектов

> Готовый blueprint для настройки Claude Code в новых проектах
> Версия: 1.0 | Дата: 2026-02-15

---

## Оглавление

1. [Обзор системы](#1-обзор-системы)
2. [Файловая структура](#2-файловая-структура)
3. [CLAUDE.md — шаблон](#3-claudemd--шаблон)
4. [Settings и Hooks](#4-settings-и-hooks)
5. [Rules — автоправила](#5-rules--автоправила)
6. [Data — хранилище](#6-data--хранилище)
7. [Skills — скиллы](#7-skills--скиллы)
8. [Agents — субагенты](#8-agents--субагенты)
9. [Проектная инфраструктура](#9-проектная-инфраструктура)
10. [Как кастомизировать под тип проекта](#10-как-кастомизировать-под-тип-проекта)
11. [Чеклист запуска нового проекта](#11-чеклист-запуска-нового-проекта)

---

## 1. Обзор системы

### Три слоя

```
┌─────────────────────────────────────────────────────┐
│  CLAUDE.md                                          │
│  Главный файл: проект, стек, правила, workflow      │
│  Всегда в контексте. Источник истины.               │
├─────────────────────────────────────────────────────┤
│  .claude/                                           │
│  ├── settings.json    — permissions, hooks           │
│  ├── rules/           — автоправила (триггерятся)    │
│  ├── data/            — персистентные данные          │
│  ├── skills/          — /команды (загружаются)       │
│  └── agents/          — субагенты (делегирование)    │
├─────────────────────────────────────────────────────┤
│  Проектная инфраструктура                           │
│  ├── _status/         — состояние окружений          │
│  ├── _changelogs/     — история релизов              │
│  ├── documentation/   — живая документация           │
│  ├── backlog/         — задачи                       │
│  └── _specs/          — спецификации                 │
└─────────────────────────────────────────────────────┘
```

### Принципы

1. **CLAUDE.md — Single Source of Truth** для Claude. Всё критичное — здесь
2. **Progressive Disclosure** — metadata всегда видна, body загружается по триггеру, references — по необходимости
3. **Error Learning** — система обучается на ошибках и записывает их
4. **Information Architecture** — [CANONICAL], [REF:], никаких дубликатов
5. **Safety First** — подтверждение для деструктивных операций, checklist для PROD

---

## 2. Файловая структура

```
PROJECT_NAME/
│
├── CLAUDE.md                              # Главный файл инструкций
├── VERSION                                # Версия проекта (semver)
├── .gitignore
│
├── .claude/
│   ├── settings.json                      # Permissions + hooks → в git
│   ├── settings.local.json                # Локальные настройки → НЕ в git
│   │
│   ├── rules/                             # Автоправила (загружаются автоматически)
│   │   ├── error-learning.md              #   Обучение на ошибках
│   │   └── auto-backup.md                 #   Напоминание о бэкапе
│   │
│   ├── data/                              # Персистентные данные правил
│   │   └── error-log.md                   #   Лог ошибок (newest first)
│   │
│   ├── agents/                            # Субагенты
│   │   ├── deployer.md                    #   Деплой DEV/PROD
│   │   ├── docs-generator.md             #   Генерация документации
│   │   └── test-runner.md                 #   Запуск тестов
│   │
│   └── skills/                            # Скиллы (/команды)
│       ├── README.md                      #   Каталог всех скиллов
│       ├── commit/SKILL.md                #   /commit
│       ├── push/SKILL.md                  #   /push
│       ├── cherry-pick/SKILL.md           #   /cherry-pick
│       ├── merge-to-prod/SKILL.md         #   /merge-to-prod
│       ├── deploy-dev/SKILL.md            #   /deploy-dev
│       ├── deploy-prod/SKILL.md           #   /deploy-prod
│       ├── git-status/SKILL.md            #   /git-status
│       ├── test/SKILL.md                  #   /test
│       ├── docs/SKILL.md                  #   /docs
│       ├── techdebt/SKILL.md              #   /techdebt
│       ├── architect/SKILL.md             #   /architect
│       └── project-manager/               #   /project-manager
│           ├── SKILL.md
│           └── references/role.md
│
├── _status/                               # Состояние окружений
│   ├── DEV.md
│   ├── PROD.md
│   ├── PENDING_RELEASE.md                 # Diff DEV → PROD
│   └── DEVELOPMENT_STATUS.md              # "Где я остановился"
│
├── _changelogs/                           # История изменений
│   ├── dev.md
│   └── prod.md
│
├── documentation/                         # Живая документация
│   ├── README.md
│   ├── ARCHITECTURE.md
│   └── ERROR_REGISTRY.md
│
├── backlog/                               # Задачи
│   └── README.md
│
├── _specs/                                # Спецификации
│   └── README.md
│
└── src/                                   # Исходный код
    └── ...
```

---

## 3. CLAUDE.md — шаблон

> Ниже — полный шаблон. Секции помечены `<!-- ОБЯЗАТЕЛЬНО -->` или `<!-- ОПЦИОНАЛЬНО -->`.
> Замени `{PLACEHOLDERS}` на реальные значения.

```markdown
# CLAUDE.md — {Название проекта}

Last Updated: {YYYY-MM-DD}

<!-- ОБЯЗАТЕЛЬНО -->
## Язык
Используй язык ответов, такой же, как пользователь использовал для вопросов.
Если пользователь пишет на русском — отвечай на русском, если на английском — на английском.

<!-- ОБЯЗАТЕЛЬНО -->
## Response Format

Формат ответов для всех задач:
1. **Понятность задачи:** <0–100%> — если <70%, сначала задать уточняющие вопросы
2. **Уверенность в ответе:** <0–100%>
3. **Роль:** <экспертная роль, релевантная запросу>
4. **TL;DR** — краткий ответ
5. **Полный ответ**

### Self-Reflection
Перед ответом внутренне оцени: Accuracy, Honesty, Objectivity, Clarity, Brevity, Practical Value.
Итерируй пока оценка не будет ≥98/100.

<!-- ОБЯЗАТЕЛЬНО -->
## Проект
{Одно-два предложения: что за проект, для кого, зачем}

<!-- ОБЯЗАТЕЛЬНО -->
## Стек

| Компонент | Технология |
|-----------|------------|
| Язык | {Python 3.11+ / TypeScript / ...} |
| Фреймворк | {aiogram 3.x / Astro / Next.js / ...} |
| БД | {Supabase / PostgreSQL / SQLite / ...} |
| Кэш | {Redis / ...} |
| Хостинг | {VPS / Vercel / ...} |
| CI/CD | {Docker / GitHub Actions / ...} |

<!-- ОБЯЗАТЕЛЬНО -->
## Архитектура

```
{Handlers/Pages} → {Services/API} → {Repositories/Models}
```

<!-- ОПЦИОНАЛЬНО -->
## Структура проекта

```
{project}/
├── src/
│   ├── ...
├── tests/
├── scripts/
├── ...
```

<!-- ОБЯЗАТЕЛЬНО для проектов с DEV/PROD -->
## Окружения

| Env | URL/Bot | БД | Ветка |
|-----|---------|-----|-------|
| DEV | {dev URL} | {dev DB} | dev |
| PROD | {prod URL} | {prod DB} | prod |

<!-- ОБЯЗАТЕЛЬНО -->
## КРИТИЧЕСКИЕ ПРАВИЛА

### Рабочая ветка — `local`
Ветка `local` — основная рабочая ветка.
После ЛЮБОЙ операции (deploy, push, merge) — ВСЕГДА возвращайся на `local`.

### Деплой на PROD
1. НИКОГДА напрямую на PROD — сначала DEV
2. Требуется ЯВНОЕ подтверждение пользователя
3. Workflow: local → DEV → тест → PROD

### После КАЖДОГО деплоя
1. Протестируй что деплой работает
2. Обнови документацию (запусти /docs)
3. Обнови VERSION при значимых изменениях
4. Обнови changelog

### Security
- `.env.*` — НЕ коммитить (в .gitignore)
- Секреты только из env, не хардкод
- Функции с `# SECURITY-SENSITIVE` требуют повышенного внимания
- Не логировать значения секретов

<!-- ОБЯЗАТЕЛЬНО -->
## Git Workflow

```
local (разработка) → cherry-pick → dev (тестирование) → merge → prod (production)
```

| Ветка | Назначение | Что коммитить |
|-------|------------|---------------|
| local | Рабочая ветка | Всё: код, specs, планы |
| dev | Тестирование | Только рабочий код |
| prod | Production | Только протестированный код |

### Git-правила для Claude
- НЕ делать commit/push/merge без подтверждения пользователя
- НЕ делать force push, reset --hard, rebase без явного запроса
- Conventional commits: `<type>(<scope>): <description>`
- Всегда `Co-Authored-By: Claude <model> <noreply@anthropic.com>`

<!-- ОБЯЗАТЕЛЬНО -->
## Быстрые команды

```bash
# Локальный запуск
{команда запуска}

# Тесты
{команда тестов}

# Деплой
{команда деплоя DEV}
{команда деплоя PROD}
```

<!-- ОБЯЗАТЕЛЬНО -->
## Скиллы (Claude Code)

| Скилл | Описание |
|-------|----------|
| /commit | AI-генерация commit message |
| /deploy-dev | Деплой на DEV |
| /deploy-prod | Деплой на PROD |
| /git-status | Статус всех веток |
| /test | Тестирование кода |
| /docs | Обновление документации |
| /techdebt | Поиск технического долга |
| /architect | Архитектурный анализ |
| /project-manager | Управление задачами |

<!-- ОБЯЗАТЕЛЬНО -->
## Принципы разработки

- **KISS** — простота важнее сложности
- **YAGNI** — не пиши код "на будущее"
- **Plan then Act** — сначала планируй, потом реализуй
- **SRP** — одна ответственность на функцию
- **Three-Layer Rule** — Handlers → Services → Models

### Чеклист перед добавлением сложности
1. Нужна ли эта фича прямо сейчас?
2. Есть ли реальная проблема, которую решает эта сложность?
3. Можно ли решить проблему проще?
4. Добавляет ли это новую зависимость?

### Красные флаги
- Более 3 слоёв абстракции
- Фабрики, создающие фабрики
- Сложная конфигурация вместо env-переменных

<!-- ОПЦИОНАЛЬНО -->
## Информационная архитектура

- `[CANONICAL]` — единственный авторитетный источник
- `[REF: path#section]` — ссылка (вместо дубликата)
- `[CONFIRMED: source]` — проверенная информация
- В каждой папке — `README.md` с описанием содержимого
- Дата обновления в документах: `Last Updated: YYYY-MM-DD`

<!-- ОПЦИОНАЛЬНО -->
## Context7 MCP
При работе с библиотеками/API используй `use context7` для актуальной документации.

<!-- ОПЦИОНАЛЬНО -->
## Документация
- [documentation/](documentation/) — архитектура, деплой, ошибки
- [_specs/](_specs/) — спецификации
- [_changelogs/](_changelogs/) — история релизов
- [_status/](_status/) — текущее состояние окружений
```

---

## 4. Settings и Hooks

### `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:docs.anthropic.com)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path\"); if [[ \"$FILE\" == *.py ]]; then ruff check --fix \"$FILE\" 2>&1; fi'"
          }
        ]
      }
    ]
  }
}
```

**Что это делает:**
- Разрешает WebFetch на docs.anthropic.com без подтверждения
- После каждого Write в `.py` файл автоматически запускает `ruff check --fix`

**Варианты hooks для других стеков:**

TypeScript/JavaScript:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path\"); if [[ \"$FILE\" == *.ts || \"$FILE\" == *.tsx ]]; then npx eslint --fix \"$FILE\" 2>&1; fi'"
          }
        ]
      }
    ]
  }
}
```

Astro/Web:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path\"); if [[ \"$FILE\" == *.astro || \"$FILE\" == *.ts || \"$FILE\" == *.tsx ]]; then npx prettier --write \"$FILE\" 2>&1; fi'"
          }
        ]
      }
    ]
  }
}
```

### `.claude/settings.local.json`

Не попадает в git. Для локальных override:
```json
{
  "permissions": {
    "allow": [
      "Bash(git checkout:*)"
    ]
  }
}
```

---

## 5. Rules — автоправила

### `.claude/rules/error-learning.md`

```markdown
---
description: "Record errors after bugfix, failed deploy, or 2+ failed attempts to prevent recurrence"
---

# Error Learning

After a bugfix, failed deploy, or 2+ failed attempts at a task:

1. **Record** in `.claude/data/error-log.md`:
   - Symptom (what happened)
   - Root Cause (why — dig past the surface)
   - Fix (what was done)
   - Prevention (what to update so this doesn't repeat)
   - Files (affected)

2. **Update instructions** if the error reveals a gap:
   - CLAUDE.md — if it's a project-wide pattern
   - Memory (MEMORY.md) — if it's a cross-session insight
   - Skip if the error is one-off and unlikely to repeat

3. **Rule of Three**: update instructions immediately on first occurrence
   only if the fix is obvious. Otherwise wait for 3 occurrences of the
   same class of error before codifying a rule.
```

### `.claude/rules/auto-backup.md`

```markdown
---
description: "Suggest backup after significant work: 3+ files changed, task completed, documentation updated, config modified"
---

# Auto-Backup

После завершения значимой работы — предложи пользователю сделать бэкап.

## Что считается значимой работой
- Завершение задачи (создание/редактирование файлов)
- Работа с данными (обновление бэклога, отчётов)
- Создание документации
- Изменение конфигурации (скиллы, правила)
- 3+ файлов изменено за сессию

## Что НЕ является значимой работой
- Только чтение и анализ
- Ответы на вопросы без редактирования
- Незавершённая работа (пользователь явно продолжает)

## Формат
После завершения значимой работы добавь:

---
Сделать бэкап в GitHub? Скажи "да" — закоммичу и запушу.

## Важно
- НЕ делай бэкап автоматически — только предлагай
- Пользователь сам решает когда пушить
```

---

## 6. Data — хранилище

### `.claude/data/error-log.md`

```markdown
# Error Log

Structured log of errors and their root causes.
Used by error-learning rule to prevent recurring mistakes.
Format: newest first.

<!--
## YYYY-MM-DD — Short description
- **Symptom**: what happened
- **Root Cause**: why it happened (dig deep)
- **Fix**: what was done
- **Prevention**: what to update in CLAUDE.md / memory / rules
- **Files**: affected files
-->
```

---

## 7. Skills — скиллы

### `.claude/skills/README.md`

```markdown
# .claude/skills/

Claude Code skills для автоматизации разработки и управления проектом.

## Git & CI/CD

| Skill | Команда | Описание |
|-------|---------|----------|
| [commit](commit/SKILL.md) | `/commit` | AI-генерация commit message |
| [push](push/SKILL.md) | `/push` | Безопасный push с подтверждением |
| [cherry-pick](cherry-pick/SKILL.md) | `/cherry-pick` | Перенос коммитов local → dev |
| [merge-to-prod](merge-to-prod/SKILL.md) | `/merge-to-prod` | Merge dev → prod |
| [deploy-dev](deploy-dev/SKILL.md) | `/deploy-dev` | Деплой на DEV |
| [deploy-prod](deploy-prod/SKILL.md) | `/deploy-prod` | Деплой на PROD |
| [git-status](git-status/SKILL.md) | `/git-status` | Статус всех веток |

## Quality & Testing

| Skill | Команда | Описание |
|-------|---------|----------|
| [test](test/SKILL.md) | `/test` | Тестирование кода |
| [techdebt](techdebt/SKILL.md) | `/techdebt` | Поиск технического долга |

## Documentation & Planning

| Skill | Команда | Описание |
|-------|---------|----------|
| [docs](docs/SKILL.md) | `/docs` | Обновление документации после деплоя |
| [architect](architect/SKILL.md) | `/architect` | Архитектурный анализ |
| [project-manager](project-manager/SKILL.md) | `/project-manager` | Управление задачами |

## Git Workflow

```
local (разработка)
  │
  └─> /cherry-pick → dev (тестирование)
                       │
                       └─> /merge-to-prod → prod (production)
```
```

---

### `/commit`

```markdown
---
name: commit
description: AI-генерация commit message из git diff в conventional commit формате. Используй при коммите, создании коммита, git commit, сохранении изменений, закоммитить.
---

# /commit — AI-Generated Commit

## Instructions

### 1. Проверь изменения
```bash
git status
git diff --stat
```

Если нет изменений: "Нет изменений для коммита."

### 2. Проанализируй diff
Прочитай diff и определи:
- Какие файлы изменены и зачем
- Тип изменения (feat/fix/docs/refactor/test/chore/perf)
- Scope (область: handlers, services, config, deps, ...)

### 3. Сгенерируй commit message

Формат:
```
<type>(<scope>): <subject>

<optional body — bullet points>

Co-Authored-By: Claude <model> <noreply@anthropic.com>
```

### 4. Покажи preview и спроси подтверждение

```
Изменённые файлы:
  M src/services/auth.py (+25, -3)
  A src/models/token.py

Предлагаемый коммит:
  feat(auth): add JWT token generation

  - Implement token creation with expiry
  - Add Token pydantic model

  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

Создать коммит? [y/N]
```

### 5. Создай коммит (при подтверждении)
```bash
git add <specific-files>
git commit -m "$(cat <<'EOF'
<message>
EOF
)"
```

**Правила:**
- НИКОГДА `git add -A` или `git add .`
- Добавляй файлы по отдельности
- Не коммить .env, credentials

### 6. Результат
```
Committed abc1234: feat(auth): add JWT token generation

Next: /cherry-pick → dev | /git-status
```
```

---

### `/push`

```markdown
---
name: push
description: Безопасный push на remote с показом что будет отправлено и подтверждением. Используй при push, пуш, отправить, запушить.
---

# /push — Safe Push

## Instructions

### 1. Покажи что будет запушено
```bash
git log origin/$(git branch --show-current)..HEAD --oneline
```

### 2. Спроси подтверждение
```
Push to origin/{branch}:
- {N} commits
- Files: {list}

Confirm? [y/N]
```

### 3. Push (при подтверждении)
```bash
git push origin $(git branch --show-current)
```

### 4. Результат
```
Pushed to origin/{branch}: {N} commits
```
```

---

### `/cherry-pick`

```markdown
---
name: cherry-pick
description: Перенос последнего коммита из local в dev. Используй при cherry-pick, перенести в dev, передать в dev.
---

# /cherry-pick — Transfer to Dev

## Instructions

### 1. Проверь текущую ветку
Должна быть `local`. Если нет — сообщи.

### 2. Запомни коммит
```bash
COMMIT=$(git log -1 --format="%H")
MSG=$(git log -1 --format="%s")
```

### 3. Перенеси
```bash
git checkout dev
git cherry-pick $COMMIT
```

### 4. Вернись на local
```bash
git checkout local
```

### 5. Результат
```
Cherry-picked {hash}: {message} → dev

Next: /push (push dev) | /deploy-dev
```
```

---

### `/merge-to-prod`

```markdown
---
name: merge-to-prod
description: Merge ветки dev в prod для релиза. ТРЕБУЕТ подтверждения. Используй при merge-to-prod, релиз, выкатить на прод, merge в prod.
---

# /merge-to-prod — Release to Production

## Instructions

### 1. Покажи что будет смержено
```bash
git log dev..prod --oneline  # что уже в prod
git log prod..dev --oneline  # что будет добавлено
```

### 2. ОБЯЗАТЕЛЬНО спроси подтверждение

```
PRODUCTION MERGE

Коммиты из dev → prod:
{список коммитов}

Код протестирован на DEV? Подтвердите merge в prod.
```

### 3. Merge (при подтверждении)
```bash
git checkout prod
git merge dev --no-edit
```

### 4. Вернись на local
```bash
git checkout local
```

### 5. Результат
```
Merged dev → prod

Next: /push (push prod) | /deploy-prod
```
```

---

### `/deploy-dev`

```markdown
---
name: deploy-dev
description: Деплой на DEV окружение. Используй при deploy dev, деплой на дев, развернуть dev, выкатить на дев.
---

# /deploy-dev — Deploy to DEV

## Instructions

### 1. Проверь ветку
```bash
git rev-parse --abbrev-ref HEAD  # Должна быть dev
```
Если не dev: "Переключись на dev: git checkout dev"

### 2. Проверь синхронизацию
```bash
git fetch origin dev
git status
```

### 3. Деплой
```bash
{./scripts/deploy.sh dev}
```

### 4. Проверь логи
```bash
{ssh server 'docker logs app-dev --tail 20'}
```

### 5. Вернись на local
```bash
git checkout local
```

### 6. Результат
```
Deployed to DEV

Next:
  1. Тест на {DEV URL/bot}
  2. Если баги → fix в local → repeat
  3. /test для валидации
  4. Если ОК → /merge-to-prod
```
```

---

### `/deploy-prod`

```markdown
---
name: deploy-prod
description: Деплой на PROD окружение. ТРЕБУЕТ подтверждения и тестирования на DEV. Используй при deploy prod, деплой на прод, выкатить на production.
---

# /deploy-prod — Deploy to PROD

## Instructions

### 1. Safety Checklist
```
PRODUCTION DEPLOYMENT CHECKLIST:

[ ] Код протестирован на DEV?
[ ] Все тесты проходят?
[ ] Критических багов нет?
[ ] Подтверждаете деплой на PROD?
```

ВСЕ пункты должны быть подтверждены.

### 2. Проверь ветку
```bash
git rev-parse --abbrev-ref HEAD  # Должна быть prod
```

### 3. Деплой
```bash
{./scripts/deploy.sh prod}
```

### 4. Проверь логи
```bash
{ssh server 'docker logs app-prod --tail 20'}
```

### 5. Post-deploy
1. Протестируй
2. Запусти /docs для обновления документации
3. Обнови VERSION (semver)
4. Обнови _changelogs/prod.md

### 6. Вернись на local
```bash
git checkout local
```

### 7. Результат
```
Deployed to PROD

Next:
  1. Monitor {PROD URL/bot}
  2. Check logs
  3. /docs — обновить документацию
```
```

---

### `/git-status`

```markdown
---
name: git-status
description: Статус всех веток git workflow. Используй при git-status, статус, состояние веток, что в работе.
---

# /git-status — Multi-Branch Status

## Instructions

### 1. Собери информацию
```bash
git branch -vv
git status --short
git log --oneline -5
git log origin/dev..dev --oneline 2>/dev/null
git log origin/prod..prod --oneline 2>/dev/null
git log prod..dev --oneline 2>/dev/null
```

### 2. Покажи отчёт

```
## Git Status

Current branch: {branch}

### Uncommitted changes
{git status}

### Recent commits (local)
{last 5 commits}

### Unpushed to remote
- dev: {N} commits
- prod: {N} commits

### Pending release (dev → prod)
{commits in dev but not in prod}
```
```

---

### `/test`

```markdown
---
name: test
description: Тестирование кода. Используй при тестировании, проверке, test, lint, smoke test, проверке качества.
---

# /test — Testing & Validation

## Instructions

Запускай все тесты по порядку. Если один падает — продолжай остальные.

### 1. Lint
```bash
{ruff check src/ | npx eslint src/}
```

### 2. Type Check
```bash
{mypy src/ | npx tsc --noEmit}
```

### 3. Unit Tests
```bash
{pytest tests/ -v | npm test}
```

### 4. Build Check
```bash
{python -m py_compile src/main.py | npm run build}
```

### 5. Отчёт

```
## Test Report

| Test | Status | Notes |
|------|--------|-------|
| Lint | PASS/FAIL | ... |
| Types | PASS/FAIL | ... |
| Unit | PASS/FAIL | ... |
| Build | PASS/FAIL | ... |

### Issues Found
{список или "None"}

### Recommendation
{Ready for deploy / Needs fixes}
```

**Правило:** НЕ исправляй ошибки — только отчёт.
```

---

### `/docs`

```markdown
---
name: docs
description: Обновление документации после деплоя. Используй при docs, обновить документацию, после деплоя, update docs.
---

# /docs — Documentation Update

## Instructions

### 1. Собери информацию
```bash
cat VERSION
git log --oneline -10
date "+%Y-%m-%d %H:%M"
```

### 2. Обнови _status/{ENV}.md
- Версия, коммит, дата деплоя
- Доступные фичи/команды
- Технические детали

### 3. Обнови _status/PENDING_RELEASE.md
```bash
git log prod..dev --oneline
git diff prod..dev --name-only
```

### 4. Обнови _status/DEVELOPMENT_STATUS.md
- Что в работе
- Последние изменения
- Известные баги
- Запланировано

### 5. Обнови documentation/ERROR_REGISTRY.md (если был багфикс)

### 6. Отчёт
```
## Documentation Updated

| File | Changes |
|------|---------|
| _status/{ENV}.md | Updated version, features |
| PENDING_RELEASE.md | Updated diff |
| ... | ... |
```
```

---

### `/techdebt`

```markdown
---
name: techdebt
description: Поиск технического долга и проблем качества кода. Используй при techdebt, технический долг, cleanup, TODO, рефакторинг, качество кода.
---

# /techdebt — Technical Debt Scanner

## Instructions

### 1. Сканирование

Выполни ВСЕ проверки:

```bash
# TODO/FIXME/HACK
grep -rn "TODO\|FIXME\|HACK\|XXX" src/ --include="*.py" --include="*.ts" --include="*.tsx" --include="*.astro"

# Большие файлы (>300 строк)
find src/ -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.astro" | xargs wc -l | awk '$1 > 300'

# Устаревшие зависимости
{pip list --outdated | npm outdated}
```

### 2. Дополнительный анализ
- Дублирование кода
- Функции >50 строк
- Мёртвый код
- Нарушения архитектуры (прямые импорты между слоями)

### 3. Отчёт по приоритетам

```
## Tech Debt Summary

| Категория | Найдено | Критичность |
|-----------|---------|-------------|
| TODO/FIXME | N | Low |
| Большие файлы | N | Medium |
| Устаревшие deps | N | Low |

**Топ-3 приоритета:**
1. ...
2. ...
3. ...
```

**Правило:** НЕ исправляй — только отчёт и рекомендации.

### Режимы
- `/techdebt` — быстрый обзор
- `/techdebt full` — детальный отчёт в `_status/TECHDEBT.md`
```

---

### `/architect`

```markdown
---
name: architect
description: Архитектурный анализ и планирование реализации фич. Используй при планировании, архитектуре, дизайне, новой фиче, как реализовать.
---

# /architect — Architecture & Planning

## Instructions

### 1. Пойми задачу
Уточни: что реализовать, ограничения, примеры.

### 2. Изучи текущую архитектуру
Прочитай ключевые файлы проекта.

### 3. Предложи решение

```
## Архитектура: {название фичи}

### Обзор
{краткое описание}

### Компоненты
1. **Handler/Page** — ...
2. **Service** — ...
3. **Repository/Model** — ...

### Модели данных
{Pydantic/TypeScript models}

### План реализации
1. [ ] Создать модели
2. [ ] Реализовать сервис
3. [ ] Добавить handler
4. [ ] Протестировать
```

### 4. Принципы
- KISS — простота
- YAGNI — не на будущее
- SRP — одна ответственность
```

---

### `/project-manager`

```markdown
---
name: project-manager
description: Управление бэклогом, планирование спринтов, статус-отчёты, приоритизация задач, декомпозиция.
argument-hint: [команда: статус | спринт | приоритизация | декомпозиция]
---

# /project-manager — Project Management

## Перед началом
Загрузи контекст роли: [references/role.md](references/role.md)

## Бэклог
**Файл:** `backlog/` — Single Source of Truth

## Компетенции
1. **Приоритизация** — ICE scoring, Eisenhower matrix, value vs effort
2. **Спринт-планирование** — отбор задач на период по capacity
3. **Статус-отчёт** — что сделано, что в работе, блокеры
4. **Декомпозиция** — крупная задача → конкретные шаги + критерии приёмки

## Команды
- `/project-manager статус` — статус всех проектов
- `/project-manager спринт` — сформировать спринт
- `/project-manager приоритизация` — ревью приоритетов
- `/project-manager декомпозиция {задача}` — разбить на шаги
```

### `project-manager/references/role.md`

```markdown
# Роль: Project Manager

## Кто ты
Опытный PM с 7+ лет опытом. Agile/Scrum/Kanban на практике.

## Методология
1. **Уточняй цель** — зачем, кто заказчик, какой результат
2. **Декомпозируй** — конкретные шаги + критерии приёмки
3. **Приоритизируй** — срочность, важность, зависимости
4. **Планируй** — спринты с учётом capacity
5. **Трекай** — прогресс, блокеры, эскалация

## Принципы
- Бэклог — Single Source of Truth
- Каждая задача — глагол + объект + результат
- Приоритеты абсолютные, без "всё важное"
- Блокеры эскалировать немедленно
```

---

## 8. Agents — субагенты

### `.claude/agents/deployer.md`

```markdown
---
name: deployer
description: Деплой на DEV или PROD окружение с safety checks и автообновлением документации. Используй при deploy, деплой, выкатить, развернуть.
tools: Bash, Read, Grep, Edit, Write
model: opus
---

# Deployer Agent

## Workflow

1. **Определи окружение** — спроси если не указано (dev/prod)
2. **Проверь ветку** — dev для DEV, prod для PROD
3. **Проверь синхронизацию** — git fetch + status
4. **[PROD only] Safety Checklist** — 4 пункта, все подтверждены
5. **Деплой** — запусти deploy script
6. **Проверь логи** — tail последних 20 строк
7. **Обнови документацию** — _status/{ENV}.md
8. **Вернись на local** — git checkout local
9. **Результат** — сообщи + next steps

## Critical Rules
- НИКОГДА deploy на PROD без подтверждения
- НИКОГДА пропускай checklist для PROD
- ВСЕГДА проверяй ветку перед деплоем
- ВСЕГДА возвращайся на local
```

### `.claude/agents/docs-generator.md`

```markdown
---
name: docs-generator
description: Генерация документации состояния окружения после деплоя. Обновляет _status/DEV.md, _status/PROD.md, PENDING_RELEASE.md, DEVELOPMENT_STATUS.md.
tools: Read, Grep, Glob, Bash, Edit, Write
model: opus
---

# Docs Generator Agent

## Задача
После каждого деплоя обновить:

### 1. _status/{ENV}.md
Что задеплоено: версия, коммит, дата, фичи, команды, техдетали.

### 2. _status/PENDING_RELEASE.md
Diff DEV → PROD: новые фичи, изменённые файлы, что тестировать.

```bash
git diff prod..dev --name-only
git log prod..dev --oneline
```

### 3. _status/DEVELOPMENT_STATUS.md
Текущее состояние: что в работе, последние изменения, баги, roadmap.

## Правила
- НЕ включай секреты
- Пиши понятно для человека
- Сравнивай с другим окружением
```

### `.claude/agents/test-runner.md`

```markdown
---
name: test-runner
description: Автоматическое тестирование (lint, types, tests, smoke). Используй после разработки для проверки кода.
tools: Bash, Read, Grep, Glob
model: opus
---

# Test Runner Agent

## Порядок тестов
1. **Lint** — стиль кода
2. **Type Check** — типизация
3. **Syntax Check** — компиляция
4. **Import Check** — зависимости
5. **Unit Tests** — pytest / jest
6. **Smoke Tests** — подключение к БД/API

## Формат отчёта

```
## Test Report

### Summary
Total: X | Passed: Y | Failed: Z

### Results
| Test | Status | Details |
|------|--------|---------|
| Lint | PASS/FAIL | ... |
| Types | PASS/FAIL | ... |
| ... | ... | ... |

### Errors
{файл:строка — описание}

### Recommendations
{что исправить}
```

## Правила
- Запускай ВСЕ тесты даже если один падает
- Возвращай ПОЛНЫЙ вывод
- НЕ исправляй ошибки — только отчёт
```

---

## 9. Проектная инфраструктура

### `_status/DEV.md` (шаблон)

```markdown
# DEV Environment Status

> Последнее обновление: {YYYY-MM-DD HH:MM}

## Deployment Info

| Параметр | Значение |
|----------|----------|
| Version | {VERSION} |
| Commit | {HASH} ({MSG}) |
| Branch | dev |
| Deployed | {DATE} |
| URL/Bot | {DEV URL} |

## Доступные фичи
- {фича 1}
- {фича 2}

## Технические детали
- ...

## Отличия от PROD
- ...
```

### `_status/PENDING_RELEASE.md` (шаблон)

```markdown
# Pending Release — DEV → PROD

> Последнее обновление: {DATE}

## Сводка
DEV: **{DEV_VERSION}** | PROD: **{PROD_VERSION}**

## Новые фичи (только в DEV)

| Фича | Описание | Готовность |
|------|----------|------------|

## Изменённые файлы
{git diff prod..dev --name-only}

## Что тестировать перед релизом
- [ ] ...

## Коммиты для релиза
{git log prod..dev --oneline}
```

### `_status/DEVELOPMENT_STATUS.md` (шаблон)

```markdown
# Development Status

> Для быстрого возвращения к проекту после паузы
> Последнее обновление: {DATE}

## Текущее состояние
- Ветка: {branch}
- Последний коммит: {msg}

## В работе
- {задача}

## Готово к релизу
- {фича}

## Известные баги
- {баг}

## Roadmap
- [ ] {ближайшее}
- [ ] {в перспективе}
```

### `_changelogs/prod.md` (шаблон)

```markdown
# Production Changelog

## {VERSION} — {YYYY-MM-DD}

### Added
- {новая фича}

### Changed
- {изменение}

### Fixed
- {багфикс}
```

### `documentation/README.md` (шаблон)

```markdown
# Documentation

| Файл | Описание |
|------|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Архитектура системы |
| [ERROR_REGISTRY.md](ERROR_REGISTRY.md) | Реестр ошибок с root causes |
```

### `documentation/ERROR_REGISTRY.md` (шаблон)

```markdown
# Error Registry

Structured errors with root causes and fixes. Newest first.

## {YYYY-MM-DD} — [{category}] Short description

**Symptom:** what happened
**Root Cause:** why (dig deep)
**Fix:** what was done
**Prevention:** how to avoid in future
**Files:** affected files
```

---

## 10. Как кастомизировать под тип проекта

### Python Backend (Telegram-бот, API)

CLAUDE.md:
- Стек: Python 3.11+, aiogram/FastAPI, Supabase/PostgreSQL, Redis, Docker
- Архитектура: Handlers → Services → Repositories
- Команды: `PYTHONPATH=src python -m app.main`, `pytest`, `ruff check src/`

settings.json hook: `ruff check --fix` после Write на `.py`

Дополнительные скиллы:
- `/rollback` — откат деплоя
- `/logs` — просмотр логов VPS

### Web Frontend (Astro, Next.js, React)

CLAUDE.md:
- Стек: TypeScript, Astro/Next.js, Tailwind CSS
- Архитектура: Pages → Components → Data
- Команды: `npm run dev`, `npm run build`, `npm test`

settings.json hook: `prettier --write` или `eslint --fix` после Write

Дополнительные скиллы:
- Component Naming Convention в CLAUDE.md
- Analytics Events список
- Routing таблица

### Контент/PM проект (без кода)

CLAUDE.md:
- Убрать секции: Стек, Архитектура, Окружения, Deploy
- Добавить: Команда проекта, Целевая аудитория, "Как со мной работать"

Основные скиллы:
- `/project-manager` — бэклог, спринты
- `/docs` — документация (упрощённая)
- skill-creator — для создания доменных скиллов

Дополнительно:
- README.md Memory Bank в каждой папке
- FACTS.md для ключевых фактов
- Cross-references с [REF:] тегами

### Гибридный проект (код + PM + контент)

Полный шаблон + domain-specific скиллы:
- `/ecom-manager` для e-commerce
- `/presentation-storytelling` для выступлений
- Кастомные роли в `references/role.md`

---

## 11. Чеклист запуска нового проекта

### Фаза 1: Инициализация (5 мин)

- [ ] Скопировать структуру из шаблона
- [ ] Заполнить CLAUDE.md (проект, стек, архитектура)
- [ ] Настроить .claude/settings.json (hooks под стек)
- [ ] Создать VERSION файл
- [ ] `git init && git add . && git commit -m "init: project scaffold"`

### Фаза 2: Git Workflow (5 мин)

- [ ] Создать ветки: `git branch dev && git branch prod`
- [ ] Настроить remote: `git remote add origin {URL}`
- [ ] Заполнить секцию "Окружения" в CLAUDE.md
- [ ] Адаптировать deploy-dev и deploy-prod скиллы

### Фаза 3: Кастомизация (10 мин)

- [ ] Адаптировать /test скилл под стек проекта
- [ ] Удалить неиспользуемые скиллы
- [ ] Добавить domain-specific скиллы (если нужно)
- [ ] Проверить что /commit и /git-status работают

### Фаза 4: Первый цикл

- [ ] Написать первый код
- [ ] `/commit` — первый коммит
- [ ] `/cherry-pick` → `/deploy-dev` — первый деплой
- [ ] `/test` — первые тесты
- [ ] `/docs` — первая документация
- [ ] Проверить что error-learning правило работает

---

> Этот документ — полный blueprint для запуска любого проекта с Claude Code.
> Все шаблоны готовы к копированию и адаптации.
