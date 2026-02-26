# PostToolUse Hooks — Examples

Copy the relevant hook into `.claude/settings.json` under `hooks.PostToolUse`.

## Python (ruff) — already in settings.json

```json
{
  "matcher": "Write",
  "hooks": [
    {
      "type": "command",
      "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path\"); if [[ \"$FILE\" == *.py ]]; then ruff check --fix \"$FILE\" 2>&1; fi'"
    }
  ]
}
```

## TypeScript/JavaScript (eslint)

```json
{
  "matcher": "Write",
  "hooks": [
    {
      "type": "command",
      "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path\"); if [[ \"$FILE\" == *.ts || \"$FILE\" == *.tsx || \"$FILE\" == *.js || \"$FILE\" == *.jsx ]]; then npx eslint --fix \"$FILE\" 2>&1; fi'"
    }
  ]
}
```

## Astro/Svelte (prettier)

```json
{
  "matcher": "Write",
  "hooks": [
    {
      "type": "command",
      "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path\"); if [[ \"$FILE\" == *.astro || \"$FILE\" == *.svelte || \"$FILE\" == *.vue ]]; then npx prettier --write \"$FILE\" 2>&1; fi'"
    }
  ]
}
```

## Combined (Python + TypeScript)

```json
{
  "matcher": "Write",
  "hooks": [
    {
      "type": "command",
      "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path\"); if [[ \"$FILE\" == *.py ]]; then ruff check --fix \"$FILE\" 2>&1; elif [[ \"$FILE\" == *.ts || \"$FILE\" == *.tsx ]]; then npx eslint --fix \"$FILE\" 2>&1; fi'"
    }
  ]
}
```
