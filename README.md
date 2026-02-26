# AI Coding Agent Project Template

Ready-to-use project scaffold with pre-configured skills, agents, rules, and deployment infrastructure. Compatible with **Claude Code** and **OpenAI Codex CLI**.

## Agent Compatibility

| Feature | Claude Code | OpenAI Codex |
|---------|-------------|--------------|
| Instructions file | `CLAUDE.md` | `AGENTS.md` |
| Skills location | `.claude/skills/` | `.agents/skills/` |
| Skill format | `SKILL.md` (YAML frontmatter) | `SKILL.md` (YAML frontmatter) |
| UI metadata | — | `agents/openai.yaml` |
| Config | `.claude/settings.json` | `~/.codex/config.toml` |

Both instruction sets are included. Each agent reads its own file automatically.

## What's Inside

### AI Brain — Claude Code (`.claude/`)
- **21 skills** — slash commands for git, deploy, testing, architecture, project management, SEO
- **3 agents** — deployer, test-runner, docs-generator
- **2 rules** — error-learning, auto-backup
- **Hooks** — auto-linting on file write (Python/ruff)

### AI Brain — OpenAI Codex (`.agents/`)
- **21 skills** — mirrored from Claude Code, adapted for Codex
- **`agents/openai.yaml`** — UI metadata for each skill
- Path references updated for `.agents/skills/` structure

### Documentation Infrastructure
- **CLAUDE.md** — master instructions for Claude Code
- **AGENTS.md** — master instructions for OpenAI Codex
- **AGENDA.md** — working session memory (current focus, next steps)
- **_status/** — environment state tracking (DEV/PROD)
- **_changelogs/** — release history
- **_specs/** — specifications + templates (user-spec, tech-spec, task)
- **backlog/** — task management
- **documentation/** — architecture docs, error registry

### Deployment Templates (`deploy/`)
- **Dockerfiles** — Python (3.11-slim + non-root + healthcheck) and Node.js (multi-stage)
- **docker-compose** — DEV (dev-friendly) and PROD (logging, always-restart)
- **Nginx configs** — DEV (Basic Auth + API bypass) and PROD (HSTS, caching, security headers)
- **pyproject.toml** — Python project config (ruff, pytest, dependency groups)
- **Hooks examples** — PostToolUse for Python, TypeScript, Astro

### Operational Scripts (`scripts/`)
- **smoke-test.sh** — 6-category HTTP smoke test (connectivity, headers, HTML, routes, assets, API)
- **deploy-dev.sh** — Pre-checks, DB backup, rsync, docker build, health polling, smoke test
- **deploy-prod.sh** — Same as DEV + safety warnings, 30 backup retention
- **connect-vps.sh** — SSH master script (shell, logs, status, restart, postgres, redis)

## Skills (Slash Commands)

| Command | Description |
|---------|-------------|
| `commit` | AI-generated commit messages (conventional commits) |
| `push` | Safe push with preview and confirmation |
| `backup` | Quick backup to GitHub (commit + push) |
| `cherry-pick` | Transfer commits: local -> dev |
| `merge-to-prod` | Merge dev -> prod (requires confirmation) |
| `git-status` | Multi-branch status overview |
| `deploy-dev` | Deploy to DEV environment |
| `deploy-prod` | Deploy to PROD (with safety checklist) |
| `rollback` | Rollback deploy on DEV/PROD |
| `logs` | View DEV/PROD logs via SSH |
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
| `lawyer` | Russian commercial law for IP |

## Git Workflow

```
local (development) -> cherry-pick -> dev (testing) -> merge -> prod (production)
```

## Quick Start

1. Clone/copy this template
2. Fill in `{placeholders}` in `CLAUDE.md` and `AGENTS.md` (project name, stack, URLs)
3. Fill in `{placeholders}` in `scripts/*.sh` (VPS host, domain, paths)
4. Copy relevant files from `deploy/` to project root (Dockerfile, docker-compose, nginx)
5. Adapt `.claude/settings.json` hooks for your stack (see `deploy/hooks-examples.md`)
6. `git init && git checkout -b local`
7. Create branches: `git branch dev && git branch prod`
8. Start coding with Claude Code (`claude`) or OpenAI Codex (`codex`)

### Codex-specific Setup

For OpenAI Codex, optionally add to `~/.codex/config.toml`:

```toml
project_doc_fallback_filenames = ["CLAUDE.md"]
project_doc_max_bytes = 65536
```

### AGENTS.md for Codex

`AGENTS.md` is the main project instruction file for OpenAI Codex in this repository. It defines:

- response format and language rules
- project architecture and stack placeholders
- git workflow (`local -> dev -> prod`) and branch safety rules
- deploy constraints (DEV first, explicit confirmation for PROD)
- security requirements (`.env.*` never commit, no hardcoded secrets)
- available Codex skills in `.agents/skills/`

When Codex runs inside this repo, it reads `AGENTS.md` and uses it as the default operating contract.

### How This Repository Works with Codex

1. Open the repository in Codex CLI from the project root.
2. Codex reads `AGENTS.md` automatically and applies its workflow/safety rules.
3. Use built-in skills from `.agents/skills/` for routine tasks (`test`, `deploy-dev`, `docs`, `git-status`, etc.).
4. Keep day-to-day work in the `local` branch, then promote changes through `dev` and `prod`.
5. After deploy, follow the checklist from `AGENTS.md`: verify, update docs/status/changelog, and sync branches.

See [_specs/RECOMMENDED_SYSTEM.md](_specs/RECOMMENDED_SYSTEM.md) for the full setup guide.

## Author

Vadim Bakanov, creator of [Vibe-Commerce](https://vibecommerce.ru) — leveraging artificial intelligence in e-commerce.

## License

MIT
