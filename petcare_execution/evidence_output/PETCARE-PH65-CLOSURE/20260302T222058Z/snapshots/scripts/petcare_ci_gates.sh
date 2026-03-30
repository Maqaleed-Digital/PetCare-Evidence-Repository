#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${REPO}/.venv/bin/python"

echo "=== CI GATES ==="
echo "repo=${REPO}"
echo "python=${PY}"

if [ ! -x "${PY}" ]; then
  echo "FAIL: venv python missing at ${PY}"
  exit 10
fi

echo ""
echo "=== GATE 0: Workflow required steps assert ==="
bash "${REPO}/scripts/petcare_required_checks_assert.sh"

echo ""
echo "=== GATE 0b: Policy drift check ==="
bash "${REPO}/scripts/petcare_policy_drift_check.sh"

echo ""
echo "=== GATE 0c: Registry drift check ==="
bash "${REPO}/scripts/petcare_registry_drift_check.sh"

echo ""
echo "=== GATE 1: Python version ==="
"${PY}" -V

echo ""
echo "=== GATE 2: Dependency sanity (pip check) ==="
"${PY}" -m pip check

echo ""
echo "=== GATE 3: Syntax check (compileall) ==="
"${PY}" -m compileall -q "${REPO}"

echo ""
echo "=== GATE 4: Unit tests (pytest) ==="
"${PY}" -m pytest --version
echo ""
echo "RUN=pytest -q"
"${PY}" -m pytest -q

echo ""
echo "=== GATE 5: Lockfile determinism (requirements.lock) ==="
bash "${REPO}/scripts/petcare_lock_verify.sh"

echo ""
echo "=== GATE 6: Evidence size guard ==="
# Default max is 4096MB. Override as needed:
# MAX_MB=2048 bash scripts/petcare_ci_gates.sh
bash "${REPO}/scripts/petcare_evidence_size_guard.sh"

echo ""
echo "=== GATE: verification index generation (drift) ==="
python3 "${REPO}/scripts/petcare_verification_index_generate.py" --check --ts_utc "$(date -u +%Y%m%dT%H%M%SZ)"

echo ""
echo "=== GATE: verification index quorum ==="
bash "${REPO}/scripts/petcare_verification_index_quorum_guard.sh"

echo ""
echo "RESULT=PASS"
exit 0
