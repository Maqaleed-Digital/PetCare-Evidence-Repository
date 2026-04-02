#!/usr/bin/env bash
set -euo pipefail

MODE="${PETCARE_PROD_ACTIVATION_MODE:-SIMULATION}"

echo "DF09 PRODUCTION ACTIVATION MODE: ${MODE}"

########################################
# STEP 1 — RUN DF08 WORKFLOW
########################################
echo "STEP 1: RUN CONTROLLED RELEASE WORKFLOW"

./scripts/petcare_df08_release_workflow.sh

########################################
# STEP 2 — MODE CHECK
########################################

if [ "$MODE" = "SIMULATION" ]; then
  echo "SIMULATION MODE — NO PRODUCTION ACTIVATION"
  exit 0
fi

########################################
# STEP 3 — APPROVAL CHECK
########################################

if [ "${PETCARE_PROD_ACTIVATION_APPROVED:-}" != "true" ]; then
  echo "DF09 ACTIVATION BLOCKED: approval flag missing"
  exit 1
fi

########################################
# STEP 4 — ACTIVATION RECORD (NO REAL DEPLOY)
########################################

echo "CONTROLLED ACTIVATION APPROVED"

########################################
# STEP 5 — EVIDENCE PACK
########################################

./scripts/petcare_df07_evidence_pack.sh

echo "DF09 CONTROLLED ACTIVATION: PASS"
