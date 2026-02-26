# Deploy Templates

Templates for deployment infrastructure. Copy to project root and customize.

## Contents

| Directory/File | Description |
|---------------|-------------|
| `docker/Dockerfile.python` | Multi-stage Dockerfile for Python apps |
| `docker/Dockerfile.node` | Multi-stage Dockerfile for Node.js apps |
| `docker/docker-compose.dev.yml` | DEV environment (PG + Redis + App) |
| `docker/docker-compose.prod.yml` | PROD environment (with logging + always restart) |
| `docker/pyproject.toml.template` | Python project config (ruff, pytest, deps) |
| `nginx/dev.conf` | Nginx DEV config (Basic Auth + proxy) |
| `nginx/prod.conf` | Nginx PROD config (HSTS + caching + security) |
| `hooks-examples.md` | PostToolUse hooks for Python, TS, Astro |

## Quick Setup

1. Copy relevant Dockerfile to project root as `Dockerfile`
2. Copy docker-compose files to project root
3. Copy nginx configs to VPS `/etc/nginx/sites-available/`
4. Replace all `{placeholders}` with your values
5. Set up SSL: `sudo certbot --nginx -d your-domain.com`

## Key Differences: DEV vs PROD

| Aspect | DEV | PROD |
|--------|-----|------|
| restart | `unless-stopped` | `always` |
| logging | default | json-file with rotation |
| auth | Basic Auth | none (public) |
| caching | disabled | 30d for static |
| HSTS | no | yes |
| backups | keep 10 | keep 30 |
