#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
EXECUTION_ROOT="${REPO_ROOT}/petcare_execution"
DF05_ROOT="${EXECUTION_ROOT}/PHASE_2/DF05"

: "${PRJ_NONPROD:?Missing PRJ_NONPROD}"
: "${REGION_PRIMARY:?Missing REGION_PRIMARY}"
: "${SERVICE_NAME_NONPROD:?Missing SERVICE_NAME_NONPROD}"

echo "VALIDATE_PATHS"
test -f "${DF05_ROOT}/README.md"
test -f "${DF05_ROOT}/scripts/df05_apply.sh"
test -f "${DF05_ROOT}/scripts/df05_validate.sh"

echo "VALIDATE_SERVICE_EXISTS"
gcloud run services describe "${SERVICE_NAME_NONPROD}" \
  --project="${PRJ_NONPROD}" \
  --region="${REGION_PRIMARY}" >/dev/null

LATEST_RUN_DIR="$(find "${EXECUTION_ROOT}/EVIDENCE/PETCARE-PHASE-2-DF05-NONPROD-RUNTIME-VERIFICATION-AND-ACCESS-MODEL-CONFIRMATION" -mindepth 1 -maxdepth 1 -type d | sort | tail -1)"
test -n "${LATEST_RUN_DIR}"

echo "VALIDATE_EVIDENCE_FILES"
test -f "${LATEST_RUN_DIR}/run_service_nonprod.json"
test -f "${LATEST_RUN_DIR}/run_service_nonprod_iam_policy.json"
test -f "${LATEST_RUN_DIR}/service_url.txt"
test -f "${LATEST_RUN_DIR}/latest_ready_revision.txt"
test -f "${LATEST_RUN_DIR}/service_account_email.txt"
test -f "${LATEST_RUN_DIR}/secret_wiring_check.txt"
test -f "${LATEST_RUN_DIR}/allusers_invoker_present.txt"
test -f "${LATEST_RUN_DIR}/root_unauth_status.txt"
test -f "${LATEST_RUN_DIR}/root_auth_status.txt"
test -f "${LATEST_RUN_DIR}/runtime_summary.txt"
test -f "${LATEST_RUN_DIR}/MANIFEST.json"

echo "VALIDATE_SECRET_WIRING_RESULT"
grep -qx 'true' "${LATEST_RUN_DIR}/secret_wiring_check.txt"

echo "VALIDATE_STATUS_CODES_CAPTURED"
grep -Eq '^[0-9]{3}$' "${LATEST_RUN_DIR}/root_unauth_status.txt"
grep -Eq '^[0-9]{3}$' "${LATEST_RUN_DIR}/root_auth_status.txt"

echo "VALIDATE_SUMMARY_FIELDS"
grep -q 'ACCESS_MODEL_RESULT=' "${LATEST_RUN_DIR}/runtime_summary.txt"
grep -q 'AUTHENTICATED_REACHABILITY=' "${LATEST_RUN_DIR}/runtime_summary.txt"

echo "DF05_VALIDATE_PASS"
