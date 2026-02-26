---
name: qa-tester
description: >
  Комплексное QA-тестирование — HTTP smoke, контент-анализ, визуальное тестирование
  с Playwright MCP, тестирование с авторизацией. Поддержка LOCAL/DEV/PROD.
  Используй при: qa-tester, тестирование, quality assurance, smoke test, проверка сайта,
  проверка после деплоя, pre-deploy check, qa, тест окружения.
---

# /qa-tester — QA Testing Agent

## Использование

```
/qa-tester              → LOCAL, L1+L2
/qa-tester dev          → DEV, L1+L2
/qa-tester prod         → PROD, L1 (safe default)
/qa-tester dev full     → DEV, L1+L2+L3 (полное)
/qa-tester prod l2      → PROD, L1+L2
/qa-tester local l3     → LOCAL, L3 only
```

## Phase 0: Setup

### 1. Определи окружение

Парсинг аргументов: первый аргумент = env, остальные = уровни.

```
ENV = первый аргумент (local/dev/prod), default: local
LEVELS = остальные аргументы (l1/l2/l3/full), default: зависит от ENV
```

### 2. Разреши URL и auth

```bash
case ENV:
  local → BASE_URL="http://localhost:{PORT}", AUTH=""
  dev   → BASE_URL="{DEV_URL}", AUTH="{DEV_AUTH_IF_NEEDED}"
  prod  → BASE_URL="{PROD_URL}", AUTH=""
```

### 3. Определи уровни по дефолту

```
local → L1 + L2
dev   → L1 + L2
prod  → L1
full  → L1 + L2 + L3
```

### 4. Проверь доступность инструментов

- L1: всегда доступен (curl через Bash)
- L2: всегда доступен (WebFetch)
- L3: проверь наличие Playwright MCP. Если недоступен — предупреди и пропусти L3

### 5. Покажи план тестирования

```
QA Test Plan — {PROJECT}
Environment: {ENV} ({BASE_URL})
Levels: {L1 + L2 + ...}
Categories: C1-C7

Starting...
```

---

## Phase 1: L1 Smoke (curl)

### 1a. Запусти smoke-test.sh (если есть)

```bash
./scripts/smoke-test.sh {ENV}
```

### 1b. Дополнительные curl-проверки

**ВАЖНО:** Каждый curl-вызов выполняй ОТДЕЛЬНОЙ Bash-командой.

**Публичные страницы (expect 200):**

```bash
# curl -s -o /dev/null -w "%{http_code}" "$BASE_URL{ROUTE}"
/             → 200
# Добавь другие публичные роуты проекта
```

**Auth redirect (expect 302 → /login без сессии):**

```bash
# curl -s -o /dev/null -w "%{http_code}" "$BASE_URL{ROUTE}"
# НЕ использовать -L, чтобы увидеть 302
/dashboard    → 302
/admin        → 302
```

**API endpoints:**

```bash
# Health check
curl -s "$BASE_URL/api/health"
# Ожидание: {"status":"ok"}
```

**404:**

```bash
curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/nonexistent-slug-xyz-12345"
# Ожидание: 404
```

**PROD ограничения:** На PROD НЕ тестировать POST-эндпоинты, которые меняют данные.

---

## Phase 2: L2 Content (WebFetch)

Пропусти если L2 не в плане.

### Homepage (/)

WebFetch `$BASE_URL/` → проверь:
- Title присутствует и не пустой
- Meta description присутствует и непустой
- Есть навигация
- Есть основной контент
- Нет текста "error", "500", "undefined"

### Другие ключевые страницы

WebFetch каждую ключевую страницу → проверь:
- Title присутствует
- Основной контент рендерится
- Нет ошибок

**Проверка "error" в HTML:** слова `error`, `hasErrorBoundary` в HTML фреймворка — НЕ ошибки.
Ищи только: `500`, `Internal Server Error`, `Application Error`, `Unexpected`.

---

## Phase 3: L3 Visual (Playwright MCP)

Пропусти если L3 не в плане или Playwright MCP недоступен.

### Homepage

```
browser_navigate → $BASE_URL
browser_screenshot → (проверь визуал)
browser_console_messages → (проверь на JS errors: Error, TypeError, ReferenceError)
browser_snapshot → (проверь accessibility tree: heading, navigation, inputs)
```

### Ключевые страницы

Повтори для каждой ключевой страницы.

### Mobile viewport

```
browser_resize → width=375, height=667
browser_navigate → $BASE_URL
browser_screenshot → (проверь адаптивность: нет горизонтального скролла)
```

---

## Phase 4: Report

Собери результаты всех фаз в единый отчёт.

### Формат отчёта

```markdown
## QA Test Report — {PROJECT}

**Environment:** {ENV} ({BASE_URL})
**Date:** {YYYY-MM-DD HH:MM}
**Levels:** {L1 + L2 + ...}
**Duration:** {Xs}

### Summary
| Total | Passed | Failed | Warnings | Skipped | Status |
|-------|--------|--------|----------|---------|--------|
| N     | N      | N      | N        | N       | PASS/WARN/FAIL |

### C1: Инфраструктура
| Проверка | Статус | Детали |
|----------|--------|--------|
| ... | PASS/FAIL/WARN | ... |

### C2: Публичные страницы
...

### C3: API Endpoints
...

### C4: Auth Flow
...

### C5: Динамический контент
...

### C6: SEO & Accessibility
(если L2 выполнялся)
...

### C7: Visual & Interactive
(если L3 выполнялся)
...

### Issues Found
1. **FAIL** описание проблемы (категория)
2. **WARN** описание (категория)

### Recommendation
**PASS/WARN/FAIL** — краткий вердикт и рекомендация.
```

### Правила статуса

```
PASS = 0 FAIL, 0 WARN
WARN = 0 FAIL, 1+ WARN
FAIL = 1+ FAIL
```

### Правило

**НЕ исправляй ошибки** — только отчёт. Пользователь решает что фиксить.

---

## Адаптация под проект

При первом запуске в проекте — определи:
1. Какие публичные роуты есть (из router/pages)
2. Какие API endpoints есть
3. Какие защищённые роуты требуют auth
4. Есть ли smoke-test.sh

Сохрани конфигурацию в отчёте для повторного использования.
