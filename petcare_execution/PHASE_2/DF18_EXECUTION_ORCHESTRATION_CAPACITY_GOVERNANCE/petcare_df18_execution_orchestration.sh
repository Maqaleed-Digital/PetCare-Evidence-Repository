#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

DF17_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF17_EXECUTION_INTELLIGENCE_GOVERNANCE/petcare_df17_execution_intelligence_governance.sh"

if [ ! -x "$DF17_SCRIPT" ]; then
  echo "FAIL: DF17 prerequisite missing"
  exit 1
fi

echo "Checking DF17 prerequisite..."
PRIORITIZATION_ASSIGNED="1" \
PRIORITY_RANK_ELIGIBLE="1" \
DEPENDENCIES_RESOLVED="1" \
OVERRIDE_REQUESTED="false" \
"$DF17_SCRIPT" >/dev/null

FAIL=0

if [ -z "${CAPACITY_DEFINED:-}" ]; then
  echo "FAIL: CAPACITY_DEFINED missing"
  FAIL=1
fi

if [ -z "${WITHIN_CAPACITY_LIMIT:-}" ]; then
  echo "FAIL: WITHIN_CAPACITY_LIMIT missing"
  FAIL=1
fi

if [ -z "${EXECUTION_WINDOW_VALID:-}" ]; then
  echo "FAIL: EXECUTION_WINDOW_VALID missing"
  FAIL=1
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF18 CAPACITY_BLOCKED"
  exit 1
fi

echo "DF18 EXECUTION_ORCHESTRATION_ACTIVE"
