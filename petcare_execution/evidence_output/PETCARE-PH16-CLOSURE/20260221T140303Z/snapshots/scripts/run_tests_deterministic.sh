#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 1

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then PY_BIN=".venv/bin/python"; fi

exec env -u PYTEST_ADDOPTS -u PYTHONPATH "${PY_BIN}" -m pytest -q
