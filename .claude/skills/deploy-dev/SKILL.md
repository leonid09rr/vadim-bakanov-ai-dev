---
name: deploy-dev
description: Деплой на DEV окружение. Используй при deploy dev, деплой на дев, развернуть dev, выкатить на дев, задеплоить на dev.
---

# /deploy-dev — Deploy to DEV

## Instructions

### 1. Проверь ветку

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "dev" ]; then
  echo "ERROR: Current branch is $BRANCH, need dev"
  exit 1
fi
```

Если не dev: "Переключись на dev: `git checkout dev`"

### 2. Проверь синхронизацию

```bash
git fetch origin dev
git status
```

Если behind remote: "Сначала pull: `git pull origin dev`"

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

Next steps:
  1. Test on {DEV URL/bot}
  2. If bugs → fix in local, repeat
  3. /test for validation
  4. /docs — update documentation
  5. If all good → /merge-to-prod
```
