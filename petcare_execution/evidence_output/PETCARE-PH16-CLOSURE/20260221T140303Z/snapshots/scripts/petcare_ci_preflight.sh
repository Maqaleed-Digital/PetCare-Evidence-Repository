#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PY_BIN=".venv/bin/python"
fi

echo "=== CI PREFLIGHT ==="
echo "repo_root=${REPO_ROOT}"
echo "python_bin=${PY_BIN}"
command -v "${PY_BIN}" || true
"${PY_BIN}" -V || true

test -f "pytest.ini" || { echo "MISSING pytest.ini"; exit 4; }

"${PY_BIN}" -m compileall -q .

echo "PREFLIGHT_OK"
