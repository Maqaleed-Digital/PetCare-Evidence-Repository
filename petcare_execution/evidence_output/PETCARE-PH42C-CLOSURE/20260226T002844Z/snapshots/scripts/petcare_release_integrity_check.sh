#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

echo "=== RELEASE INTEGRITY CHECK ==="
echo "repo=${ROOT}"

fail=0

echo ""
echo "=== CHECK: governance drift ==="
if [ -x "${ROOT}/scripts/petcare_policy_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_policy_drift_check.sh" || fail=1
else
  echo "MISSING=scripts/petcare_policy_drift_check.sh"
  fail=1
fi

if [ -x "${ROOT}/scripts/petcare_registry_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_registry_drift_check.sh" || fail=1
else
  echo "MISSING=scripts/petcare_registry_drift_check.sh"
  fail=1
fi

echo ""
echo "=== CHECK: lock determinism ==="
if [ -x "${ROOT}/scripts/petcare_lock_verify.sh" ]; then
  bash "${ROOT}/scripts/petcare_lock_verify.sh" || fail=1
else
  echo "MISSING=scripts/petcare_lock_verify.sh"
  fail=1
fi

echo ""
echo "=== CHECK: evidence_output must not be tracked ==="
if git ls-files | grep -qE '^evidence_output/'; then
  echo "FAIL evidence_output tracked"
  fail=1
else
  echo "PASS evidence_output not tracked"
fi

echo ""
echo "=== CHECK: env files must not be tracked ==="
if git ls-files | grep -qE '(^|/)\.env($|[^/])|(^|/)\.env\.|(^|/)env\.|(^|/)\.envrc$'; then
  echo "FAIL env files tracked"
  fail=1
else
  echo "PASS no env files tracked"
fi

echo ""
echo "=== CHECK: obvious secret patterns in tracked files (heuristic) ==="
if git grep -nE '(AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH) PRIVATE KEY|xox[baprs]-|-----BEGIN PRIVATE KEY-----|SECRET_KEY=|API_KEY=|PASSWORD=|TOKEN=)' -- . >/dev/null 2>&1; then
  echo "FAIL secret heuristic hit"
  fail=1
else
  echo "PASS no obvious secret patterns found"
fi

echo ""
echo "=== CHECK: workflows should not reference prod secrets (heuristic) ==="
if git grep -nE '(PROD_SECRET|PROD_|PRODUCTION_|VAULT_PROD|KMS_PROD)' -- ".github/workflows" >/dev/null 2>&1; then
  echo "FAIL prod-like tokens in workflows"
  fail=1
else
  echo "PASS no prod-like tokens found in workflows"
fi

if [ "${fail}" -eq 0 ]; then
  echo ""
  echo "RELEASE_INTEGRITY_RESULT=PASS"
  exit 0
fi

echo ""
echo "RELEASE_INTEGRITY_RESULT=FAIL"
exit 1
