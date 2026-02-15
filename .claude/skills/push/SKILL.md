---
name: push
description: Безопасный push на remote с показом что будет отправлено и подтверждением. Используй при push, пуш, отправить, запушить.
---

# /push — Safe Push

## Instructions

### 1. Покажи что будет запушено

```bash
BRANCH=$(git branch --show-current)
git log origin/$BRANCH..$BRANCH --oneline 2>/dev/null || echo "No remote tracking branch"
```

### 2. Спроси подтверждение

```
Push to origin/{branch}:
- {N} commits
- {list of commit messages}

Confirm? [y/N]
```

### 3. Push (при подтверждении)

```bash
git push origin $(git branch --show-current)
```

### 4. Результат

```
Pushed to origin/{branch}: {N} commits

Next: /deploy-dev | /git-status
```
