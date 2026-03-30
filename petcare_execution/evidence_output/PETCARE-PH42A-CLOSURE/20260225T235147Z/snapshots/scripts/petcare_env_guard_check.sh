#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

echo "=== PH42-A ENV GUARD CHECK ==="
echo "root=${ROOT}"

fail=0

echo ""
echo "=== CHECK: evidence_output must not be tracked ==="
if git ls-files | grep -q '^evidence_output/'; then
  echo "FAIL evidence_output is tracked by git"
  git ls-files | grep '^evidence_output/' | sed -n '1,120p'
  fail=1
else
  echo "PASS evidence_output not tracked"
fi

echo ""
echo "=== CHECK: .env files must not be tracked ==="
if git ls-files | grep -E -q '(^|/)\.env($|[^/])|(^|/)\.env\.|(^|/)env\.|(^|/)\.envrc$'; then
  echo "FAIL env files tracked"
  git ls-files | grep -E '(^|/)\.env($|[^/])|(^|/)\.env\.|(^|/)env\.|(^|/)\.envrc$' | sed -n '1,120p'
  fail=1
else
  echo "PASS no env files tracked"
fi

echo ""
echo "=== CHECK: obvious secret patterns in tracked files (heuristic) ==="
patterns='(BEGIN[[:space:]]+PRIVATE[[:space:]]+KEY|AWS_SECRET_ACCESS_KEY|AKIA[0-9A-Z]{16}|xox[baprs]-|ghp_[A-Za-z0-9]{20,}|-----BEGIN)'
hits="$(git grep -nE "${patterns}" -- . 2>/dev/null || true)"
if [ -n "${hits}" ]; then
  echo "FAIL secret-like patterns detected in tracked files"
  echo "${hits}" | sed -n '1,120p'
  fail=1
else
  echo "PASS no obvious secret patterns found"
fi

echo ""
echo "=== CHECK: CI workflows should not reference PROD secrets (heuristic) ==="
if [ -d ".github/workflows" ]; then
  wf_hits="$(git grep -nE '(PROD_SECRET|PROD_|PRODUCTION_|VAULT_PROD|KMS_PROD)' -- ".github/workflows" 2>/dev/null || true)"
  if [ -n "${wf_hits}" ]; then
    echo "WARN found prod-like tokens in workflows (review required)"
    echo "${wf_hits}" | sed -n '1,160p'
  else
    echo "PASS no prod-like tokens found in workflows"
  fi
else
  echo "WARN missing .github/workflows directory"
fi

echo ""
if [ "${fail}" -ne 0 ]; then
  echo "ENV_GUARD_RESULT=FAIL"
  exit 1
fi

echo "ENV_GUARD_RESULT=PASS"
