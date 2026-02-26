#!/bin/bash
# smoke-test.sh — Universal HTTP smoke test
# Usage: ./scripts/smoke-test.sh [dev|prod|local]
# Usage with auth: ./scripts/smoke-test.sh dev user:password
#
# Checks: HTTP status, response time, headers, HTML, key routes, static assets, API health
#
# CUSTOMIZE: Update BASE_URL, ROUTES, and API health endpoint for your project

ENV="${1:-local}"
AUTH="${2:-}"

# ══════════════════════════════════════════
# CONFIGURATION — edit these for your project
# ══════════════════════════════════════════

case "$ENV" in
  local) BASE_URL="http://localhost:3000" ;;
  dev)   BASE_URL="https://dev.{YOUR_DOMAIN}" ;;
  prod)  BASE_URL="https://{YOUR_DOMAIN}" ;;
  *)     echo "Usage: $0 [local|dev|prod] [user:password]"; exit 1 ;;
esac

# Routes to check (add your own)
ROUTES=("/" "/api/health")
# Add routes as app grows:
# ROUTES+=("/login" "/dashboard" "/about")

# ══════════════════════════════════════════
# ENGINE — no changes needed below
# ══════════════════════════════════════════

CURL_OPTS="--max-time 10 -s"
if [ -n "$AUTH" ]; then
  CURL_OPTS="$CURL_OPTS -u $AUTH"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass() { echo -e "  ${GREEN}✓${NC} $1"; PASS=$((PASS + 1)); }
fail() { echo -e "  ${RED}✗${NC} $1"; FAIL=$((FAIL + 1)); }
warn() { echo -e "  ${YELLOW}!${NC} $1"; WARN=$((WARN + 1)); }

echo "==========================================="
echo " Smoke Test — $ENV ($BASE_URL)"
echo "==========================================="
echo ""

# --- 1. Basic connectivity ---
echo "> Connectivity"
HTTP_CODE=$(curl $CURL_OPTS -o /dev/null -w "%{http_code}" "$BASE_URL/" 2>/dev/null) || HTTP_CODE="000"
RESPONSE_TIME=$(curl $CURL_OPTS -o /dev/null -w "%{time_total}" "$BASE_URL/" 2>/dev/null) || RESPONSE_TIME="0"

if [ "$HTTP_CODE" = "200" ]; then
  pass "Homepage returns 200"
elif [ "$HTTP_CODE" = "000" ]; then
  fail "Cannot connect to $BASE_URL"
  echo ""
  echo "Result: Cannot reach server. Aborting."
  exit 1
elif [ "$HTTP_CODE" = "401" ]; then
  fail "Homepage returns 401 (auth required — use: $0 $ENV user:password)"
  echo ""
  echo "Hint: Pass basic auth credentials as second argument."
  exit 1
else
  warn "Homepage returns $HTTP_CODE (expected 200)"
fi

# Response time check (awk for macOS compatibility)
SLOW=$(echo "$RESPONSE_TIME" | awk '{print ($1 >= 2.0)}')
VERY_SLOW=$(echo "$RESPONSE_TIME" | awk '{print ($1 >= 5.0)}')

if [ "$VERY_SLOW" = "1" ]; then
  fail "Response time: ${RESPONSE_TIME}s (very slow, > 5s)"
elif [ "$SLOW" = "1" ]; then
  warn "Response time: ${RESPONSE_TIME}s (slow, > 2s)"
else
  pass "Response time: ${RESPONSE_TIME}s (< 2s)"
fi

# --- 2. Response headers ---
echo ""
echo "> Headers"
HEADERS=$(curl $CURL_OPTS -I "$BASE_URL/" 2>/dev/null)

if echo "$HEADERS" | grep -qi "content-type"; then
  pass "Content-Type header present"
else
  fail "Missing Content-Type header"
fi

if echo "$HEADERS" | grep -qi "x-powered-by"; then
  warn "X-Powered-By header exposed (consider removing)"
else
  pass "X-Powered-By not exposed"
fi

if [ "$ENV" != "local" ]; then
  if echo "$HEADERS" | grep -qi "strict-transport-security"; then
    pass "HSTS header present"
  else
    warn "HSTS header missing"
  fi
fi

# --- 3. HTML content check ---
echo ""
echo "> HTML Content"
HTML=$(curl $CURL_OPTS "$BASE_URL/" 2>/dev/null)

if echo "$HTML" | grep -qi "<html"; then
  pass "Valid HTML document"
else
  # Might be JSON API — not necessarily a failure
  if echo "$HTML" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    pass "Valid JSON response (API mode)"
  else
    warn "Response is neither HTML nor JSON"
  fi
fi

if echo "$HTML" | grep -qi "<title>"; then
  TITLE=$(echo "$HTML" | grep -oi '<title>[^<]*</title>' | head -1 | sed 's/<[^>]*>//g')
  if [ -n "$TITLE" ]; then
    pass "Page title: $TITLE"
  else
    warn "Empty <title> tag"
  fi
fi

# Check for error indicators
if echo "$HTML" | grep -qi "500\|internal server error\|application error\|unexpected error"; then
  fail "Server error detected in response body"
else
  pass "No server errors in response"
fi

# --- 4. Key routes ---
echo ""
echo "> Key Routes"

for ROUTE in "${ROUTES[@]}"; do
  CODE=$(curl $CURL_OPTS -o /dev/null -w "%{http_code}" "${BASE_URL}${ROUTE}" 2>/dev/null) || CODE="000"
  if [ "$CODE" = "200" ] || [ "$CODE" = "302" ] || [ "$CODE" = "301" ]; then
    pass "${ROUTE} -> ${CODE}"
  elif [ "$CODE" = "000" ]; then
    fail "${ROUTE} -> connection failed"
  elif [ "$CODE" = "404" ]; then
    warn "${ROUTE} -> 404 (not implemented yet?)"
  else
    warn "${ROUTE} -> ${CODE}"
  fi
done

# --- 5. Static assets ---
echo ""
echo "> Static Assets"

CSS_LINKS=$(echo "$HTML" | grep -o 'href="[^"]*\.css[^"]*"' | head -3 | sed 's/href="//;s/"$//')
JS_LINKS=$(echo "$HTML" | grep -o 'src="[^"]*\.js[^"]*"' | head -3 | sed 's/src="//;s/"$//')

ASSET_CHECKED=0
for ASSET in $CSS_LINKS $JS_LINKS; do
  if [ -z "$ASSET" ]; then continue; fi

  if echo "$ASSET" | grep -q "^/"; then
    ASSET_URL="${BASE_URL}${ASSET}"
  elif echo "$ASSET" | grep -q "^http"; then
    ASSET_URL="$ASSET"
  else
    ASSET_URL="${BASE_URL}/${ASSET}"
  fi

  ACODE=$(curl $CURL_OPTS -o /dev/null -w "%{http_code}" "$ASSET_URL" 2>/dev/null) || ACODE="000"
  ASSET_SHORT=$(echo "$ASSET" | sed 's/.*\///' | cut -c1-40)
  if [ "$ACODE" = "200" ]; then
    pass "Asset: $ASSET_SHORT -> 200"
  else
    fail "Asset: $ASSET_SHORT -> $ACODE"
  fi
  ASSET_CHECKED=$((ASSET_CHECKED + 1))
  [ "$ASSET_CHECKED" -ge 4 ] && break
done

if [ "$ASSET_CHECKED" -eq 0 ]; then
  warn "No CSS/JS assets found to check (API-only app?)"
fi

# --- 6. API health (non-local only) ---
if [ "$ENV" != "local" ]; then
  echo ""
  echo "> API Health"
  API_CODE=$(curl $CURL_OPTS -o /dev/null -w "%{http_code}" "${BASE_URL}/api/health" 2>/dev/null) || API_CODE="000"
  if [ "$API_CODE" = "200" ]; then
    pass "API /api/health -> 200"
  elif [ "$API_CODE" = "000" ]; then
    warn "API /api/health -> connection failed"
  elif [ "$API_CODE" = "404" ]; then
    warn "API /api/health -> 404 (endpoint not yet implemented)"
  else
    warn "API /api/health -> $API_CODE"
  fi
fi

# --- Summary ---
echo ""
echo "==========================================="
TOTAL=$((PASS + FAIL + WARN))
echo -e " Results: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}, ${YELLOW}${WARN} warnings${NC} (${TOTAL} checks)"

if [ "$FAIL" -gt 0 ]; then
  echo -e " Status: ${RED}FAIL${NC}"
  exit 1
elif [ "$WARN" -gt 0 ]; then
  echo -e " Status: ${YELLOW}WARN${NC}"
  exit 0
else
  echo -e " Status: ${GREEN}PASS${NC}"
  exit 0
fi
