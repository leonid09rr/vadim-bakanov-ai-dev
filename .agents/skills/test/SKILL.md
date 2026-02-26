---
name: test
description: Тестирование кода и функционала — lint, types, unit tests, build check. Используй при тестировании, проверке, test, lint, smoke test, проверке качества кода.
---

# /test — Testing & Validation

## Instructions

Запускай все тесты по порядку. Если один падает — продолжай остальные.

### 1. Lint

```bash
# Python
ruff check src/ 2>&1 || echo "ruff not available"

# TypeScript/JS
npx eslint src/ 2>&1 || echo "eslint not configured"
```

### 2. Type Check

```bash
# Python
mypy src/ --ignore-missing-imports --no-error-summary 2>&1 || echo "mypy not available"

# TypeScript
npx tsc --noEmit 2>&1 || echo "tsc not configured"
```

### 3. Unit Tests

```bash
# Python
pytest tests/ -v --tb=short 2>&1 || echo "No tests found"

# Node
npm test 2>&1 || echo "No tests configured"
```

### 4. Build Check

```bash
# Python
python -m py_compile src/main.py 2>&1 || echo "No main.py"

# Node
npm run build 2>&1 || echo "Build not configured"
```

### 5. Отчёт

```
## Test Report

### Summary
Total: X | Passed: Y | Failed: Z

### Results

| Test | Status | Notes |
|------|--------|-------|
| Lint | PASS/FAIL | ... |
| Types | PASS/FAIL/SKIP | ... |
| Unit Tests | PASS/FAIL/SKIP | ... |
| Build | PASS/FAIL | ... |

### Issues Found
{list or "None"}

### Recommendation
{Ready for deploy / Needs fixes}
```

**Правило:** НЕ исправляй ошибки — только отчёт.
