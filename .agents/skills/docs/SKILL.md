---
name: docs
description: Обновление документации после деплоя — _status/ файлы, changelogs, architecture docs, error registry. Используй при docs, обновить документацию, после деплоя, update docs.
---

# /docs — Documentation Update

## Instructions

### 1. Собери информацию

```bash
cat VERSION
git log --oneline -10
git rev-parse --abbrev-ref HEAD
date "+%Y-%m-%d %H:%M"
```

### 2. Определи контекст

Какое окружение было задеплоено?
- **DEV** — обнови _status/DEV.md + PENDING_RELEASE.md + DEVELOPMENT_STATUS.md
- **PROD** — обнови _status/PROD.md + PENDING_RELEASE.md + DEVELOPMENT_STATUS.md + _changelogs/prod.md

### 3. Обнови _status/{ENV}.md

- Последнее обновление (дата)
- Version, Commit в Deployment Info
- Новые фичи (если были)

### 4. Обнови _status/PENDING_RELEASE.md

```bash
git log prod..dev --oneline
git diff prod..dev --name-only
```

### 5. Обнови _status/DEVELOPMENT_STATUS.md

- Что сейчас в работе
- Последние изменения
- Известные баги
- Roadmap

### 6. Обнови documentation/ERROR_REGISTRY.md (если был багфикс)

Добавь запись: симптом, причина, фикс, предотвращение.

### 7. Обнови _changelogs/{env}.md (если PROD)

```markdown
## {VERSION} — {YYYY-MM-DD}

### Added
- ...

### Changed
- ...

### Fixed
- ...
```

### 8. Отчёт

```
## Documentation Updated

| File | Changes |
|------|---------|
| _status/{ENV}.md | Updated version, features |
| PENDING_RELEASE.md | Updated diff |
| DEVELOPMENT_STATUS.md | Updated current state |
| ... | ... |
```
