# Claude Code Project Template

Ready-to-use project scaffold with pre-configured Claude Code skills, agents, rules, and documentation infrastructure.

## What's Inside

- **CLAUDE.md** -- master instructions for Claude Code (project rules, stack, workflow)
- **.claude/** -- AI brain: 12 skills, 3 agents, 2 rules, hooks
- **_status/** -- environment state tracking (DEV/PROD)
- **_changelogs/** -- release history
- **_specs/** -- specifications and blueprints
- **backlog/** -- task management
- **documentation/** -- architecture docs, error registry

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
3. Adapt `.claude/settings.json` hooks for your stack
4. `git init && git checkout -b local`
5. Create branches: `git branch dev && git branch prod`
6. Start coding

See [_specs/RECOMMENDED_SYSTEM.md](_specs/RECOMMENDED_SYSTEM.md) for the full setup guide.

## License

MIT
