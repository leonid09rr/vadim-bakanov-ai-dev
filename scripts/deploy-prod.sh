#!/bin/bash
set -e

# Deploy to PROD environment
# Usage: ./scripts/deploy-prod.sh
#
# SAFETY: This script should only be run after DEV has been tested!
#
# CUSTOMIZE: Update variables below for your project

# ══════════════════════════════════════════
# CONFIGURATION — edit these for your project
# ══════════════════════════════════════════

VPS_HOST="{your-vps-host}"           # SSH host from ~/.ssh/config
VPS_APP_DIR="/home/{user}/{project}-prod"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"
CONTAINER_APP="{project}-prod-app"
CONTAINER_PG="{project}-prod-postgres"
BACKUP_DIR="/home/{user}/backups/prod"
HEALTH_URL="https://{YOUR_DOMAIN}/api/health"

# ══════════════════════════════════════════
# ENGINE — no changes needed below
# ══════════════════════════════════════════

echo "=== Deploy to PROD ==="
echo ""
echo "WARNING: You are deploying to PRODUCTION!"
echo "Make sure DEV has been tested first."
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
  echo "ERROR: .env not found on VPS at $VPS_APP_DIR/.env"
  exit 1
fi
echo "  .env found on VPS"

# Check disk space on VPS (warn if < 2GB free for PROD)
FREE_KB=$(ssh "$VPS_HOST" "df $VPS_APP_DIR --output=avail 2>/dev/null | tail -1 | tr -d ' '" 2>/dev/null || echo "0")
if [ "$FREE_KB" != "0" ]; then
  FREE_MB=$((FREE_KB / 1024))
  if [ "$FREE_KB" -lt 2097152 ]; then
    echo "  WARNING: Only ${FREE_MB}MB free on VPS (< 2GB)"
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
    docker exec $CONTAINER_PG pg_dump -U postgres postgres 2>/dev/null | gzip > "$BACKUP_DIR/prod-\${TIMESTAMP}.sql.gz"
    echo "  Backup saved: prod-\${TIMESTAMP}.sql.gz"
    # Keep last 30 backups for PROD
    ls -t "$BACKUP_DIR"/prod-*.sql.gz 2>/dev/null | tail -n +31 | xargs rm -f 2>/dev/null
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
for i in $(seq 1 30); do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$HEALTH_URL" 2>/dev/null) || HTTP_CODE="000"
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
"$PROJECT_DIR/scripts/smoke-test.sh" prod

echo ""
echo "=== Deploy to PROD complete ==="
