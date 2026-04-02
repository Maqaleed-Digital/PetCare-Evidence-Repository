#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF05_ROOT="${EXECUTION_ROOT}/PHASE_2/DF05"
EVIDENCE_PARENT="${EXECUTION_ROOT}/EVIDENCE/PETCARE-PHASE-2-DF05-NONPROD-RUNTIME-VERIFICATION-AND-ACCESS-MODEL-CONFIRMATION"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${EVIDENCE_PARENT}/${TS}"

mkdir -p "${RUN_DIR}"
exec > >(tee "${RUN_DIR}/apply.log") 2>&1

echo "DF05_APPLY_START=${TS}"
echo "REPO_ROOT=${REPO_ROOT}"
echo "DF05_ROOT=${DF05_ROOT}"
echo "RUN_DIR=${RUN_DIR}"

: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${SERVICE_NAME_NONPROD:?Missing SERVICE_NAME_NONPROD}"
: "${RUNTIME_SECRET_NAME_NONPROD:?Missing RUNTIME_SECRET_NAME_NONPROD}"

git rev-parse HEAD > "${RUN_DIR}/git_head_before.txt"
git status --short > "${RUN_DIR}/git_status_before.txt"

SERVICE_JSON="${RUN_DIR}/run_service_nonprod.json"
IAM_JSON="${RUN_DIR}/run_service_nonprod_iam_policy.json"

gcloud run services describe "${SERVICE_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json > "${SERVICE_JSON}"

gcloud run services get-iam-policy "${SERVICE_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" \
  --format=json > "${IAM_JSON}"

SERVICE_URL="$(python3 - <<PY
import json
with open("${SERVICE_JSON}") as f:
    data = json.load(f)
print(data["status"]["url"])
PY
)"
echo "${SERVICE_URL}" > "${RUN_DIR}/service_url.txt"

LATEST_READY_REVISION="$(python3 - <<PY
import json
with open("${SERVICE_JSON}") as f:
    data = json.load(f)
print(data["status"].get("latestReadyRevisionName",""))
PY
)"
echo "${LATEST_READY_REVISION}" > "${RUN_DIR}/latest_ready_revision.txt"

SERVICE_ACCOUNT_EMAIL="$(python3 - <<PY
import json
with open("${SERVICE_JSON}") as f:
    data = json.load(f)
print(data["spec"]["template"]["spec"].get("serviceAccountName",""))
PY
)"
echo "${SERVICE_ACCOUNT_EMAIL}" > "${RUN_DIR}/service_account_email.txt"

SECRET_WIRING_CHECK="$(python3 - <<PY
import json
with open("${SERVICE_JSON}") as f:
    data = json.load(f)
containers = data["spec"]["template"]["spec"].get("containers", [])
found = False
for c in containers:
    for env in c.get("env", []):
        if env.get("name") == "PETCARE_RUNTIME_CONFIG" and "valueFrom" in env:
            found = True
print("true" if found else "false")
PY
)"
echo "${SECRET_WIRING_CHECK}" > "${RUN_DIR}/secret_wiring_check.txt"

ALLUSERS_INVOKER_PRESENT="$(python3 - <<PY
import json
with open("${IAM_JSON}") as f:
    data = json.load(f)
found = False
for b in data.get("bindings", []):
    if b.get("role") == "roles/run.invoker" and "allUsers" in b.get("members", []):
        found = True
print("true" if found else "false")
PY
)"
echo "${ALLUSERS_INVOKER_PRESENT}" > "${RUN_DIR}/allusers_invoker_present.txt"

curl_status() {
  local url="$1"
  local outfile="$2"
  local code
  code="$(curl -sS -L -o "${outfile}" -w "%{http_code}" "${url}" || true)"
  printf '%s' "${code}"
}

ROOT_UNAUTH_STATUS="$(curl_status "${SERVICE_URL}" "${RUN_DIR}/root_unauth_body.txt")"
echo "${ROOT_UNAUTH_STATUS}" > "${RUN_DIR}/root_unauth_status.txt"

HEALTH_UNAUTH_STATUS="$(curl_status "${SERVICE_URL}/health" "${RUN_DIR}/health_unauth_body.txt")"
echo "${HEALTH_UNAUTH_STATUS}" > "${RUN_DIR}/health_unauth_status.txt"

READY_UNAUTH_STATUS="$(curl_status "${SERVICE_URL}/ready" "${RUN_DIR}/ready_unauth_body.txt")"
echo "${READY_UNAUTH_STATUS}" > "${RUN_DIR}/ready_unauth_status.txt"

IDENTITY_TOKEN="$(gcloud auth print-identity-token 2>/dev/null || gcloud auth print-access-token 2>/dev/null || echo "")"
printf '%s' "${IDENTITY_TOKEN}" > "${RUN_DIR}/identity_token.txt"

AUTH_CODE="$(curl -sS -L -o "${RUN_DIR}/root_auth_body.txt" -w "%{http_code}" \
  -H "Authorization: Bearer ${IDENTITY_TOKEN}" \
  "${SERVICE_URL}" || true)"
echo "${AUTH_CODE}" > "${RUN_DIR}/root_auth_status.txt"

AUTH_HEALTH_CODE="$(curl -sS -L -o "${RUN_DIR}/health_auth_body.txt" -w "%{http_code}" \
  -H "Authorization: Bearer ${IDENTITY_TOKEN}" \
  "${SERVICE_URL}/health" || true)"
echo "${AUTH_HEALTH_CODE}" > "${RUN_DIR}/health_auth_status.txt"

AUTH_READY_CODE="$(curl -sS -L -o "${RUN_DIR}/ready_auth_body.txt" -w "%{http_code}" \
  -H "Authorization: Bearer ${IDENTITY_TOKEN}" \
  "${SERVICE_URL}/ready" || true)"
echo "${AUTH_READY_CODE}" > "${RUN_DIR}/ready_auth_status.txt"

python3 - <<PY
from pathlib import Path
run_dir = Path("${RUN_DIR}")
root_unauth = (run_dir / "root_unauth_status.txt").read_text().strip()
root_auth = (run_dir / "root_auth_status.txt").read_text().strip()
allusers = (run_dir / "allusers_invoker_present.txt").read_text().strip()
if root_unauth.startswith(("2","3")):
    access = "public_effective"
elif root_unauth in ("401","403"):
    access = "restricted_effective"
else:
    access = "indeterminate"
if root_auth.startswith(("2","3")):
    auth = "authenticated_reachable"
elif root_auth in ("401","403"):
    auth = "authenticated_blocked"
else:
    auth = "authenticated_indeterminate"
summary = [
    f"SERVICE_URL={(run_dir / 'service_url.txt').read_text().strip()}",
    f"LATEST_READY_REVISION={(run_dir / 'latest_ready_revision.txt').read_text().strip()}",
    f"SERVICE_ACCOUNT_EMAIL={(run_dir / 'service_account_email.txt').read_text().strip()}",
    f"SECRET_WIRING_CHECK={(run_dir / 'secret_wiring_check.txt').read_text().strip()}",
    f"ALLUSERS_INVOKER_PRESENT={allusers}",
    f"ROOT_UNAUTH_STATUS={root_unauth}",
    f"ROOT_AUTH_STATUS={root_auth}",
    f"ACCESS_MODEL_RESULT={access}",
    f"AUTHENTICATED_REACHABILITY={auth}",
]
(run_dir / "runtime_summary.txt").write_text("\n".join(summary) + "\n")
PY

find "${DF05_ROOT}" -type f | sort > "${RUN_DIR}/file_listing.txt"

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

echo "DF05_APPLY_COMPLETE=${RUN_DIR}"
