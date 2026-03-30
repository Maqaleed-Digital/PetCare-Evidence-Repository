#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PY_BIN=".venv/bin/python"
fi

TARGET="${1:-}"
if [ -z "${TARGET}" ]; then
  if [ -d "TESTS" ]; then
    TARGET="TESTS"
  elif [ -d "tests" ]; then
    TARGET="tests"
  else
    echo "ERROR: no TESTS/ or tests/ directory found"
    exit 4
  fi
fi

env -u PYTEST_ADDOPTS -u PYTHONPATH "${PY_BIN}" -m pytest -q "${TARGET}"
