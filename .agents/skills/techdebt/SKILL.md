---
name: techdebt
description: Поиск технического долга и проблем качества кода — TODO/FIXME, большие файлы, неиспользуемые импорты, устаревшие зависимости. Используй при techdebt, технический долг, cleanup, рефакторинг, TODO, качество кода.
---

# /techdebt — Technical Debt Scanner

## Instructions

### 1. Сканирование

Выполни ВСЕ проверки:

```bash
# TODO/FIXME/HACK комментарии
grep -rn "TODO\|FIXME\|HACK\|XXX" src/ --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.astro" 2>/dev/null || echo "Нет TODO"

# Большие файлы (>300 строк)
find src/ -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.astro" \) -exec wc -l {} + 2>/dev/null | awk '$1 > 300 {print}' | sort -rn

# Устаревшие зависимости
pip list --outdated 2>/dev/null | head -20 || npm outdated 2>/dev/null | head -20 || echo "Не удалось проверить"

# Type check warnings
mypy src/ --ignore-missing-imports --no-error-summary 2>/dev/null | head -30 || echo "mypy not available"
```

### 2. Дополнительный анализ

Проанализируй код на:
- **Дублирование** — похожие функции/блоки
- **Сложность** — функции >50 строк, глубокая вложенность
- **Мёртвый код** — неиспользуемые функции/классы
- **Нарушения архитектуры** — прямые импорты между слоями

### 3. Отчёт по приоритетам

```
## Tech Debt Summary

| Категория | Найдено | Критичность |
|-----------|---------|-------------|
| TODO/FIXME | N | Low |
| Большие файлы | N | Medium |
| Устаревшие deps | N | Low |
| Проблемы типизации | N | Medium |

**Топ-3 приоритета:**
1. {файл} — {проблема} — {рекомендация}
2. ...
3. ...
```

**Правило:** НЕ исправляй — только отчёт и рекомендации.

### Режимы

| Команда | Действие |
|---------|----------|
| `/techdebt` | Быстрый обзор |
| `/techdebt full` | Детальный отчёт в `_status/TECHDEBT.md` |
| `/techdebt focus:todo` | Только TODO/FIXME |
