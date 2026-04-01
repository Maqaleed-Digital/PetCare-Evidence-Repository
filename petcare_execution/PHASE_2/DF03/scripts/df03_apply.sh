#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF03_ROOT="${EXECUTION_ROOT}/PHASE_2/DF03"
EVIDENCE_PARENT="${EXECUTION_ROOT}/EVIDENCE/PETCARE-PHASE-2-DF03-DEPLOYMENT-PIPELINE"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${EVIDENCE_PARENT}/${TS}"

mkdir -p "${RUN_DIR}"

exec > >(tee "${RUN_DIR}/apply.log") 2>&1

echo "DF03_APPLY_START=${TS}"
echo "REPO_ROOT=${REPO_ROOT}"
echo "DF03_ROOT=${DF03_ROOT}"
echo "RUN_DIR=${RUN_DIR}"

: "${PRJ_PROD:?Missing PRJ_PROD}"
: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${PRJ_SANDBOX:?Missing PRJ_SANDBOX}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${ARTIFACT_REPO:?Missing ARTIFACT_REPO}"
: "${SERVICE_NAME_NONPROD:?Missing SERVICE_NAME_NONPROD}"
: "${SERVICE_NAME_PROD:?Missing SERVICE_NAME_PROD}"
: "${BUILD_SA_NAME:?Missing BUILD_SA_NAME}"
: "${DEPLOY_NONPROD_SA_NAME:?Missing DEPLOY_NONPROD_SA_NAME}"
: "${DEPLOY_PROD_SA_NAME:?Missing DEPLOY_PROD_SA_NAME}"

GITHUB_REPO_OWNER="${GITHUB_REPO_OWNER:-}"
GITHUB_REPO_NAME="${GITHUB_REPO_NAME:-}"
GITHUB_REPOSITORY_RESOURCE="${GITHUB_REPOSITORY_RESOURCE:-}"
NONPROD_BRANCH_PATTERN="${NONPROD_BRANCH_PATTERN:-^main$}"
PROD_TAG_PATTERN="${PROD_TAG_PATTERN:-^prod-release-.*$}"
NONPROD_TRIGGER_NAME="${NONPROD_TRIGGER_NAME:-petcare-nonprod-main}"
PROD_TRIGGER_NAME="${PROD_TRIGGER_NAME:-petcare-prod-release}"
IMAGE_NAME="${IMAGE_NAME:-petcare-api}"
RUNTIME_SECRET_NAME_NONPROD="${RUNTIME_SECRET_NAME_NONPROD:-petcare-runtime-config-nonprod}"
RUNTIME_SECRET_NAME_PROD="${RUNTIME_SECRET_NAME_PROD:-petcare-runtime-config-prod}"
RUNTIME_SECRET_VALUE_NONPROD="${RUNTIME_SECRET_VALUE_NONPROD:-}"
RUNTIME_SECRET_VALUE_PROD="${RUNTIME_SECRET_VALUE_PROD:-}"
CREATE_PLACEHOLDER_SECRETS="${CREATE_PLACEHOLDER_SECRETS:-false}"

BUILD_SA_EMAIL="${BUILD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_NONPROD_SA_EMAIL="${DEPLOY_NONPROD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_PROD_SA_EMAIL="${DEPLOY_PROD_SA_NAME}@${PRJ_PROD}.iam.gserviceaccount.com"

NONPROD_IMAGE_BASE="${REGION_PRIMARY}-docker.pkg.dev/${PRJ_NONPROD}/${ARTIFACT_REPO}/${IMAGE_NAME}"

if [[ -z "${GITHUB_REPOSITORY_RESOURCE}" && ( -z "${GITHUB_REPO_OWNER}" || -z "${GITHUB_REPO_NAME}" ) ]]; then
  echo "Missing GitHub linkage. Set GITHUB_REPOSITORY_RESOURCE for 2nd-gen repo connection, or set GITHUB_REPO_OWNER and GITHUB_REPO_NAME for 1st-gen GitHub trigger creation."
  exit 31
fi

gcloud services enable artifactregistry.googleapis.com --project="${PRJ_NONPROD}"
gcloud services enable cloudbuild.googleapis.com --project="${PRJ_NONPROD}"
gcloud services enable run.googleapis.com --project="${PRJ_NONPROD}"
gcloud services enable secretmanager.googleapis.com --project="${PRJ_NONPROD}"
gcloud services enable logging.googleapis.com --project="${PRJ_NONPROD}"
gcloud services enable monitoring.googleapis.com --project="${PRJ_NONPROD}"

gcloud services enable cloudbuild.googleapis.com --project="${PRJ_PROD}"
gcloud services enable run.googleapis.com --project="${PRJ_PROD}"
gcloud services enable secretmanager.googleapis.com --project="${PRJ_PROD}"
gcloud services enable logging.googleapis.com --project="${PRJ_PROD}"
gcloud services enable monitoring.googleapis.com --project="${PRJ_PROD}"

gcloud artifacts repositories update "${ARTIFACT_REPO}" \
  --project="${PRJ_NONPROD}" \
  --location="${REGION_PRIMARY}" \
  --immutable-tags

if ! gcloud iam service-accounts describe "${BUILD_SA_EMAIL}" --project="${PRJ_NONPROD}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${BUILD_SA_NAME}" \
    --project="${PRJ_NONPROD}" \
    --display-name="PetCare DF03 Build Service Account"
fi

if ! gcloud iam service-accounts describe "${DEPLOY_NONPROD_SA_EMAIL}" --project="${PRJ_NONPROD}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${DEPLOY_NONPROD_SA_NAME}" \
    --project="${PRJ_NONPROD}" \
    --display-name="PetCare DF03 Deploy Nonprod Service Account"
fi

if ! gcloud iam service-accounts describe "${DEPLOY_PROD_SA_EMAIL}" --project="${PRJ_PROD}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${DEPLOY_PROD_SA_NAME}" \
    --project="${PRJ_PROD}" \
    --display-name="PetCare DF03 Deploy Prod Service Account"
fi

for role in roles/run.admin roles/artifactregistry.reader roles/secretmanager.secretAccessor roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "${PRJ_NONPROD}" \
    --member="serviceAccount:${DEPLOY_NONPROD_SA_EMAIL}" \
    --role="${role}" \
    --quiet
done

for role in roles/run.admin roles/artifactregistry.reader roles/secretmanager.secretAccessor roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "${PRJ_PROD}" \
    --member="serviceAccount:${DEPLOY_PROD_SA_EMAIL}" \
    --role="${role}" \
    --quiet
done

for role in roles/cloudbuild.builds.editor roles/artifactregistry.writer roles/run.admin roles/iam.serviceAccountUser roles/logging.logWriter roles/secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding "${PRJ_NONPROD}" \
    --member="serviceAccount:${BUILD_SA_EMAIL}" \
    --role="${role}" \
    --quiet
done

gcloud iam service-accounts add-iam-policy-binding "${DEPLOY_NONPROD_SA_EMAIL}" \
  --project="${PRJ_NONPROD}" \
  --member="serviceAccount:${BUILD_SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet

gcloud iam service-accounts add-iam-policy-binding "${DEPLOY_PROD_SA_EMAIL}" \
  --project="${PRJ_PROD}" \
  --member="serviceAccount:${BUILD_SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet

if ! gcloud secrets describe "${RUNTIME_SECRET_NAME_NONPROD}" --project="${PRJ_NONPROD}" >/dev/null 2>&1; then
  gcloud secrets create "${RUNTIME_SECRET_NAME_NONPROD}" \
    --project="${PRJ_NONPROD}" \
    --replication-policy="automatic"
fi

if ! gcloud secrets describe "${RUNTIME_SECRET_NAME_PROD}" --project="${PRJ_PROD}" >/dev/null 2>&1; then
  gcloud secrets create "${RUNTIME_SECRET_NAME_PROD}" \
    --project="${PRJ_PROD}" \
    --replication-policy="automatic"
fi

if [[ -n "${RUNTIME_SECRET_VALUE_NONPROD}" ]]; then
  printf '%s' "${RUNTIME_SECRET_VALUE_NONPROD}" | \
    gcloud secrets versions add "${RUNTIME_SECRET_NAME_NONPROD}" \
      --project="${PRJ_NONPROD}" \
      --data-file=-
elif [[ "${CREATE_PLACEHOLDER_SECRETS}" == "true" ]]; then
  printf '%s' 'REPLACE_NONPROD_RUNTIME_CONFIG' | \
    gcloud secrets versions add "${RUNTIME_SECRET_NAME_NONPROD}" \
      --project="${PRJ_NONPROD}" \
      --data-file=-
fi

if [[ -n "${RUNTIME_SECRET_VALUE_PROD}" ]]; then
  printf '%s' "${RUNTIME_SECRET_VALUE_PROD}" | \
    gcloud secrets versions add "${RUNTIME_SECRET_NAME_PROD}" \
      --project="${PRJ_PROD}" \
      --data-file=-
elif [[ "${CREATE_PLACEHOLDER_SECRETS}" == "true" ]]; then
  printf '%s' 'REPLACE_PROD_RUNTIME_CONFIG' | \
    gcloud secrets versions add "${RUNTIME_SECRET_NAME_PROD}" \
      --project="${PRJ_PROD}" \
      --data-file=-
fi

gcloud run services describe "${SERVICE_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" >/dev/null 2>&1 || \
gcloud run deploy "${SERVICE_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --platform=managed \
  --image="us-docker.pkg.dev/cloudrun/container/hello" \
  --service-account="${DEPLOY_NONPROD_SA_EMAIL}" \
  --allow-unauthenticated \
  --quiet

gcloud run services describe "${SERVICE_NAME_PROD}" \
  --project="${PRJ_PROD}" \
  --region="${REGION_PRIMARY}" >/dev/null 2>&1 || \
gcloud run deploy "${SERVICE_NAME_PROD}" \
  --project="${PRJ_PROD}" \
  --region="${REGION_PRIMARY}" \
  --platform=managed \
  --image="us-docker.pkg.dev/cloudrun/container/hello" \
  --service-account="${DEPLOY_PROD_SA_EMAIL}" \
  --allow-unauthenticated \
  --quiet

create_nonprod_trigger() {
  if [[ -n "${GITHUB_REPOSITORY_RESOURCE}" ]]; then
    gcloud builds triggers create github \
      --project="${PRJ_NONPROD}" \
      --region="${REGION_PRIMARY}" \
      --name="${NONPROD_TRIGGER_NAME}" \
      --repository="${GITHUB_REPOSITORY_RESOURCE}" \
      --branch-pattern="${NONPROD_BRANCH_PATTERN}" \
      --build-config="petcare_execution/PHASE_2/DF03/cloudbuild.nonprod.yaml" \
      --service-account="projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}" \
      --include-logs-with-status \
      --substitutions="_REGION=${REGION_PRIMARY},_ARTIFACT_REPO=${ARTIFACT_REPO},_IMAGE_NAME=${IMAGE_NAME},_SERVICE_NAME=${SERVICE_NAME_NONPROD},_PLATFORM_PROJECT=${PRJ_NONPROD},_DEPLOY_SA_EMAIL=${DEPLOY_NONPROD_SA_EMAIL},_RUNTIME_SECRET_NAME=${RUNTIME_SECRET_NAME_NONPROD}"
  else
    gcloud builds triggers create github \
      --project="${PRJ_NONPROD}" \
      --region="${REGION_PRIMARY}" \
      --name="${NONPROD_TRIGGER_NAME}" \
      --repo-owner="${GITHUB_REPO_OWNER}" \
      --repo-name="${GITHUB_REPO_NAME}" \
      --branch-pattern="${NONPROD_BRANCH_PATTERN}" \
      --build-config="petcare_execution/PHASE_2/DF03/cloudbuild.nonprod.yaml" \
      --service-account="projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}" \
      --include-logs-with-status \
      --substitutions="_REGION=${REGION_PRIMARY},_ARTIFACT_REPO=${ARTIFACT_REPO},_IMAGE_NAME=${IMAGE_NAME},_SERVICE_NAME=${SERVICE_NAME_NONPROD},_PLATFORM_PROJECT=${PRJ_NONPROD},_DEPLOY_SA_EMAIL=${DEPLOY_NONPROD_SA_EMAIL},_RUNTIME_SECRET_NAME=${RUNTIME_SECRET_NAME_NONPROD}"
  fi
}

create_prod_trigger() {
  if [[ -n "${GITHUB_REPOSITORY_RESOURCE}" ]]; then
    gcloud builds triggers create github \
      --project="${PRJ_NONPROD}" \
      --region="${REGION_PRIMARY}" \
      --name="${PROD_TRIGGER_NAME}" \
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

cat > "${RUN_DIR}/promotion_model.txt" <<PROMO
NONPROD_IMAGE_BASE=${NONPROD_IMAGE_BASE}
PROD_DEPLOY_CONFIG=petcare_execution/PHASE_2/DF03/cloudbuild.prod.yaml

CONTROLLED_PRODUCTION_PROMOTION
1. select immutable nonprod digest:
   gcloud artifacts docker images list ${NONPROD_IMAGE_BASE} --include-tags

2. assign controlled prod release tag to that digest:
   gcloud artifacts docker tags add ${NONPROD_IMAGE_BASE}@sha256:REPLACE_DIGEST ${NONPROD_IMAGE_BASE}:prod-release-REPLACE_RELEASE_TAG

3. deploy manually through Cloud Build using the controlled image reference:
   gcloud builds submit --no-source --project=${PRJ_NONPROD} --region=${REGION_PRIMARY} --config=petcare_execution/PHASE_2/DF03/cloudbuild.prod.yaml --service-account=projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL} --substitutions=_REGION=${REGION_PRIMARY},_SERVICE_NAME=${SERVICE_NAME_PROD},_PLATFORM_PROJECT=${PRJ_PROD},_DEPLOY_SA_EMAIL=${DEPLOY_PROD_SA_EMAIL},_RUNTIME_SECRET_NAME=${RUNTIME_SECRET_NAME_PROD},_IMAGE_URI=${NONPROD_IMAGE_BASE}:prod-release-REPLACE_RELEASE_TAG
PROMO

git rev-parse HEAD > "${RUN_DIR}/git_head_before.txt"
git status --short > "${RUN_DIR}/git_status_before.txt"
gcloud artifacts repositories describe "${ARTIFACT_REPO}" --project="${PRJ_NONPROD}" --location="${REGION_PRIMARY}" > "${RUN_DIR}/artifact_repo_describe.txt"
gcloud builds triggers list --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/triggers_list.txt"
gcloud run services describe "${SERVICE_NAME_NONPROD}" --project="${PRJ_NONPROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/run_service_nonprod.txt"
gcloud run services describe "${SERVICE_NAME_PROD}" --project="${PRJ_PROD}" --region="${REGION_PRIMARY}" > "${RUN_DIR}/run_service_prod.txt"

find "${DF03_ROOT}" -type f | sort > "${RUN_DIR}/file_listing.txt"

python3 - <<PY
import hashlib, json, os, pathlib
run_dir = pathlib.Path("${RUN_DIR}")
manifest = {"run_dir": str(run_dir), "files": []}
for p in sorted(run_dir.rglob("*")):
    if p.is_file():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest["files"].append({"path": str(p), "sha256": h})
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
PY

echo "DF03_APPLY_COMPLETE=${RUN_DIR}"
