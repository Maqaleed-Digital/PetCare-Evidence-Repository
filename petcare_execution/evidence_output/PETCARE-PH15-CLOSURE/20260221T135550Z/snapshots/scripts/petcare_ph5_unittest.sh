#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PY="${REPO_ROOT}/.venv/bin/python"
if [ -x "${PY}" ]; then
  :
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "FAIL: python not found"
  exit 2
fi

echo "PH5 UNITTEST"
echo "repo_root=${REPO_ROOT}"
echo "python=$(${PY} --version 2>&1)"

"${PY}" -m unittest discover -s "TESTS" -p "test_*.py" -v
