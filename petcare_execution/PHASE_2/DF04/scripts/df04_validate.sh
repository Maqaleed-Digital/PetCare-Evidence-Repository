#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF04_ROOT="${EXECUTION_ROOT}/PHASE_2/DF04"

: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${NONPROD_TRIGGER_NAME:?Missing NONPROD_TRIGGER_NAME}"

echo "VALIDATE_PATHS"
test -f "${DF04_ROOT}/README.md"
test -f "${DF04_ROOT}/cloudbuild.nonprod.app.yaml"
test -f "${DF04_ROOT}/scripts/df04_apply.sh"
test -f "${DF04_ROOT}/scripts/df04_validate.sh"

NONPROD_TRIGGER_ID="$(gcloud builds triggers list \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --filter="name=${NONPROD_TRIGGER_NAME}" \
  --format="value(id)")"

echo "VALIDATE_TRIGGER_EXISTS"
test -n "${NONPROD_TRIGGER_ID}"

echo "VALIDATE_TRIGGER_USES_BUILD_FIELD"
gcloud builds triggers describe "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json | grep -q '"build"'

echo "VALIDATE_TRIGGER_NO_FILENAME_DEPENDENCY"
! gcloud builds triggers describe "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json | grep -q '"filename"'

echo "VALIDATE_APP_CONTRACT_TEXT"
grep -q -- '--source="app/backend"' "${DF04_ROOT}/cloudbuild.nonprod.app.yaml"
grep -q 'PETCARE_RUNTIME_CONFIG=' "${DF04_ROOT}/cloudbuild.nonprod.app.yaml"
grep -q 'DF04_NONPROD_APP_PASS' "${DF04_ROOT}/cloudbuild.nonprod.app.yaml"

echo "DF04_VALIDATE_PASS"
