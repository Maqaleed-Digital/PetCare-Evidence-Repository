#!/usr/bin/env bash
set -euo pipefail

FAIL=0

if [ -z "${OPTIMIZATION_APPROVED:-}" ]; then
  echo "FAIL: OPTIMIZATION_APPROVED missing"
  FAIL=1
fi

if [ -z "${ROLLBACK_PLAN_DEFINED:-}" ]; then
  echo "FAIL: ROLLBACK_PLAN_DEFINED missing"
  FAIL=1
fi

if [ -z "${KPI_LINKED:-}" ]; then
  echo "FAIL: KPI_LINKED missing"
  FAIL=1
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF16 OPTIMIZATION_EXECUTION_BLOCKED"
  exit 1
fi

echo "DF16 OPTIMIZATION_EXECUTION_GOVERNANCE_ACTIVE"
