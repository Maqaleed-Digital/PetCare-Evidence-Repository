#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "DF07_POST_DEPLOY_VERIFY: FAIL - $1" >&2
  exit 1
}

: "${PETCARE_VERIFY_URL:?PETCARE_VERIFY_URL is required}"

PETCARE_VERIFY_HEALTH_PATH="${PETCARE_VERIFY_HEALTH_PATH:-/health}"
PETCARE_VERIFY_READY_PATH="${PETCARE_VERIFY_READY_PATH:-/ready}"
PETCARE_EXPECT_HTTP_CODE="${PETCARE_EXPECT_HTTP_CODE:-200}"

health_url="${PETCARE_VERIFY_URL%/}${PETCARE_VERIFY_HEALTH_PATH}"
ready_url="${PETCARE_VERIFY_URL%/}${PETCARE_VERIFY_READY_PATH}"

health_code="$(curl -sS -o /dev/null -w "%{http_code}" "$health_url" || true)"
ready_code="$(curl -sS -o /dev/null -w "%{http_code}" "$ready_url" || true)"

[ "$health_code" = "$PETCARE_EXPECT_HTTP_CODE" ] || fail "health endpoint returned ${health_code}, expected ${PETCARE_EXPECT_HTTP_CODE}"
[ "$ready_code" = "$PETCARE_EXPECT_HTTP_CODE" ] || fail "ready endpoint returned ${ready_code}, expected ${PETCARE_EXPECT_HTTP_CODE}"

echo "DF07_POST_DEPLOY_VERIFY: PASS"
echo "verify_url=${PETCARE_VERIFY_URL}"
echo "health_url=${health_url}"
echo "ready_url=${ready_url}"
echo "expected_http_code=${PETCARE_EXPECT_HTTP_CODE}"
