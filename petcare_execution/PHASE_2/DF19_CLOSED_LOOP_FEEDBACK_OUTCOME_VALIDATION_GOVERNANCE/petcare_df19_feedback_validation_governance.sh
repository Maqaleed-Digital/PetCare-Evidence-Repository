#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DF18_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF18_EXECUTION_ORCHESTRATION_CAPACITY_GOVERNANCE/petcare_df18_execution_orchestration.sh"

if [ ! -x "$DF18_SCRIPT" ]; then
  echo "FAIL: DF18 prerequisite missing"
  exit 1
fi

echo "Checking DF18 prerequisite..."
OPTIMIZATION_APPROVED="1" \
ROLLBACK_PLAN_DEFINED="1" \
KPI_LINKED="1" \
PRIORITIZATION_ASSIGNED="1" \
PRIORITY_RANK_ELIGIBLE="1" \
DEPENDENCIES_RESOLVED="1" \
OVERRIDE_REQUESTED="false" \
CAPACITY_DEFINED="1" \
WITHIN_CAPACITY_LIMIT="1" \
EXECUTION_WINDOW_VALID="1" \
"$DF18_SCRIPT" >/dev/null

FAIL=0

if [ -z "${OUTCOME_VALIDATED:-}" ]; then
  echo "FAIL: OUTCOME_VALIDATED missing"
  FAIL=1
fi

if [ -z "${FEEDBACK_RECORDED:-}" ]; then
  echo "FAIL: FEEDBACK_RECORDED missing"
  FAIL=1
fi

if [ -z "${VARIANCE_ASSESSED:-}" ]; then
  echo "FAIL: VARIANCE_ASSESSED missing"
  FAIL=1
fi

if [ "${SIMILAR_FAILURE_DETECTED:-false}" = "true" ]; then
  if [ -z "${REVIEW_CLEARED:-}" ]; then
    echo "FAIL: REVIEW_CLEARED missing for similar prior failure"
    FAIL=1
  fi
fi

if [ "${THRESHOLD_BREACH_DETECTED:-false}" = "true" ]; then
  if [ -z "${MANDATORY_REVIEW_COMPLETED:-}" ]; then
    echo "FAIL: MANDATORY_REVIEW_COMPLETED missing for threshold breach"
    FAIL=1
  fi
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF19 FEEDBACK_BLOCKED"
  exit 1
fi

echo "DF19 CLOSED_LOOP_FEEDBACK_GOVERNANCE_ACTIVE"
