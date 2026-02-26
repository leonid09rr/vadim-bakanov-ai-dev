# AGENTS.md — Project Template

Last Updated: 2026-02-26

## Language
Use the same response language as the user used in their questions.
If the user writes in Russian, respond in Russian; if in English, respond in English.

## Response Format

Response format for all tasks:
1. **Task Clarity:** <0-100%> - if <70%, ask clarifying questions first
2. **Confidence in the Answer:** <0-100%>
3. **Role:** <expert role relevant to the request>
4. **TL;DR** - brief answer
5. **Full Answer**

## Project

{One-two sentences: what the project is, for whom, why}

## Stack

| Component | Technology |
|-----------|------------|
| Language | {Python 3.11+ / TypeScript / ...} |
| Framework | {aiogram 3.x / Astro / Next.js / ...} |
| DB | {Supabase / PostgreSQL / SQLite / ...} |
| Cache | {Redis / ...} |
| Hosting | {VPS / Vercel / ...} |
| CI/CD | {Docker / GitHub Actions / ...} |

## Architecture

```
{Handlers/Pages} → {Services/API} → {Repositories/Models}
```

## Project Structure

```
{project}/
├── src/
│   ├── ...
├── tests/
├── scripts/
├── deploy/
├── documentation/
├── _specs/
├── _changelogs/
├── _status/
└── backlog/
```

## Environments

| Env | URL/Bot | DB | Branch |
|-----|---------|-----|-------|
| DEV | {dev URL} | {dev DB} | dev |
| PROD | {prod URL} | {prod DB} | prod |

## Critical Rules

### Working Branch — `local`

The `local` branch is the main developer branch. After ANY operation (deploy, push, merge, cherry-pick) — ALWAYS return to the `local` branch.

### Deploy to PROD

1. **NEVER deploy directly to PROD** — always DEV first
2. **Explicit user confirmation required**
3. Workflow: `local → DEV → test → PROD`

### After EVERY Deploy

1. Verify the deploy works
2. Update documentation
3. Update VERSION for significant changes (semver)
4. Update changelog (`_changelogs/`)
5. Check branch synchronization

Do NOT consider a deploy finished until all steps are completed.

### Security

- `.env.*` files — **NEVER commit** (in .gitignore)
- Secrets only from environment variables, never hardcoded
- Functions marked `# SECURITY-SENSITIVE` require extra attention
- Never log secret values (tokens, keys, passwords)
- Never remove existing validations without discussion

## Git Workflow

```
local (development) → cherry-pick → dev (testing) → merge → prod (production)

main — frozen (archive)
```

| Branch | Purpose | What to commit |
|--------|---------|----------------|
| **local** | Developer working branch | Everything: code, specs, plans, TODO |
| **dev** | Testing environment | Only working code (completed features) |
| **prod** | Production | Only tested code |

### Git Rules

- **DO NOT** commit/push/merge without user confirmation
- **DO NOT** force push, reset --hard, rebase without explicit request
- **DO NOT** commit secrets (.env, credentials)
- **DO NOT** use `git add -A` or `git add .` — add files individually
- Use conventional commits: `<type>(<scope>): <description>`
- Types: feat | fix | docs | style | refactor | test | chore | perf

## Commands

```bash
# Local run
{run command}

# Tests
{test command}

# Lint
ruff check src/ || npx eslint src/

# Deploy
./scripts/deploy-dev.sh
./scripts/deploy-prod.sh

# Smoke test
./scripts/smoke-test.sh [local|dev|prod]

# VPS management
./scripts/connect-vps.sh [shell|logs|status|restart|postgres|redis|ssh]
```

## Available Skills

Skills are located in `.agents/skills/`. Use `$skill-name` or `/skills` to invoke.

| Skill | Description |
|-------|-------------|
| `commit` | AI-generated commit message (conventional commits) |
| `push` | Safe push with preview and confirmation |
| `backup` | Quick backup to GitHub (commit + push) |
| `cherry-pick` | Transfer commits: local → dev |
| `merge-to-prod` | Merge dev → prod (requires confirmation) |
| `deploy-dev` | Deploy to DEV environment |
| `deploy-prod` | Deploy to PROD (with safety checklist) |
| `rollback` | Rollback deploy on DEV/PROD |
| `logs` | View DEV/PROD logs via SSH |
| `git-status` | Multi-branch status overview |
| `test` | Run lint, types, unit tests, build |
| `qa-tester` | Comprehensive QA testing (HTTP, content, visual) |
| `docs` | Update documentation after deploy |
| `techdebt` | Scan for technical debt |
| `architect` | Architecture analysis and planning |
| `project-manager` | Backlog, sprints, priorities |
| `seo-research` | Competitive SEO analysis with keyword clustering |
| `seo-audit` | SEO + AEO audit with Schema.org markup |
| `seo-content` | Keyword research and content optimization |
| `seo-positions` | Position monitoring in Google and Yandex |

## Development Principles

- **KISS** — simplicity over complexity
- **YAGNI** — don't write code for the future
- **Plan then Act** — plan first, implement second
- **SRP** — single responsibility per function
- **Three-Layer Rule** — Handlers → Services → Models
- **Open/Closed** — extend, don't rewrite working code
- **Dead Code** — delete dead code, don't comment it out
- **DRY** — don't duplicate knowledge (but similar code in different contexts is OK)

### Red Flags: Over-Engineering

- More than 3 abstraction layers for a single operation
- Factories creating factories
- Complex configuration instead of environment variables
- Multiple ways to do the same thing

## Documentation

- `documentation/` — architecture, errors
- `_specs/` — specifications
- `_specs/templates/` — templates: user-spec, tech-spec, task
- `_changelogs/` — release history
- `_status/` — current environment state
- `backlog/` — tasks

## Infrastructure

- `scripts/` — deploy, testing, VPS management scripts
- `deploy/` — Docker, Nginx, pyproject.toml templates

## Additional Context

For Claude Code-specific instructions, see `CLAUDE.md`.
