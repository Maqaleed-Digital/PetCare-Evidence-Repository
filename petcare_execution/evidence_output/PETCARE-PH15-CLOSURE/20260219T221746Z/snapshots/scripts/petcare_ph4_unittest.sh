#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_LOG="${1:-/dev/stdout}"

cd "${REPO_ROOT}" || exit 1

PY="${REPO_ROOT}/.venv/bin/python"
if [ ! -x "${PY}" ]; then
  echo "FAIL: missing venv python at ${PY}"
  exit 2
fi

{
  echo "=============================================="
  echo "PetCare PH4 — Unittest Runner"
  echo "repo_root=${REPO_ROOT}"
  echo "timestamp_utc=$(date -u +%Y%m%dT%H%M%SZ)"
  echo "python=$(${PY} --version 2>&1)"
  echo "=============================================="
  echo ""
  "${PY}" -m unittest discover -s "TESTS" -p "test_*.py" -v
  echo ""
  echo "UNITTEST: PASS"
} 2>&1 | tee "${OUT_LOG}"
