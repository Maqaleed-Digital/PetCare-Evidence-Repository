#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DF19_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF19_CLOSED_LOOP_FEEDBACK_OUTCOME_VALIDATION_GOVERNANCE/petcare_df19_feedback_validation_governance.sh"

if [ ! -x "$DF19_SCRIPT" ]; then
  echo "FAIL: DF19 prerequisite missing"
  exit 1
fi

echo "Checking DF19 prerequisite..."
OUTCOME_VALIDATED="1" \
FEEDBACK_RECORDED="1" \
VARIANCE_ASSESSED="1" \
SIMILAR_FAILURE_DETECTED="false" \
THRESHOLD_BREACH_DETECTED="false" \
"$DF19_SCRIPT" >/dev/null

FAIL=0

if [ -z "${POLICY_CHANGE_REQUESTED:-}" ]; then
  echo "FAIL: POLICY_CHANGE_REQUESTED missing"
  FAIL=1
fi

if [ -z "${EVIDENCE_LINKED:-}" ]; then
  echo "FAIL: EVIDENCE_LINKED missing"
  FAIL=1
fi

if [ -z "${APPROVAL_RECORDED:-}" ]; then
  echo "FAIL: APPROVAL_RECORDED missing"
  FAIL=1
fi

if [ -z "${VERSION_TRANSITION_DEFINED:-}" ]; then
  echo "FAIL: VERSION_TRANSITION_DEFINED missing"
  FAIL=1
fi

if [ -z "${BEFORE_AFTER_CAPTURED:-}" ]; then
  echo "FAIL: BEFORE_AFTER_CAPTURED missing"
  FAIL=1
fi

if [ "${TEMPORARY_TUNING:-false}" = "true" ]; then
  if [ -z "${EXPIRY_DEFINED:-}" ]; then
    echo "FAIL: EXPIRY_DEFINED missing for temporary tuning"
    FAIL=1
  fi
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF20 POLICY_CHANGE_BLOCKED"
  exit 1
fi

echo "DF20 GOVERNED_POLICY_TUNING_ACTIVE"
