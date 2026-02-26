#!/bin/bash
set -e

# Deploy to DEV environment
# Usage: ./scripts/deploy-dev.sh
#
# CUSTOMIZE: Update variables below for your project

# ══════════════════════════════════════════
# CONFIGURATION — edit these for your project
# ══════════════════════════════════════════

VPS_HOST="{your-vps-host}"           # SSH host from ~/.ssh/config
VPS_APP_DIR="/home/{user}/{project}-dev"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="docker-compose.dev.yml"
CONTAINER_APP="{project}-dev-app"
CONTAINER_PG="{project}-dev-postgres"
BACKUP_DIR="/home/{user}/backups/dev"
HEALTH_URL="https://dev.{YOUR_DOMAIN}/api/health"
# SMOKE_AUTH="user:password"          # Uncomment if DEV uses Basic Auth

# ══════════════════════════════════════════
# ENGINE — no changes needed below
# ══════════════════════════════════════════

echo "=== Deploy to DEV ==="
echo ""

# --- Pre-deploy checks ---
echo "--- Pre-deploy checks ---"

# Check VPS connectivity
if ! ssh -o ConnectTimeout=5 "$VPS_HOST" "echo 'ok'" > /dev/null 2>&1; then
  echo "ERROR: Cannot connect to VPS ($VPS_HOST)"
  exit 1
fi
echo "  VPS reachable"

# Check .env exists on VPS
if ! ssh "$VPS_HOST" "test -f $VPS_APP_DIR/.env" 2>/dev/null; then
  echo "  WARNING: .env not found on VPS at $VPS_APP_DIR/.env"
  echo "  First deploy? Create .env on VPS before deploying."
fi

# Check disk space on VPS (warn if < 1GB free)
FREE_KB=$(ssh "$VPS_HOST" "df $VPS_APP_DIR --output=avail 2>/dev/null | tail -1 | tr -d ' '" 2>/dev/null || echo "0")
if [ "$FREE_KB" != "0" ]; then
  FREE_MB=$((FREE_KB / 1024))
  if [ "$FREE_KB" -lt 1048576 ]; then
    echo "  WARNING: Only ${FREE_MB}MB free on VPS (< 1GB)"
  else
    echo "  Disk space: ${FREE_MB}MB free"
  fi
fi

echo "Pre-deploy checks passed."
echo ""

# --- Pre-deploy DB backup ---
echo "--- Creating database backup ---"
ssh "$VPS_HOST" << ENDSSH
  mkdir -p $BACKUP_DIR
  TIMESTAMP=\$(date +%Y%m%d_%H%M%S)

  if docker ps --format '{{.Names}}' | grep -q "$CONTAINER_PG"; then
    docker exec $CONTAINER_PG pg_dump -U postgres postgres 2>/dev/null | gzip > "$BACKUP_DIR/dev-\${TIMESTAMP}.sql.gz"
    echo "  Backup saved: dev-\${TIMESTAMP}.sql.gz"
    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/dev-*.sql.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
  else
    echo "  No running postgres container — skipping backup (first deploy?)"
  fi
ENDSSH
echo ""

# --- Rsync project to VPS ---
echo "--- Syncing project to VPS ---"
for attempt in 1 2 3; do
  if rsync -avz --delete \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='.env.*' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='build' \
    --exclude='dist' \
    --exclude='.react-router' \
    --exclude='.claude/settings.local.json' \
    "$PROJECT_DIR/" "$VPS_HOST:$VPS_APP_DIR/"; then
    break
  fi
  echo "  Rsync attempt $attempt failed. Retrying in $((attempt * 5))s..."
  sleep $((attempt * 5))
  if [ "$attempt" -eq 3 ]; then
    echo "ERROR: rsync failed after 3 attempts"
    exit 1
  fi
done
echo "Project synced."

# --- Build and start Docker containers ---
echo ""
echo "--- Building and starting containers ---"
ssh "$VPS_HOST" << ENDSSH
  cd $VPS_APP_DIR
  docker compose -f $COMPOSE_FILE build
  docker compose -f $COMPOSE_FILE up -d --force-recreate
  echo ""
  echo "--- Container status ---"
  docker compose -f $COMPOSE_FILE ps
ENDSSH

# --- Wait for app to be healthy ---
echo ""
echo "--- Waiting for app to be healthy ---"
CURL_AUTH=""
if [ -n "${SMOKE_AUTH:-}" ]; then
  CURL_AUTH="-u $SMOKE_AUTH"
fi

for i in $(seq 1 30); do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $CURL_AUTH --max-time 5 "$HEALTH_URL" 2>/dev/null) || HTTP_CODE="000"
  if [ "$HTTP_CODE" = "200" ]; then
    echo "  App is ready (attempt $i)"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "  WARNING: App not ready after 60s (last HTTP: $HTTP_CODE)"
  else
    echo "  Waiting... (attempt $i, HTTP $HTTP_CODE)"
    sleep 2
  fi
done

# --- Run smoke test ---
echo ""
echo "--- Running smoke test ---"
if [ -n "${SMOKE_AUTH:-}" ]; then
  "$PROJECT_DIR/scripts/smoke-test.sh" dev "$SMOKE_AUTH"
else
  "$PROJECT_DIR/scripts/smoke-test.sh" dev
fi

echo ""
echo "=== Deploy to DEV complete ==="
