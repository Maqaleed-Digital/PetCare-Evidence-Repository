#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
PACK_ROOT="$ROOT_DIR/petcare_execution/PHASE_6/PH6_LIVE_PILOT_EXECUTION"
EVIDENCE_ROOT="$ROOT_DIR/petcare_execution/EVIDENCE/PETCARE-PH6-LIVE-PILOT-EXECUTION"
APP_SOURCE_OF_TRUTH_COMMIT="${APP_SOURCE_OF_TRUTH_COMMIT:-c6e57769}"
TS="${TS:-$(date -u +"%Y%m%dT%H%M%SZ")}"
RUN_DIR="$EVIDENCE_ROOT/$TS"
TMP_DIR="$RUN_DIR/.tmp"

mkdir -p "$RUN_DIR" "$TMP_DIR"

required_vars=(
  PILOT_OPERATOR
  PILOT_INCIDENT_CHANNEL
  PILOT_APPROVAL_REF
  PILOT_EXECUTION_WINDOW_UTC
  PILOT_CLINIC_NAME
  PILOT_CLINIC_LICENSE_REF
  PILOT_VET_1_NAME
  PILOT_VET_1_LICENSE_REF
  PILOT_OWNER_CASE_1_REF
  PILOT_PRODUCTION_URL
)

forbidden_pattern='demo|test|sample|fake|seed|dummy|placeholder'

{
  echo "PH6 live pilot decision log"
  echo "app_source_of_truth_commit=$APP_SOURCE_OF_TRUTH_COMMIT"
  echo "run_dir=$RUN_DIR"
  echo "timestamp_utc=$TS"
} > "$TMP_DIR/decision_log.txt"

missing=()
invalid=()

for v in "${required_vars[@]}"; do
  current="${!v:-}"
  if [ -z "$current" ]; then
    missing+=("$v")
  else
    lower="$(printf '%s' "$current" | tr '[:upper:]' '[:lower:]')"
    if printf '%s' "$lower" | grep -Eq "$forbidden_pattern"; then
      invalid+=("$v")
    fi
  fi
done

{
  printf '{\n'
  printf '  "app_source_of_truth_commit": "%s",\n' "$APP_SOURCE_OF_TRUTH_COMMIT"
  printf '  "pilot_operator": "%s",\n' "${PILOT_OPERATOR:-}"
  printf '  "pilot_incident_channel": "%s",\n' "${PILOT_INCIDENT_CHANNEL:-}"
  printf '  "pilot_approval_ref": "%s",\n' "${PILOT_APPROVAL_REF:-}"
  printf '  "pilot_execution_window_utc": "%s",\n' "${PILOT_EXECUTION_WINDOW_UTC:-}"
  printf '  "pilot_clinic_name": "%s",\n' "${PILOT_CLINIC_NAME:-}"
  printf '  "pilot_clinic_license_ref": "%s",\n' "${PILOT_CLINIC_LICENSE_REF:-}"
  printf '  "pilot_vet_1_name": "%s",\n' "${PILOT_VET_1_NAME:-}"
  printf '  "pilot_vet_1_license_ref": "%s",\n' "${PILOT_VET_1_LICENSE_REF:-}"
  printf '  "pilot_owner_case_1_ref": "%s",\n' "${PILOT_OWNER_CASE_1_REF:-}"
  printf '  "pilot_production_url": "%s"\n' "${PILOT_PRODUCTION_URL:-}"
  printf '}\n'
} > "$TMP_DIR/operator_inputs.json"

set +u
_missing_count="${#missing[@]}"
_invalid_count="${#invalid[@]}"
set -u

if [ "$_missing_count" -gt 0 ] || [ "$_invalid_count" -gt 0 ]; then
  {
    echo "STATUS=BLOCKED"
    echo "REASON=Missing or invalid live variables"
    echo "MISSING_COUNT=$_missing_count"
    for item in "${missing[@]+"${missing[@]}"}"; do
      echo "MISSING=$item"
    done
    echo "INVALID_COUNT=$_invalid_count"
    for item in "${invalid[@]+"${invalid[@]}"}"; do
      echo "INVALID=$item"
    done
  } > "$TMP_DIR/blocked.log"

  {
    echo "Pre-Run: BLOCKED"
    echo "Live Run: NOT_STARTED"
    echo "Post-Run: NOT_STARTED"
  } > "$TMP_DIR/checklist_status.txt"

  {
    printf '{\n'
    printf '  "status": "blocked",\n'
    printf '  "app_source_of_truth_commit": "%s",\n' "$APP_SOURCE_OF_TRUTH_COMMIT"
    printf '  "run_dir": "%s"\n' "$RUN_DIR"
    printf '}\n'
  } > "$TMP_DIR/execution_state.json"

  git rev-parse HEAD > "$TMP_DIR/git_head.txt"

  (
    cd "$RUN_DIR"
    find . -maxdepth 1 -type f | sed 's#^\./##' | sort > "$TMP_DIR/MANIFEST.txt"
  )

  for f in decision_log.txt operator_inputs.json blocked.log checklist_status.txt execution_state.json git_head.txt; do
    mv "$TMP_DIR/$f" "$RUN_DIR/$f"
  done
  cp "$TMP_DIR/MANIFEST.txt" "$RUN_DIR/MANIFEST.txt"

  echo "EVIDENCE_RUN_DIR=$RUN_DIR"
  exit 1
fi

{
  echo "STATUS=ACTIVE"
  echo "REASON=All required live variables present"
  echo "NEXT_STEP=Execute real workflow in production"
} > "$TMP_DIR/active.log"

{
  echo "Pre-Run: PASS"
  echo "Live Run: READY"
  echo "Post-Run: PENDING"
} > "$TMP_DIR/checklist_status.txt"

{
  printf '{\n'
  printf '  "status": "active_ready",\n'
  printf '  "app_source_of_truth_commit": "%s",\n' "$APP_SOURCE_OF_TRUTH_COMMIT"
  printf '  "run_dir": "%s"\n' "$RUN_DIR"
  printf '}\n'
} > "$TMP_DIR/execution_state.json"

git rev-parse HEAD > "$TMP_DIR/git_head.txt"

(
  cd "$RUN_DIR"
  find . -maxdepth 1 -type f | sed 's#^\./##' | sort > "$TMP_DIR/MANIFEST.txt"
)

for f in decision_log.txt operator_inputs.json active.log checklist_status.txt execution_state.json git_head.txt; do
  mv "$TMP_DIR/$f" "$RUN_DIR/$f"
done
cp "$TMP_DIR/MANIFEST.txt" "$RUN_DIR/MANIFEST.txt"

echo "EVIDENCE_RUN_DIR=$RUN_DIR"
