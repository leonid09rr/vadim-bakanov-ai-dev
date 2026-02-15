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
| [test](test/SKILL.md) | `/test` | Тестирование кода (lint, types, unit, build) |
| [techdebt](techdebt/SKILL.md) | `/techdebt` | Поиск технического долга |

## Documentation & Planning

| Skill | Команда | Описание |
|-------|---------|----------|
| [docs](docs/SKILL.md) | `/docs` | Обновление документации после деплоя |
| [architect](architect/SKILL.md) | `/architect` | Архитектурный анализ и планирование фич |
| [project-manager](project-manager/SKILL.md) | `/project-manager` | Управление задачами и бэклогом |

## Git Workflow

```
local (разработка)
  │
  ├─> /commit
  │
  └─> /cherry-pick → dev (тестирование)
                       │
                       ├─> /deploy-dev → Test
                       │
                       └─> /merge-to-prod → prod (production)
                                              │
                                              └─> /deploy-prod → /docs
```
