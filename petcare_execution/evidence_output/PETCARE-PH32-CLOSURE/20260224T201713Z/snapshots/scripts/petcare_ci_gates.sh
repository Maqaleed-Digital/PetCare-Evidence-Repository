#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO}"

PY="${REPO}/.venv/bin/python"
if [ ! -x "${PY}" ]; then
  echo "FAIL: venv python missing: ${PY}"
  echo "HINT: create .venv and install deps before running CI gates"
  exit 2
fi

echo "=== CI GATES ==="
echo "repo=${REPO}"
echo "python=${PY}"

echo ""
echo "=== GATE 1: Python version ==="
"${PY}" -V

echo ""
echo "=== GATE 2: Dependency sanity (pip check) ==="
set +e
"${PY}" -m pip check | tee "evidence_output/_ci_pip_check.log"
RC_PIP=${PIPESTATUS[0]}
set -e
if [ "${RC_PIP}" -ne 0 ]; then
  echo "FAIL: pip check failed rc=${RC_PIP}"
  exit 10
fi

echo ""
echo "=== GATE 3: Syntax check (compileall) ==="
set +e
"${PY}" -m compileall -q . | tee "evidence_output/_ci_compileall.log"
RC_COMP=${PIPESTATUS[0]}
set -e
if [ "${RC_COMP}" -ne 0 ]; then
  echo "FAIL: compileall failed rc=${RC_COMP}"
  exit 11
fi

echo ""
echo "=== GATE 4: Unit tests (pytest) ==="
set +e
"${PY}" -m pytest --version | tee "evidence_output/_ci_pytest_version.log"
RC_VER=${PIPESTATUS[0]}
set -e
if [ "${RC_VER}" -ne 0 ]; then
  echo "FAIL: pytest --version failed rc=${RC_VER}"
  exit 12
fi

echo ""
echo "RUN=pytest -q"
set +e
"${PY}" -m pytest -q | tee "evidence_output/_ci_pytest_run.log"
RC_TEST=${PIPESTATUS[0]}
set -e
if [ "${RC_TEST}" -ne 0 ]; then
  echo "FAIL: pytest run failed rc=${RC_TEST}"
  exit 13
fi

echo ""
echo "RESULT=PASS"
