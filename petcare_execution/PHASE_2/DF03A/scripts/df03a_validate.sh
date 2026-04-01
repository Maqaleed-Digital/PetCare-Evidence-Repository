#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF03_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03"
DF03A_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03A"

: "${PRJ_PROD:?Missing PRJ_PROD}"
: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${NONPROD_TRIGGER_NAME:?Missing NONPROD_TRIGGER_NAME}"
: "${PROD_TRIGGER_NAME:?Missing PROD_TRIGGER_NAME}"
: "${RUNTIME_SECRET_NAME_NONPROD:?Missing RUNTIME_SECRET_NAME_NONPROD}"
: "${RUNTIME_SECRET_NAME_PROD:?Missing RUNTIME_SECRET_NAME_PROD}"

echo "VALIDATE_PATHS"
test -f "${DF03_ROOT}/cloudbuild.nonprod.yaml"
test -f "${DF03_ROOT}/cloudbuild.prod.yaml"
test -f "${DF03A_ROOT}/README.md"
test -f "${DF03A_ROOT}/scripts/df03a_apply.sh"
test -f "${DF03A_ROOT}/scripts/df03a_validate.sh"

echo "VALIDATE_TRIGGERS_EXIST"
gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --format="value(name)" | grep -qx "${NONPROD_TRIGGER_NAME}"
gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --format="value(name)" | grep -qx "${PROD_TRIGGER_NAME}"

echo "VALIDATE_PROD_APPROVAL_GATE"
PROD_TRIGGER_ID="$(gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --filter="name=${PROD_TRIGGER_NAME}" --format="value(id)")"
gcloud builds triggers describe "${PROD_TRIGGER_ID}" --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --format="value(approvalConfig.approvalRequired)" | grep -qx "True"

echo "VALIDATE_SECRET_VERSIONS_PRESENT"
NONPROD_SECRET_COUNT="$(gcloud secrets versions list "${RUNTIME_SECRET_NAME_NONPROD}" --project="${PRJ_NONPROD}" --format="value(name)" | wc -l | tr -d ' ')"
PROD_SECRET_COUNT="$(gcloud secrets versions list "${RUNTIME_SECRET_NAME_PROD}" --project="${PRJ_PROD}" --format="value(name)" | wc -l | tr -d ' ')"
test "${NONPROD_SECRET_COUNT}" -ge 1
test "${PROD_SECRET_COUNT}" -ge 1

echo "VALIDATE_PROD_GUARDRAIL_TEXT"
grep -q "candidate image tags are not allowed for production" "${DF03_ROOT}/cloudbuild.prod.yaml"
grep -q "production requires digest-pinned image or prod-release tag" "${DF03_ROOT}/cloudbuild.prod.yaml"

echo "DF03A_VALIDATE_PASS"
