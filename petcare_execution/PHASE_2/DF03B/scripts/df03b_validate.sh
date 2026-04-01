#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF03_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03"
DF03B_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03B"

: "${PRJ_PROD:?Missing PRJ_PROD}"
: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${NONPROD_TRIGGER_NAME:?Missing NONPROD_TRIGGER_NAME}"
: "${PROD_TRIGGER_NAME:?Missing PROD_TRIGGER_NAME}"

echo "VALIDATE_PATHS"
test -f "${DF03_ROOT}/cloudbuild.prod.yaml"
test -f "${DF03B_ROOT}/README.md"
test -f "${DF03B_ROOT}/cloudbuild.nonprod.smoke.yaml"
test -f "${DF03B_ROOT}/scripts/df03b_apply.sh"
test -f "${DF03B_ROOT}/scripts/df03b_validate.sh"

NONPROD_TRIGGER_ID="$(gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --filter="name=${NONPROD_TRIGGER_NAME}" --format="value(id)")"
PROD_TRIGGER_ID="$(gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --filter="name=${PROD_TRIGGER_NAME}" --format="value(id)")"

echo "VALIDATE_TRIGGERS_EXIST"
test -n "${NONPROD_TRIGGER_ID}"
test -n "${PROD_TRIGGER_ID}"

echo "VALIDATE_NONPROD_INLINE_CONFIG"
gcloud builds triggers describe "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if 'build' in d and 'filename' not in d else 1)"

echo "VALIDATE_PROD_APPROVAL_GATE"
gcloud builds triggers describe "${PROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format="value(approvalConfig.approvalRequired)" | grep -qx "True"

echo "VALIDATE_SMOKE_CONFIG_TEXT"
grep -q "DF03B_NONPROD_SMOKE_PASS" "${DF03B_ROOT}/cloudbuild.nonprod.smoke.yaml"

echo "DF03B_VALIDATE_PASS"
