#!/usr/bin/env bash
set -euo pipefail

echo "DF08 RELEASE WORKFLOW START"

########################################
# STEP 1 — RELEASE GATE
########################################
echo "STEP 1: RELEASE GATE CHECK"
./scripts/petcare_df07_release_gate_check.sh

########################################
# STEP 2 — NONPROD VERIFY ONLY
########################################
echo "STEP 2: POST-DEPLOY VERIFY (NONPROD)"

: "${PETCARE_NONPROD_SERVICE_URL:?required}"

export PETCARE_VERIFY_URL="$PETCARE_NONPROD_SERVICE_URL"
export PETCARE_VERIFY_HEALTH_PATH="${PETCARE_VERIFY_HEALTH_PATH:-/health}"
export PETCARE_VERIFY_READY_PATH="${PETCARE_VERIFY_READY_PATH:-/ready}"
export PETCARE_EXPECT_HTTP_CODE="${PETCARE_EXPECT_HTTP_CODE:-200}"

./scripts/petcare_df07_post_deploy_verify.sh

########################################
# STEP 3 — EVIDENCE PACK
########################################
echo "STEP 3: EVIDENCE PACK"

./scripts/petcare_df07_evidence_pack.sh

echo "DF08 RELEASE WORKFLOW: PASS"
