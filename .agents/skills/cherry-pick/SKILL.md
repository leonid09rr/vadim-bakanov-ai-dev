---
name: cherry-pick
description: Перенос последнего коммита из local в dev. Используй при cherry-pick, перенести в dev, передать в dev, перенос коммита.
---

# /cherry-pick — Transfer to Dev

## Instructions

### 1. Проверь текущую ветку

Должна быть `local`. Если нет — сообщи.

```bash
git rev-parse --abbrev-ref HEAD
```

### 2. Запомни коммит

```bash
COMMIT=$(git log -1 --format="%H")
MSG=$(git log -1 --format="%s")
echo "Cherry-picking: $COMMIT — $MSG"
```

### 3. Перенеси

```bash
git checkout dev
git cherry-pick $COMMIT
```

Если конфликт:
```
Cherry-pick failed: merge conflict in {files}
Resolve manually or abort: git cherry-pick --abort
```

### 4. Вернись на local

```bash
git checkout local
```

### 5. Результат

```
Cherry-picked {short_hash}: {message} → dev

Next: /push (push dev) | /deploy-dev
```
