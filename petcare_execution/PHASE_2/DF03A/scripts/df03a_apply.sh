#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF03_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03"
DF03A_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03A"
EVIDENCE_PARENT="${EXECUTION_ROOT}/EVIDENCE/PETCARE-PHASE-2-DF03A-TRIGGER-ACTIVATION-AND-FIRST-CONTROLLED-NONPROD-DEPLOYMENT"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${EVIDENCE_PARENT}/${TS}"

mkdir -p "${RUN_DIR}"

exec > >(tee "${RUN_DIR}/apply.log") 2>&1

echo "DF03A_APPLY_START=${TS}"
echo "REPO_ROOT=${REPO_ROOT}"
echo "DF03_ROOT=${DF03_ROOT}"
echo "DF03A_ROOT=${DF03A_ROOT}"
echo "RUN_DIR=${RUN_DIR}"

: "${PRJ_PROD:?Missing PRJ_PROD}"
: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${ARTIFACT_REPO:?Missing ARTIFACT_REPO}"
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
: "${RUNTIME_SECRET_NAME_NONPROD:?Missing RUNTIME_SECRET_NAME_NONPROD}"
: "${RUNTIME_SECRET_NAME_PROD:?Missing RUNTIME_SECRET_NAME_PROD}"
: "${RUNTIME_SECRET_VALUE_NONPROD:?Missing RUNTIME_SECRET_VALUE_NONPROD}"
: "${RUNTIME_SECRET_VALUE_PROD:?Missing RUNTIME_SECRET_VALUE_PROD}"

BUILD_SA_EMAIL="${BUILD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_NONPROD_SA_EMAIL="${DEPLOY_NONPROD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_PROD_SA_EMAIL="${DEPLOY_PROD_SA_NAME}@${PRJ_PROD}.iam.gserviceaccount.com"

GITHUB_REPOSITORY_RESOURCE="${GITHUB_REPOSITORY_RESOURCE:-}"
GITHUB_REPO_OWNER="${GITHUB_REPO_OWNER:-}"
GITHUB_REPO_NAME="${GITHUB_REPO_NAME:-}"

if [[ -n "${GITHUB_REPOSITORY_RESOURCE}" ]]; then
  TRIGGER_MODE="2ND_GEN"
elif [[ -n "${GITHUB_REPO_OWNER}" && -n "${GITHUB_REPO_NAME}" ]]; then
  TRIGGER_MODE="1ST_GEN"
else
  echo "Missing repository linkage. Set either GITHUB_REPOSITORY_RESOURCE or both GITHUB_REPO_OWNER and GITHUB_REPO_NAME."
  exit 31
fi

test -f "${DF03_ROOT}/cloudbuild.nonprod.yaml"
test -f "${DF03_ROOT}/cloudbuild.prod.yaml"

gcloud iam service-accounts describe "${BUILD_SA_EMAIL}" --project="${PRJ_NONPROD}" >/dev/null
gcloud iam service-accounts describe "${DEPLOY_NONPROD_SA_EMAIL}" --project="${PRJ_NONPROD}" >/dev/null
gcloud iam service-accounts describe "${DEPLOY_PROD_SA_EMAIL}" --project="${PRJ_PROD}" >/dev/null

gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
  --project="${PRJ_NONPROD}" \
  --location="${REGION_PRIMARY}" >/dev/null

gcloud secrets describe "${RUNTIME_SECRET_NAME_NONPROD}" --project="${PRJ_NONPROD}" >/dev/null
gcloud secrets describe "${RUNTIME_SECRET_NAME_PROD}" --project="${PRJ_PROD}" >/dev/null

TMP_NONPROD_SECRET_FILE="${RUN_DIR}/nonprod_runtime_secret_payload.txt"
TMP_PROD_SECRET_FILE="${RUN_DIR}/prod_runtime_secret_payload.txt"

printf '%s' "${RUNTIME_SECRET_VALUE_NONPROD}" > "${TMP_NONPROD_SECRET_FILE}"
printf '%s' "${RUNTIME_SECRET_VALUE_PROD}" > "${TMP_PROD_SECRET_FILE}"

gcloud secrets versions add "${RUNTIME_SECRET_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --data-file="${TMP_NONPROD_SECRET_FILE}"

gcloud secrets versions add "${RUNTIME_SECRET_NAME_PROD}" \
  --project="${PRJ_PROD}" \
  --data-file="${TMP_PROD_SECRET_FILE}"

create_nonprod_trigger() {
  if [[ "${TRIGGER_MODE}" == "2ND_GEN" ]]; then
    gcloud builds triggers create github \
      --project="${PRJ_NONPROD}" \
      --region="${REGION_PRIMARY}" \
      --name="${NONPROD_TRIGGER_NAME}" \
      --description="PetCare DF03A nonprod controlled deployment trigger" \
      --repository="${GITHUB_REPOSITORY_RESOURCE}" \
      --branch-pattern="${NONPROD_BRANCH_PATTERN}" \
      --build-config="petcare_execution/PHASE_2/DF03/cloudbuild.nonprod.yaml" \
      --service-account="projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}" \
      --include-logs-with-status \
      --substitutions="_REGION=${REGION_PRIMARY},_ARTIFACT_REPO=${ARTIFACT_REPO},_IMAGE_NAME=petcare-api,_SERVICE_NAME=${SERVICE_NAME_NONPROD},_PLATFORM_PROJECT=${PRJ_NONPROD},_DEPLOY_SA_EMAIL=${DEPLOY_NONPROD_SA_EMAIL},_RUNTIME_SECRET_NAME=${RUNTIME_SECRET_NAME_NONPROD}"
  else
    gcloud builds triggers create github \
      --project="${PRJ_NONPROD}" \
      --region="${REGION_PRIMARY}" \
      --name="${NONPROD_TRIGGER_NAME}" \
      --description="PetCare DF03A nonprod controlled deployment trigger" \
      --repo-owner="${GITHUB_REPO_OWNER}" \
      --repo-name="${GITHUB_REPO_NAME}" \
      --branch-pattern="${NONPROD_BRANCH_PATTERN}" \
      --build-config="petcare_execution/PHASE_2/DF03/cloudbuild.nonprod.yaml" \
      --service-account="projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}" \
      --include-logs-with-status \
      --substitutions="_REGION=${REGION_PRIMARY},_ARTIFACT_REPO=${ARTIFACT_REPO},_IMAGE_NAME=petcare-api,_SERVICE_NAME=${SERVICE_NAME_NONPROD},_PLATFORM_PROJECT=${PRJ_NONPROD},_DEPLOY_SA_EMAIL=${DEPLOY_NONPROD_SA_EMAIL},_RUNTIME_SECRET_NAME=${RUNTIME_SECRET_NAME_NONPROD}"
  fi
}

create_prod_trigger() {
  if [[ "${TRIGGER_MODE}" == "2ND_GEN" ]]; then
    gcloud builds triggers create github \
      --project="${PRJ_NONPROD}" \
      --region="${REGION_PRIMARY}" \
      --name="${PROD_TRIGGER_NAME}" \
      --description="PetCare DF03A prod approval-gated release trigger" \
      --repository="${GITHUB_REPOSITORY_RESOURCE}" \
      --tag-pattern="${PROD_TAG_PATTERN}" \
      --build-config="petcare_execution/PHASE_2/DF03/cloudbuild.prod.yaml" \
      --service-account="projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}" \
      --require-approval \
      --include-logs-with-status \
      --substitutions="_REGION=${REGION_PRIMARY},_SERVICE_NAME=${SERVICE_NAME_PROD},_PLATFORM_PROJECT=${PRJ_PROD},_DEPLOY_SA_EMAIL=${DEPLOY_PROD_SA_EMAIL},_RUNTIME_SECRET_NAME=${RUNTIME_SECRET_NAME_PROD}"
  else
    gcloud builds triggers create github \
      --project="${PRJ_NONPROD}" \
      --region="${REGION_PRIMARY}" \
      --name="${PROD_TRIGGER_NAME}" \
      --description="PetCare DF03A prod approval-gated release trigger" \
      --repo-owner="${GITHUB_REPO_OWNER}" \
      --repo-name="${GITHUB_REPO_NAME}" \
      --tag-pattern="${PROD_TAG_PATTERN}" \
      --build-config="petcare_execution/PHASE_2/DF03/cloudbuild.prod.yaml" \
      --service-account="projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}" \
      --require-approval \
      --include-logs-with-status \
      --substitutions="_REGION=${REGION_PRIMARY},_SERVICE_NAME=${SERVICE_NAME_PROD},_PLATFORM_PROJECT=${PRJ_PROD},_DEPLOY_SA_EMAIL=${DEPLOY_PROD_SA_EMAIL},_RUNTIME_SECRET_NAME=${RUNTIME_SECRET_NAME_PROD}"
  fi
}

if ! gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --format="value(name)" | grep -qx "${NONPROD_TRIGGER_NAME}"; then
  create_nonprod_trigger
fi

if ! gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --format="value(name)" | grep -qx "${PROD_TRIGGER_NAME}"; then
  create_prod_trigger
fi

NONPROD_TRIGGER_ID="$(gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --filter="name=${NONPROD_TRIGGER_NAME}" --format="value(id)")"
if [[ -z "${NONPROD_TRIGGER_ID}" ]]; then
  echo "Unable to resolve nonprod trigger id"
  exit 41
fi

gcloud builds triggers run "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --branch="${NONPROD_BRANCH}" | tee "${RUN_DIR}/first_nonprod_trigger_run.txt"

gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/triggers_list.txt"
gcloud builds triggers describe "${NONPROD_TRIGGER_ID}" --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/nonprod_trigger_describe.txt"

PROD_TRIGGER_ID="$(gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" --filter="name=${PROD_TRIGGER_NAME}" --format="value(id)")"
if [[ -n "${PROD_TRIGGER_ID}" ]]; then
  gcloud builds triggers describe "${PROD_TRIGGER_ID}" --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/prod_trigger_describe.txt"
fi

gcloud secrets versions list "${RUNTIME_SECRET_NAME_NONPROD}" --project="${PRJ_NONPROD}" > "${RUN_DIR}/nonprod_secret_versions.txt"
gcloud secrets versions list "${RUNTIME_SECRET_NAME_PROD}" --project="${PRJ_PROD}" > "${RUN_DIR}/prod_secret_versions.txt"
gcloud run services describe "${SERVICE_NAME_NONPROD}" --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/run_service_nonprod.txt"
gcloud run services describe "${SERVICE_NAME_PROD}" --project="${PRJ_PROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/run_service_prod.txt"

cat > "${RUN_DIR}/trigger_mode.txt" <<MODE
TRIGGER_MODE=${TRIGGER_MODE}
GITHUB_REPOSITORY_RESOURCE=${GITHUB_REPOSITORY_RESOURCE}
GITHUB_REPO_OWNER=${GITHUB_REPO_OWNER}
GITHUB_REPO_NAME=${GITHUB_REPO_NAME}
MODE

git -C "${REPO_ROOT}" rev-parse HEAD > "${RUN_DIR}/git_head_before.txt"
git -C "${REPO_ROOT}" status --short > "${RUN_DIR}/git_status_before.txt"
find "${DF03A_ROOT}" -type f | sort > "${RUN_DIR}/file_listing.txt"

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

echo "DF03A_APPLY_COMPLETE=${RUN_DIR}"
