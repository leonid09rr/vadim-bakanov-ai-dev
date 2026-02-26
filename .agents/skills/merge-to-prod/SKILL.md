---
name: merge-to-prod
description: Merge ветки dev в prod для релиза. ТРЕБУЕТ подтверждения. Используй при merge-to-prod, релиз, выкатить на прод, merge в prod, мерж в прод.
---

# /merge-to-prod — Release to Production

## Instructions

### 1. Покажи что будет смержено

```bash
echo "=== Commits in dev but not in prod ==="
git log prod..dev --oneline

echo "=== Changed files ==="
git diff prod..dev --name-only
```

### 2. ОБЯЗАТЕЛЬНО спроси подтверждение

```
PRODUCTION MERGE

Коммиты из dev → prod:
{список коммитов}

Изменённые файлы:
{список файлов}

Код протестирован на DEV? Подтвердите merge в prod.
```

**Без подтверждения — НЕ мержить!**

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

Commits merged: {N}

Next: /push (push prod) | /deploy-prod
```
