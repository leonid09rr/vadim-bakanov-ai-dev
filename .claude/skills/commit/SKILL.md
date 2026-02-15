---
name: commit
description: AI-генерация commit message из git diff в conventional commit формате. Используй при коммите, создании коммита, git commit, сохранении изменений, закоммитить.
---

# /commit — AI-Generated Commit

Создать git коммит с AI-сгенерированным conventional commit message.

## Instructions

### 1. Проверь изменения

```bash
git status
git diff --stat
```

Если нет изменений: "Нет изменений для коммита."

### 2. Проанализируй diff

Прочитай diff и определи:
- Какие файлы изменены и зачем
- Тип изменения
- Scope (область)

### 3. Сгенерируй commit message

**Формат:**
```
<type>(<scope>): <subject>

<optional body — bullet points>

Co-Authored-By: Claude <model> <noreply@anthropic.com>
```

**Types:** feat | fix | docs | style | refactor | test | chore | perf

### 4. Покажи preview и спроси подтверждение

```
Изменённые файлы:
  M src/services/auth.py (+25, -3)
  A src/models/token.py

Предлагаемый коммит:
  feat(auth): add JWT token generation

  - Implement token creation with expiry
  - Add Token pydantic model

  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

Создать коммит? [y/N]
```

### 5. Создай коммит (при подтверждении)

```bash
git add <specific-files>
git commit -m "$(cat <<'EOF'
<message>
EOF
)"
```

**Правила:**
- НИКОГДА `git add -A` или `git add .`
- Добавляй файлы по отдельности
- Не коммить .env, credentials

### 6. Результат

```
Committed abc1234: feat(auth): add JWT token generation

Next: /cherry-pick → dev | /push | /git-status
```
