#!/usr/bin/env bash
set -euo pipefail

PH="${1:-}"

if [ -z "${PH}" ]; then
  echo "USAGE: bash scripts/petcare_increment_close.sh PH21"
  exit 2
fi

ROOT="$(pwd)"
VENV_PY="${ROOT}/.venv/bin/python"

PH_LC="$(printf "%s" "${PH}" | tr '[:upper:]' '[:lower:]')"
CLOSURE_SCRIPT="${ROOT}/scripts/petcare_${PH_LC}_closure_pack.sh"

echo "=== INCREMENT CLOSE ==="
echo "ROOT=${ROOT}"
echo "PH=${PH}"
echo "CLOSURE_SCRIPT=${CLOSURE_SCRIPT}"

echo ""
echo "=== GUARDRAIL CHECK ==="
bash "${ROOT}/scripts/petcare_emergent_guardrail_check.sh"

echo ""
echo "=== PYTEST (VENV) ==="
if [ ! -x "${VENV_PY}" ]; then
  echo "MISSING_VENV_PY=${VENV_PY}"
  exit 3
fi
"${VENV_PY}" -m pytest -q

echo ""
echo "=== CLOSURE PACK ==="
if [ ! -x "${CLOSURE_SCRIPT}" ]; then
  echo "MISSING_CLOSURE_SCRIPT=${CLOSURE_SCRIPT}"
  echo "ACTION: Create the phase closure script first (example: scripts/petcare_ph21_closure_pack.sh)."
  exit 4
fi
bash "${CLOSURE_SCRIPT}"
