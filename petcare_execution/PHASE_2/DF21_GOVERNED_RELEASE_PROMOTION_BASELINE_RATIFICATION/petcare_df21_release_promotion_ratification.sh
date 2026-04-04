#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DF20_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF20_GOVERNED_POLICY_TUNING_CHANGE_CONTROL/petcare_df20_policy_tuning_change_control.sh"

if [ ! -x "$DF20_SCRIPT" ]; then
  echo "FAIL: DF20 prerequisite missing"
  exit 1
fi

echo "Checking DF20 prerequisite..."
POLICY_CHANGE_REQUESTED="1" \
EVIDENCE_LINKED="1" \
APPROVAL_RECORDED="1" \
VERSION_TRANSITION_DEFINED="1" \
BEFORE_AFTER_CAPTURED="1" \
TEMPORARY_TUNING="false" \
"$DF20_SCRIPT" >/dev/null

FAIL=0

if [ -z "${RELEASE_CANDIDATE_DEFINED:-}" ]; then
  echo "FAIL: RELEASE_CANDIDATE_DEFINED missing"
  FAIL=1
fi

if [ -z "${PROMOTION_APPROVED:-}" ]; then
  echo "FAIL: PROMOTION_APPROVED missing"
  FAIL=1
fi

if [ -z "${RATIFICATION_RECORDED:-}" ]; then
  echo "FAIL: RATIFICATION_RECORDED missing"
  FAIL=1
fi

if [ -z "${BASELINE_TRANSITION_DEFINED:-}" ]; then
  echo "FAIL: BASELINE_TRANSITION_DEFINED missing"
  FAIL=1
fi

if [ -z "${BASELINE_BEFORE_AFTER_CAPTURED:-}" ]; then
  echo "FAIL: BASELINE_BEFORE_AFTER_CAPTURED missing"
  FAIL=1
fi

if [ "${TEMPORARY_PROMOTION:-false}" = "true" ]; then
  if [ -z "${PROMOTION_EXPIRY_DEFINED:-}" ]; then
    echo "FAIL: PROMOTION_EXPIRY_DEFINED missing for temporary promotion"
    FAIL=1
  fi
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF21 RELEASE_PROMOTION_BLOCKED"
  exit 1
fi

echo "DF21 GOVERNED_RELEASE_PROMOTION_ACTIVE"
