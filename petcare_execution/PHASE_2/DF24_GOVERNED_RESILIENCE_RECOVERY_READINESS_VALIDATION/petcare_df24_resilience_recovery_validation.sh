#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DF23_SCRIPT="$REPO_ROOT/petcare_execution/PHASE_2/DF23_GOVERNED_ASSURANCE_CONTROL_EFFECTIVENESS_ATTESTATION/petcare_df23_assurance_attestation.sh"

if [ ! -x "$DF23_SCRIPT" ]; then
  echo "FAIL: DF23 prerequisite missing"
  exit 1
fi

echo "Checking DF23 prerequisite..."
ASSURANCE_SCOPE_DEFINED="1" \
CONTROL_EFFECTIVENESS_ASSESSED="1" \
ATTESTATION_STATUS_RECORDED="1" \
REMEDIATION_REQUIRED="false" \
"$DF23_SCRIPT" >/dev/null

FAIL=0

if [ -z "${DISRUPTION_SCOPE_DEFINED:-}" ]; then
  echo "FAIL: DISRUPTION_SCOPE_DEFINED missing"
  FAIL=1
fi

if [ -z "${DEGRADED_MODE_DEFINED:-}" ]; then
  echo "FAIL: DEGRADED_MODE_DEFINED missing"
  FAIL=1
fi

if [ -z "${RECOVERY_READINESS_VALIDATED:-}" ]; then
  echo "FAIL: RECOVERY_READINESS_VALIDATED missing"
  FAIL=1
fi

if [ -z "${RESTORATION_RESULT_RECORDED:-}" ]; then
  echo "FAIL: RESTORATION_RESULT_RECORDED missing"
  FAIL=1
fi

if [ "${RESTORATION_FAILED:-false}" = "true" ]; then
  if [ -z "${EXCEPTION_TRIGGERED:-}" ]; then
    echo "FAIL: EXCEPTION_TRIGGERED missing"
    FAIL=1
  fi
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF24 RESILIENCE_BLOCKED"
  exit 1
fi

echo "DF24 GOVERNED_RESILIENCE_ACTIVE"
