---
name: rollback
description: Откат к предыдущей версии на DEV/PROD. Используй при rollback, откатить, вернуть версию, отменить деплой, revert.
---

# /rollback — Rollback Deployment

Откат к предыдущей версии приложения.

## CRITICAL: Требует подтверждения!

Откат — это деструктивная операция. Всегда запрашивай подтверждение.

## Instructions

### 1. Определи окружение

```
Rollback target:
[ ] DEV  — {dev_url}
[ ] PROD — {prod_url} (ТРЕБУЕТ ДВОЙНОЕ ПОДТВЕРЖДЕНИЕ!)
```

### 2. Проверь текущее состояние

```bash
# Текущая ветка
git rev-parse --abbrev-ref HEAD

# Последние коммиты
git log --oneline -5

# Текущая версия
cat VERSION
```

### 3. Определи точку отката

**Варианты:**

A) **Откат на 1 коммит назад:**
```bash
git log --oneline -3
# Покажет последние 3 коммита
```

B) **Откат на конкретный коммит:**
```bash
git log --oneline -10
# Пользователь выбирает коммит
```

C) **Откат на предыдущую версию:**
```bash
git tag -l --sort=-version:refname | head -5
# Список последних тегов версий
```

### 4. Safety Checklist (PROD)

**ТОЛЬКО для PROD:**

```
PRODUCTION ROLLBACK CHECKLIST:

[ ] Причина отката понятна? [y/N]:
[ ] Логи проверены? [y/N]:
[ ] Критическая проблема подтверждена? [y/N]:
[ ] Готов к rollback? [y/N]:

Type 'rollback production' to confirm:
```

### 5. Выполни откат

**Метод 1: Git Revert (безопасный)**
```bash
git checkout <branch>  # dev или prod
git revert HEAD --no-edit
git push origin <branch>
```

**Метод 2: Git Reset (если revert не подходит)**
```bash
git checkout <branch>
git reset --hard <commit-hash>
git push origin <branch> --force
```

⚠️ **Force push требует ЯВНОГО подтверждения!**

### 6. Редеплой

```bash
./scripts/deploy-dev.sh   # для DEV
./scripts/deploy-prod.sh  # для PROD
```

### 7. Проверь результат

```bash
# Логи
ssh {vps-alias} 'docker logs {dev_container_name} --tail 20'  # DEV
ssh {vps-alias} 'docker logs {prod_container_name} --tail 20'  # PROD

# Версия
cat VERSION
```

### 8. Вернись на local

```bash
git checkout local
```

### 9. Результат

```
## Rollback: DEV / PROD

### Status: SUCCESS / FAIL

### Details
- Previous commit: abc1234
- Rolled back to: def5678
- Version: X.Y.Z

### Verification
- Container status: OK
- Logs: No errors
- App responds: Yes

### Next Steps
- Monitor logs for issues
- Test critical functionality
- Document the incident
```

## Rollback Methods Comparison

| Метод | Когда использовать | Безопасность |
|-------|-------------------|--------------|
| `git revert` | Обычный откат, сохраняет историю | Безопасный |
| `git reset --hard` | Критичная ситуация, нужно полное удаление | Опасный |
| Redeploy старой версии | Если код не менялся, только конфиг | Безопасный |

## Critical Rules

1. **ВСЕГДА** делай backup перед rollback: `git stash` или новая ветка
2. **НИКОГДА** не делай force push без явного подтверждения
3. **PROD rollback** требует двойного подтверждения
4. **ВСЕГДА** проверяй логи после rollback
5. **ВСЕГДА** возвращайся на `local` после завершения
6. **Документируй** причину отката в коммите
