#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WF="${REPO}/.github/workflows/ci.yml"

echo "=== REQUIRED CHECKS ASSERT ==="
echo "repo=${REPO}"
echo "workflow=${WF}"

if [ ! -f "${WF}" ]; then
  echo "FAIL: workflow missing: .github/workflows/ci.yml"
  exit 10
fi

need() {
  local pattern="$1"
  if ! grep -Fq "${pattern}" "${WF}"; then
    echo "FAIL: missing required pattern: ${pattern}"
    exit 11
  fi
  echo "PATTERN_OK=${pattern}"
}

# CI must run these gates
need "bash scripts/petcare_ci_gates.sh"
need "bash scripts/petcare_ph31_closure_pack.sh"
need "actions/upload-artifact"

# Determinism: lockfile-first installation
need "pip install -r requirements.lock"

echo "RESULT=PASS"
exit 0
