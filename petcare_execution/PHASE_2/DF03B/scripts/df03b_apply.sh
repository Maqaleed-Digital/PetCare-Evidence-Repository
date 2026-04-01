#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF03_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03"
DF03B_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03B"
EVIDENCE_PARENT="${EXECUTION_ROOT}/EVIDENCE/PETCARE-PHASE-2-DF03B-BUILD-CONFIG-REPO-ALIGNMENT-AND-FIRST-NONPROD-PIPELINE-EXECUTION"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${EVIDENCE_PARENT}/${TS}"

mkdir -p "${RUN_DIR}"

exec > >(tee "${RUN_DIR}/apply.log") 2>&1

echo "DF03B_APPLY_START=${TS}"
echo "REPO_ROOT=${REPO_ROOT}"
echo "DF03_ROOT=${DF03_ROOT}"
echo "DF03B_ROOT=${DF03B_ROOT}"
echo "RUN_DIR=${RUN_DIR}"

: "${PRJ_PROD:?Missing PRJ_PROD}"
: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${SERVICE_NAME_NONPROD:?Missing SERVICE_NAME_NONPROD}"
: "${SERVICE_NAME_PROD:?Missing SERVICE_NAME_PROD}"
: "${BUILD_SA_NAME:?Missing BUILD_SA_NAME}"
: "${DEPLOY_NONPROD_SA_NAME:?Missing DEPLOY_NONPROD_SA_NAME}"
: "${DEPLOY_PROD_SA_NAME:?Missing DEPLOY_PROD_SA_NAME}"
: "${NONPROD_TRIGGER_NAME:?Missing NONPROD_TRIGGER_NAME}"
: "${PROD_TRIGGER_NAME:?Missing PROD_TRIGGER_NAME}"
: "${NONPROD_BRANCH:?Missing NONPROD_BRANCH}"
: "${NONPROD_BRANCH_PATTERN:?Missing NONPROD_BRANCH_PATTERN}"
: "${PROD_TAG_PATTERN:?Missing PROD_TAG_PATTERN}"
: "${GITHUB_REPO_OWNER:?Missing GITHUB_REPO_OWNER}"
: "${GITHUB_REPO_NAME:?Missing GITHUB_REPO_NAME}"

BUILD_SA_EMAIL="${BUILD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_NONPROD_SA_EMAIL="${DEPLOY_NONPROD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_PROD_SA_EMAIL="${DEPLOY_PROD_SA_NAME}@${PRJ_PROD}.iam.gserviceaccount.com"

test -f "${DF03B_ROOT}/cloudbuild.nonprod.smoke.yaml"
test -f "${DF03_ROOT}/cloudbuild.prod.yaml"

NONPROD_TRIGGER_ID="$(gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --filter="name=${NONPROD_TRIGGER_NAME}" --format="value(id)")"
PROD_TRIGGER_ID="$(gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --filter="name=${PROD_TRIGGER_NAME}" --format="value(id)")"

test -n "${NONPROD_TRIGGER_ID}"
test -n "${PROD_TRIGGER_ID}"

echo "NONPROD_TRIGGER_ID=${NONPROD_TRIGGER_ID}"
echo "PROD_TRIGGER_ID=${PROD_TRIGGER_ID}"

gcloud builds triggers import \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --source=<(python3 - <<PY
import json, pathlib, sys
smoke = pathlib.Path("${DF03B_ROOT}/cloudbuild.nonprod.smoke.yaml").read_text()
cfg = {
  "id": "${NONPROD_TRIGGER_ID}",
  "name": "${NONPROD_TRIGGER_NAME}",
  "description": "PetCare DF03B nonprod inline smoke trigger",
  "github": {
    "owner": "${GITHUB_REPO_OWNER}",
    "name": "${GITHUB_REPO_NAME}",
    "push": {"branch": "${NONPROD_BRANCH_PATTERN}"}
  },
  "inlineBuild": smoke,
  "serviceAccount": "projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}",
  "includeBuildLogs": "INCLUDE_BUILD_LOGS_WITH_STATUS",
  "substitutions": {
    "_REGION": "${REGION_PRIMARY}",
    "_PLATFORM_PROJECT": "${PRJ_NONPROD}",
    "_SERVICE_NAME": "${SERVICE_NAME_NONPROD}"
  }
}
print(json.dumps(cfg))
PY
) >> "${RUN_DIR}/nonprod_trigger_update.txt" 2>&1 || \
gcloud builds triggers update github "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --repo-owner="${GITHUB_REPO_OWNER}" \
  --repo-name="${GITHUB_REPO_NAME}" \
  --branch-pattern="${NONPROD_BRANCH_PATTERN}" \
  --inline-config="${DF03B_ROOT}/cloudbuild.nonprod.smoke.yaml" \
  --service-account="projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}" \
  --include-logs-with-status \
  --update-substitutions="_REGION=${REGION_PRIMARY},_PLATFORM_PROJECT=${PRJ_NONPROD},_SERVICE_NAME=${SERVICE_NAME_NONPROD}" >> "${RUN_DIR}/nonprod_trigger_update.txt" 2>&1

gcloud builds triggers describe "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json > "${RUN_DIR}/nonprod_trigger_after_update.json"

gcloud builds triggers describe "${PROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json > "${RUN_DIR}/prod_trigger_after_update.json"

gcloud builds triggers run "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --branch="${NONPROD_BRANCH}" | tee "${RUN_DIR}/first_nonprod_trigger_run.txt"

gcloud builds triggers list \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" > "${RUN_DIR}/triggers_list.txt"

gcloud run services describe "${SERVICE_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" > "${RUN_DIR}/run_service_nonprod.txt"

git -C "${REPO_ROOT}" rev-parse HEAD > "${RUN_DIR}/git_head_before.txt"
git -C "${REPO_ROOT}" status --short > "${RUN_DIR}/git_status_before.txt"
find "${DF03B_ROOT}" -type f | sort > "${RUN_DIR}/file_listing.txt"

python3 - <<PY
import hashlib, json, pathlib
run_dir = pathlib.Path("${RUN_DIR}")
manifest = {"run_dir": str(run_dir), "files": []}
for p in sorted(run_dir.rglob("*")):
    if p.is_file():
        manifest["files"].append({
            "path": str(p),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()
        })
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
PY

echo "DF03B_APPLY_COMPLETE=${RUN_DIR}"
