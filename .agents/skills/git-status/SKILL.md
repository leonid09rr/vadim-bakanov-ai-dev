---
name: git-status
description: Статус всех веток git workflow — текущая ветка, незакоммиченные изменения, непушнутые коммиты, diff между ветками. Используй при git-status, статус, состояние веток, что в работе.
---

# /git-status — Multi-Branch Status

## Instructions

### 1. Собери информацию

```bash
echo "=== Current branch ==="
git rev-parse --abbrev-ref HEAD

echo "=== Working tree ==="
git status --short

echo "=== Recent commits ==="
git log --oneline -5

echo "=== All branches ==="
git branch -vv

echo "=== Unpushed to dev ==="
git log origin/dev..dev --oneline 2>/dev/null || echo "N/A"

echo "=== Unpushed to prod ==="
git log origin/prod..prod --oneline 2>/dev/null || echo "N/A"

echo "=== Pending release (dev → prod) ==="
git log prod..dev --oneline 2>/dev/null || echo "N/A"
```

### 2. Покажи отчёт

```
## Git Status

**Current branch:** {branch}

### Uncommitted changes
{clean / list of changes}

### Recent commits (local)
{last 5 commits}

### Unpushed to remote
- dev: {N} commits
- prod: {N} commits

### Pending release (dev → prod)
{commits in dev not yet in prod, or "Up to date"}

### Branch sync
- local ↔ dev: {in sync / N commits ahead}
- dev ↔ prod: {in sync / N commits ahead}
```
