# Claude Code Project Template

Ready-to-use project scaffold with pre-configured Claude Code skills, agents, rules, and deployment infrastructure.

## What's Inside

### AI Brain (`.claude/`)
- **13 skills** -- slash commands for git, deploy, testing, architecture, project management
- **3 agents** -- deployer, test-runner, docs-generator
- **2 rules** -- error-learning, auto-backup
- **Hooks** -- auto-linting on file write (Python/ruff)

### Documentation Infrastructure
- **CLAUDE.md** -- master instructions (project rules, stack, workflow)
- **AGENDA.md** -- working session memory (current focus, next steps)
- **_status/** -- environment state tracking (DEV/PROD)
- **_changelogs/** -- release history
- **_specs/** -- specifications + templates (user-spec, tech-spec, task)
- **backlog/** -- task management
- **documentation/** -- architecture docs, error registry

### Deployment Templates (`deploy/`)
- **Dockerfiles** -- Python (3.11-slim + non-root + healthcheck) and Node.js (multi-stage)
- **docker-compose** -- DEV (dev-friendly) and PROD (logging, always-restart)
- **Nginx configs** -- DEV (Basic Auth + API bypass) and PROD (HSTS, caching, security headers)
- **pyproject.toml** -- Python project config (ruff, pytest, dependency groups)
- **Hooks examples** -- PostToolUse for Python, TypeScript, Astro

### Operational Scripts (`scripts/`)
- **smoke-test.sh** -- 6-category HTTP smoke test (connectivity, headers, HTML, routes, assets, API)
- **deploy-dev.sh** -- Pre-checks, DB backup, rsync, docker build, health polling, smoke test
- **deploy-prod.sh** -- Same as DEV + safety warnings, 30 backup retention
- **connect-vps.sh** -- SSH master script (shell, logs, status, restart, postgres, redis)

## Skills (Slash Commands)

| Command | Description |
|---------|-------------|
| `/commit` | AI-generated commit messages (conventional commits) |
| `/push` | Safe push with preview and confirmation |
| `/cherry-pick` | Transfer commits: local -> dev |
| `/merge-to-prod` | Merge dev -> prod (requires confirmation) |
| `/git-status` | Multi-branch status overview |
| `/deploy-dev` | Deploy to DEV environment |
| `/deploy-prod` | Deploy to PROD (with safety checklist) |
| `/test` | Run lint, types, unit tests, build |
| `/docs` | Update documentation after deploy |
| `/techdebt` | Scan for technical debt |
| `/architect` | Architecture analysis and planning |
| `/project-manager` | Backlog, sprints, priorities |

## Git Workflow

```
local (development) -> cherry-pick -> dev (testing) -> merge -> prod (production)
```

## Quick Start

1. Clone/copy this template
2. Fill in `{placeholders}` in `CLAUDE.md` (project name, stack, URLs)
3. Fill in `{placeholders}` in `scripts/*.sh` (VPS host, domain, paths)
4. Copy relevant files from `deploy/` to project root (Dockerfile, docker-compose, nginx)
5. Adapt `.claude/settings.json` hooks for your stack (see `deploy/hooks-examples.md`)
6. `git init && git checkout -b local`
7. Create branches: `git branch dev && git branch prod`
8. Start coding

See [_specs/RECOMMENDED_SYSTEM.md](_specs/RECOMMENDED_SYSTEM.md) for the full setup guide.

## License

MIT
