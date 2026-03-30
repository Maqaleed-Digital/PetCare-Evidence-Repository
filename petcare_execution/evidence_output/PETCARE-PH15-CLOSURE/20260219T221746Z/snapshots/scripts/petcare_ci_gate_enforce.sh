#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

echo "=== CI GATE ENFORCE ==="
echo "repo_root=${REPO_ROOT}"
echo "date_utc=$(date -u +%Y%m%dT%H%M%SZ)"

echo ""
echo "=== PREFLIGHT ==="
bash "scripts/petcare_ci_preflight.sh"

echo ""
echo "=== TESTS (DETERMINISTIC) ==="
bash "scripts/run_tests_deterministic.sh"

echo ""
echo "=== POLICY DRIFT CHECK ==="
bash "scripts/petcare_policy_drift_check.sh"

echo ""
echo "=== REGISTRY DRIFT CHECK ==="
bash "scripts/petcare_registry_drift_check.sh"

echo ""
echo "CI_GATE_ENFORCE_OK"
