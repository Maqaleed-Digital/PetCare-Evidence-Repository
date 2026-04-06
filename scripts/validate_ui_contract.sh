#!/usr/bin/env bash
set -euo pipefail

: "${WEB_ROOT:?Missing WEB_ROOT}"
: "${API_BASE_URL:?Missing API_BASE_URL}"
: "${AUTH_MODE:?Missing AUTH_MODE}"
: "${AUTH_ISSUER:?Missing AUTH_ISSUER}"
: "${AUTH_AUDIENCE:?Missing AUTH_AUDIENCE}"
: "${SESSION_SECRET:?Missing SESSION_SECRET}"
: "${AUDIT_PROBE_ENDPOINT:?Missing AUDIT_PROBE_ENDPOINT}"

test -f "$WEB_ROOT/package.json"
test -f "$WEB_ROOT/Dockerfile"
test -f "$WEB_ROOT/app/api/health/route.ts"
test -f "$WEB_ROOT/middleware.ts"

curl -fsS "${API_BASE_URL%/}/health" >/dev/null

if [[ "$AUTH_MODE" != "jwt" && "$AUTH_MODE" != "iap" ]]; then
  echo "AUTH_MODE invalid"
  exit 1
fi

if [[ "${#SESSION_SECRET}" -lt 16 ]]; then
  echo "SESSION_SECRET too short"
  exit 1
fi

curl -fsS -X POST "$AUDIT_PROBE_ENDPOINT" \
  -H 'content-type: application/json' \
  -d '{"event_name":"ui.audit.probe","actor_role":"admin","surface":"predeploy","correlation_id":"contract-check"}' >/dev/null

echo "UI contract validation passed"
