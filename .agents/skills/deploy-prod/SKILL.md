---
name: deploy-prod
description: Деплой на PROD окружение. ТРЕБУЕТ подтверждения и тестирования на DEV. Используй при deploy prod, деплой на прод, выкатить на production, задеплоить на prod.
---

# /deploy-prod — Deploy to PROD

## Instructions

### 1. Safety Checklist

**ОБЯЗАТЕЛЬНО перед деплоем на PROD:**

```
PRODUCTION DEPLOYMENT CHECKLIST:

[ ] Код протестирован на DEV?
[ ] Все тесты проходят?
[ ] Критических багов не обнаружено?
[ ] Подтверждаете деплой на PROD?
```

**ВСЕ пункты должны быть подтверждены! Без подтверждения — НЕ деплоить!**

### 2. Проверь ветку

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "prod" ]; then
  echo "ERROR: Current branch is $BRANCH, need prod"
  exit 1
fi
```

### 3. Деплой

```bash
{./scripts/deploy.sh prod}
```

### 4. Проверь логи

```bash
{ssh server 'docker logs app-prod --tail 20'}
```

### 5. Post-deploy (ОБЯЗАТЕЛЬНО)

1. Протестируй что деплой работает
2. Запусти `/docs` для обновления документации
3. Обнови VERSION (semver: patch/minor/major)
4. Обнови `_changelogs/prod.md`
5. Проверь синхронизацию веток

```
❌ НЕ ЗАВЕРШАЙ работу после PROD деплоя, пока ВСЕ 5 шагов не выполнены!
```

### 6. Вернись на local

```bash
git checkout local
```

### 7. Результат

```
Deployed to PROD

Next steps:
  1. Monitor {PROD URL/bot}
  2. Check logs for errors
  3. /docs — update documentation
```
