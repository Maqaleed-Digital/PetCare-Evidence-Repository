#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DF16_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF16_OPTIMIZATION_EXECUTION_GOVERNANCE/petcare_df16_optimization_governance.sh"

if [ ! -x "$DF16_SCRIPT" ]; then
  echo "FAIL: DF16 prerequisite script not found or not executable"
  exit 1
fi

echo "DF17: checking DF16 prerequisite governance"
OPTIMIZATION_APPROVED="${OPTIMIZATION_APPROVED:-}" \
ROLLBACK_PLAN_DEFINED="${ROLLBACK_PLAN_DEFINED:-}" \
KPI_LINKED="${KPI_LINKED:-}" \
"$DF16_SCRIPT" >/dev/null

FAIL=0

if [ -z "${PRIORITIZATION_ASSIGNED:-}" ]; then
  echo "FAIL: PRIORITIZATION_ASSIGNED missing"
  FAIL=1
fi

if [ -z "${PRIORITY_RANK_ELIGIBLE:-}" ]; then
  echo "FAIL: PRIORITY_RANK_ELIGIBLE missing"
  FAIL=1
fi

if [ -z "${DEPENDENCIES_RESOLVED:-}" ]; then
  echo "FAIL: DEPENDENCIES_RESOLVED missing"
  FAIL=1
fi

if [ "${OVERRIDE_REQUESTED:-false}" = "true" ]; then
  if [ -z "${OVERRIDE_APPROVED:-}" ]; then
    echo "FAIL: OVERRIDE_APPROVED missing"
    FAIL=1
  fi
  if [ -z "${OVERRIDE_SCOPE_DEFINED:-}" ]; then
    echo "FAIL: OVERRIDE_SCOPE_DEFINED missing"
    FAIL=1
  fi
  if [ -z "${OVERRIDE_JUSTIFICATION_DEFINED:-}" ]; then
    echo "FAIL: OVERRIDE_JUSTIFICATION_DEFINED missing"
    FAIL=1
  fi
  if [ -z "${OVERRIDE_EFFECTIVE_PERIOD_DEFINED:-}" ]; then
    echo "FAIL: OVERRIDE_EFFECTIVE_PERIOD_DEFINED missing"
    FAIL=1
  fi
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF17 PRIORITIZATION_BLOCKED"
  exit 1
fi

echo "DF17 EXECUTION_INTELLIGENCE_GOVERNANCE_ACTIVE"
