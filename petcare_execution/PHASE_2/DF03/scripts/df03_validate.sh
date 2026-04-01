#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF03_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03"

: "${PRJ_PROD:?Missing PRJ_PROD}"
: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${ARTIFACT_REPO:?Missing ARTIFACT_REPO}"
: "${SERVICE_NAME_NONPROD:?Missing SERVICE_NAME_NONPROD}"
: "${SERVICE_NAME_PROD:?Missing SERVICE_NAME_PROD}"
: "${BUILD_SA_NAME:?Missing BUILD_SA_NAME}"
: "${DEPLOY_NONPROD_SA_NAME:?Missing DEPLOY_NONPROD_SA_NAME}"
: "${DEPLOY_PROD_SA_NAME:?Missing DEPLOY_PROD_SA_NAME}"

BUILD_SA_EMAIL="${BUILD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_NONPROD_SA_EMAIL="${DEPLOY_NONPROD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_PROD_SA_EMAIL="${DEPLOY_PROD_SA_NAME}@${PRJ_PROD}.iam.gserviceaccount.com"

echo "VALIDATE_PATHS"
test -f "${DF03_ROOT}/README.md"
test -f "${DF03_ROOT}/cloudbuild.nonprod.yaml"
test -f "${DF03_ROOT}/cloudbuild.prod.yaml"
test -f "${DF03_ROOT}/scripts/df03_apply.sh"
test -f "${DF03_ROOT}/scripts/df03_validate.sh"

echo "VALIDATE_GCLOUD_RESOURCES"
gcloud artifacts repositories describe "${ARTIFACT_REPO}" --project="${PRJ_NONPROD}" --location="${REGION_PRIMARY}" >/dev/null
gcloud iam service-accounts describe "${BUILD_SA_EMAIL}" --project="${PRJ_NONPROD}" >/dev/null
gcloud iam service-accounts describe "${DEPLOY_NONPROD_SA_EMAIL}" --project="${PRJ_NONPROD}" >/dev/null
gcloud iam service-accounts describe "${DEPLOY_PROD_SA_EMAIL}" --project="${PRJ_PROD}" >/dev/null
gcloud run services describe "${SERVICE_NAME_NONPROD}" --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" >/dev/null
gcloud run services describe "${SERVICE_NAME_PROD}" --project="${PRJ_PROD}" --region="${REGION_PRIMARY}" >/dev/null

echo "VALIDATE_IMMUTABILITY"
gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
  --project="${PRJ_NONPROD}" \
  --location="${REGION_PRIMARY}" \
  --format="value(immutableTags)" | grep -qx "True"

echo "VALIDATE_TRIGGERS"
gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --format="value(name)" | grep -qx "petcare-nonprod-main"
gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --format="value(name)" | grep -qx "petcare-prod-release"

echo "VALIDATE_YAML_REFERENCES"
grep -q "candidate-\${SHORT_SHA}" "${DF03_ROOT}/cloudbuild.nonprod.yaml"
grep -q "production requires digest-pinned image or prod-release tag" "${DF03_ROOT}/cloudbuild.prod.yaml"

echo "DF03_VALIDATE_PASS"
