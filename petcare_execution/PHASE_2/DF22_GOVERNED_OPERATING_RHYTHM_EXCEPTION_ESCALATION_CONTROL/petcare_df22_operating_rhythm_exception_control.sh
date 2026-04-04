#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DF21_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF21_GOVERNED_RELEASE_PROMOTION_BASELINE_RATIFICATION/petcare_df21_release_promotion_ratification.sh"

if [ ! -x "$DF21_SCRIPT" ]; then
  echo "FAIL: DF21 prerequisite missing"
  exit 1
fi

echo "Checking DF21 prerequisite..."
RELEASE_CANDIDATE_DEFINED="1" \
PROMOTION_APPROVED="1" \
RATIFICATION_RECORDED="1" \
BASELINE_TRANSITION_DEFINED="1" \
BASELINE_BEFORE_AFTER_CAPTURED="1" \
TEMPORARY_PROMOTION="false" \
"$DF21_SCRIPT" >/dev/null

FAIL=0

if [ -z "${CADENCE_DEFINED:-}" ]; then
  echo "FAIL: CADENCE_DEFINED missing"
  FAIL=1
fi

if [ -z "${CHECKPOINTS_DEFINED:-}" ]; then
  echo "FAIL: CHECKPOINTS_DEFINED missing"
  FAIL=1
fi

if [ -z "${EXCEPTION_CLASSIFIED:-}" ]; then
  echo "FAIL: EXCEPTION_CLASSIFIED missing"
  FAIL=1
fi

if [ "${ESCALATION_REQUIRED:-false}" = "true" ]; then
  if [ -z "${ESCALATION_ROUTE_DEFINED:-}" ]; then
    echo "FAIL: ESCALATION_ROUTE_DEFINED missing"
    FAIL=1
  fi
  if [ -z "${ESCALATION_RECORDED:-}" ]; then
    echo "FAIL: ESCALATION_RECORDED missing"
    FAIL=1
  fi
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF22 OPERATING_RHYTHM_BLOCKED"
  exit 1
fi

echo "DF22 GOVERNED_OPERATING_RHYTHM_ACTIVE"
