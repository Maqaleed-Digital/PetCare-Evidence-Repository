#!/usr/bin/env bash
set -euo pipefail

MODE="${PETCARE_PROD_EXPOSURE_MODE:-PRIVATE_ONLY}"

fail() {
  echo "DF10_EXPOSURE_CONTROL: FAIL - $1" >&2
  exit 1
}

echo "DF10_EXPOSURE_CONTROL: MODE=${MODE}"

echo "STEP 1: DF09 CONTROLLED ACTIVATION PATH"
./scripts/petcare_df09_prod_activation.sh

case "${MODE}" in
  PRIVATE_ONLY)
    echo "DF10_EXPOSURE_CONTROL: PASS - private-only mode enforced"
    exit 0
    ;;
  CONTROLLED_PUBLIC)
    ;;
  *)
    fail "unsupported mode ${MODE}"
    ;;
esac

echo "STEP 2: PUBLIC EXPOSURE APPROVAL CHECK"

if [ "${PETCARE_PUBLIC_EXPOSURE_APPROVED:-}" != "true" ]; then
  fail "public exposure approval flag missing"
fi

if [ -z "${PETCARE_PUBLIC_EXPOSURE_CHANGE_REF:-}" ]; then
  fail "public exposure change reference missing"
fi

if [ -z "${PETCARE_PUBLIC_EXPOSURE_ROLLBACK_PLAN:-}" ]; then
  fail "public exposure rollback plan missing"
fi

echo "STEP 3: CONTROLLED PUBLIC SIMULATION ONLY"
echo "public_exposure_approved=${PETCARE_PUBLIC_EXPOSURE_APPROVED}"
echo "public_exposure_change_ref=${PETCARE_PUBLIC_EXPOSURE_CHANGE_REF}"
echo "public_exposure_rollback_plan=${PETCARE_PUBLIC_EXPOSURE_ROLLBACK_PLAN}"

echo "STEP 4: EVIDENCE PACK"
./scripts/petcare_df07_evidence_pack.sh

echo "DF10_EXPOSURE_CONTROL: PASS - controlled public simulation only"
