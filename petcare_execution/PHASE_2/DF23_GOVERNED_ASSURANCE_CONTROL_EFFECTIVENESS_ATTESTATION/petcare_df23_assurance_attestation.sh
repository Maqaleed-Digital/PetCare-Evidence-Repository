#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DF22_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF22_GOVERNED_OPERATING_RHYTHM_EXCEPTION_ESCALATION_CONTROL/petcare_df22_operating_rhythm_exception_control.sh"

if [ ! -x "$DF22_SCRIPT" ]; then
  echo "FAIL: DF22 prerequisite missing"
  exit 1
fi

echo "Checking DF22 prerequisite..."
CADENCE_DEFINED="1" \
CHECKPOINTS_DEFINED="1" \
EXCEPTION_CLASSIFIED="1" \
ESCALATION_REQUIRED="false" \
"$DF22_SCRIPT" >/dev/null

FAIL=0

if [ -z "${ASSURANCE_SCOPE_DEFINED:-}" ]; then
  echo "FAIL: ASSURANCE_SCOPE_DEFINED missing"
  FAIL=1
fi

if [ -z "${CONTROL_EFFECTIVENESS_ASSESSED:-}" ]; then
  echo "FAIL: CONTROL_EFFECTIVENESS_ASSESSED missing"
  FAIL=1
fi

if [ -z "${ATTESTATION_STATUS_RECORDED:-}" ]; then
  echo "FAIL: ATTESTATION_STATUS_RECORDED missing"
  FAIL=1
fi

if [ "${REMEDIATION_REQUIRED:-false}" = "true" ]; then
  if [ -z "${REMEDIATION_TRIGGER_RECORDED:-}" ]; then
    echo "FAIL: REMEDIATION_TRIGGER_RECORDED missing"
    FAIL=1
  fi
  if [ -z "${REMEDIATION_OWNER_DEFINED:-}" ]; then
    echo "FAIL: REMEDIATION_OWNER_DEFINED missing"
    FAIL=1
  fi
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF23 ASSURANCE_BLOCKED"
  exit 1
fi

echo "DF23 GOVERNED_ASSURANCE_ACTIVE"
