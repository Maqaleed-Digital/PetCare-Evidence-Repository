#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF04_ROOT="${EXECUTION_ROOT}/PHASE_2/DF04"
EVIDENCE_PARENT="${EXECUTION_ROOT}/EVIDENCE/PETCARE-PHASE-2-DF04-REAL-NONPROD-APPLICATION-BUILD-AND-DEPLOYMENT-CONTRACT-ALIGNMENT"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${EVIDENCE_PARENT}/${TS}"

mkdir -p "${RUN_DIR}"

exec > >(tee "${RUN_DIR}/apply.log") 2>&1

echo "DF04_APPLY_START=${TS}"
echo "REPO_ROOT=${REPO_ROOT}"
echo "DF04_ROOT=${DF04_ROOT}"
echo "RUN_DIR=${RUN_DIR}"

: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${SERVICE_NAME_NONPROD:?Missing SERVICE_NAME_NONPROD}"
: "${BUILD_SA_NAME:?Missing BUILD_SA_NAME}"
: "${DEPLOY_NONPROD_SA_NAME:?Missing DEPLOY_NONPROD_SA_NAME}"
: "${NONPROD_TRIGGER_NAME:?Missing NONPROD_TRIGGER_NAME}"
: "${NONPROD_BRANCH:?Missing NONPROD_BRANCH}"
: "${NONPROD_BRANCH_PATTERN:?Missing NONPROD_BRANCH_PATTERN}"
: "${GITHUB_REPO_OWNER:?Missing GITHUB_REPO_OWNER}"
: "${GITHUB_REPO_NAME:?Missing GITHUB_REPO_NAME}"
: "${RUNTIME_SECRET_NAME_NONPROD:?Missing RUNTIME_SECRET_NAME_NONPROD}"

BUILD_SA_EMAIL="${BUILD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"
DEPLOY_NONPROD_SA_EMAIL="${DEPLOY_NONPROD_SA_NAME}@${PRJ_NONPROD}.iam.gserviceaccount.com"

test -f "${DF04_ROOT}/cloudbuild.nonprod.app.yaml"

CURRENT_HEAD="$(git rev-parse HEAD)"
echo "${CURRENT_HEAD}" > "${RUN_DIR}/git_head_before.txt"
git status --short > "${RUN_DIR}/git_status_before.txt"

NONPROD_TRIGGER_ID="$(gcloud builds triggers list \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --filter="name=${NONPROD_TRIGGER_NAME}" \
  --format="value(id)")"

test -n "${NONPROD_TRIGGER_ID}"

gcloud builds triggers describe "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json > "${RUN_DIR}/nonprod_trigger_before_update.json"

TRIGGER_IMPORT_YAML="${RUN_DIR}/nonprod_trigger_import.yaml"
{
  echo "id: ${NONPROD_TRIGGER_ID}"
  echo "name: ${NONPROD_TRIGGER_NAME}"
  echo "description: PetCare DF04 real nonprod backend application build and deployment contract"
  echo "github:"
  echo "  owner: ${GITHUB_REPO_OWNER}"
  echo "  name: ${GITHUB_REPO_NAME}"
  echo "  push:"
  echo "    branch: ${NONPROD_BRANCH_PATTERN}"
  echo "serviceAccount: projects/${PRJ_NONPROD}/serviceAccounts/${BUILD_SA_EMAIL}"
  echo "includeBuildLogs: INCLUDE_BUILD_LOGS_WITH_STATUS"
  echo "substitutions:"
  echo "  _REGION: ${REGION_PRIMARY}"
  echo "  _PLATFORM_PROJECT: ${PRJ_NONPROD}"
  echo "  _SERVICE_NAME: ${SERVICE_NAME_NONPROD}"
  echo "  _DEPLOY_SA_EMAIL: ${DEPLOY_NONPROD_SA_EMAIL}"
  echo "  _RUNTIME_SECRET_NAME: ${RUNTIME_SECRET_NAME_NONPROD}"
  echo "build:"
  sed 's/^/  /' "${DF04_ROOT}/cloudbuild.nonprod.app.yaml"
} > "${TRIGGER_IMPORT_YAML}"

gcloud builds triggers import \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --source="${TRIGGER_IMPORT_YAML}"

gcloud builds triggers describe "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json > "${RUN_DIR}/nonprod_trigger_after_update.json"

TRIGGER_RUN_OUTPUT="${RUN_DIR}/first_nonprod_trigger_run.txt"
gcloud builds triggers run "${NONPROD_TRIGGER_ID}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --branch="${NONPROD_BRANCH}" | tee "${TRIGGER_RUN_OUTPUT}"

LATEST_BUILD_ID=""
for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
  LATEST_BUILD_ID="$(gcloud builds list \
    --project="${PRJ_NONPROD}" \
    --region="${REGION_PRIMARY}" \
    --filter="buildTriggerId=${NONPROD_TRIGGER_ID}" \
    --sort-by="~createTime" \
    --limit=1 \
    --format="value(id)")"
  if [[ -n "${LATEST_BUILD_ID}" ]]; then
    break
  fi
  sleep 5
done

echo "LATEST_BUILD_ID=${LATEST_BUILD_ID}" | tee "${RUN_DIR}/latest_build_id.txt"

if [[ -n "${LATEST_BUILD_ID}" ]]; then
  gcloud builds describe "${LATEST_BUILD_ID}" \
    --project="${PRJ_NONPROD}" \
    --region="${REGION_PRIMARY}" > "${RUN_DIR}/latest_build_describe.txt" || true
fi

gcloud builds triggers list \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" > "${RUN_DIR}/triggers_list.txt"

gcloud run services describe "${SERVICE_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" > "${RUN_DIR}/run_service_nonprod.txt"

find "${DF04_ROOT}" -type f | sort > "${RUN_DIR}/file_listing.txt"

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

echo "DF04_APPLY_COMPLETE=${RUN_DIR}"
