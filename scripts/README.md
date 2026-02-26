# Scripts

Operational scripts for deployment, testing, and VPS management.

| Script | Description | Usage |
|--------|-------------|-------|
| `smoke-test.sh` | HTTP smoke test (6 categories) | `./scripts/smoke-test.sh [local\|dev\|prod]` |
| `deploy-dev.sh` | Deploy to DEV with safety checks | `./scripts/deploy-dev.sh` |
| `deploy-prod.sh` | Deploy to PROD with safety checks | `./scripts/deploy-prod.sh` |
| `connect-vps.sh` | VPS management (logs, shell, status) | `./scripts/connect-vps.sh [command]` |

## Customization

All scripts have a `CONFIGURATION` section at the top. Replace `{placeholders}` with your project values:
- `{YOUR_DOMAIN}` — your domain
- `{your-vps-host}` — SSH host from `~/.ssh/config`
- `{project}` — project name
- `{user}` — VPS username
