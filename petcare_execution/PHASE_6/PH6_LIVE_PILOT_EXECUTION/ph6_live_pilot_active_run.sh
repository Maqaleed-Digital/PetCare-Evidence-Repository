#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
PACK_ROOT="$ROOT_DIR/petcare_execution/PHASE_6/PH6_LIVE_PILOT_EXECUTION"
EVIDENCE_ROOT="$ROOT_DIR/petcare_execution/EVIDENCE/PETCARE-PH6-LIVE-PILOT-ACTIVE-RUN"
APP_SOURCE_OF_TRUTH_COMMIT="${APP_SOURCE_OF_TRUTH_COMMIT:-ec53458d}"
TS="${TS:-$(date -u +"%Y%m%dT%H%M%SZ")}"
RUN_DIR="$EVIDENCE_ROOT/$TS"
TMP_DIR="$RUN_DIR/.tmp"

mkdir -p "$RUN_DIR" "$TMP_DIR"

required_vars=(
  APP_SOURCE_OF_TRUTH_COMMIT
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
  PILOT_APPOINTMENT_REF
  PILOT_CONSULTATION_REF
  PILOT_SIGNOFF_REF
  PILOT_RUN_RESULT
  PILOT_OPERATOR_NOTES
)

optional_vars=(
  PILOT_PRESCRIPTION_REF
  PILOT_BLOCKERS
)

forbidden_pattern='demo|test|sample|fake|seed|dummy|placeholder|replace_with|tbd|todo'

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

for v in "${optional_vars[@]}"; do
  current="${!v:-}"
  if [ -n "$current" ]; then
    lower="$(printf '%s' "$current" | tr '[:upper:]' '[:lower:]')"
    if printf '%s' "$lower" | grep -Eq "$forbidden_pattern"; then
      invalid+=("$v")
    fi
  fi
done

{
  echo "PH6 live pilot active run"
  echo "app_source_of_truth_commit=$APP_SOURCE_OF_TRUTH_COMMIT"
  echo "run_dir=$RUN_DIR"
  echo "timestamp_utc=$TS"
} > "$TMP_DIR/decision_log.txt"

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
  printf '  "pilot_production_url": "%s",\n' "${PILOT_PRODUCTION_URL:-}"
  printf '  "pilot_appointment_ref": "%s",\n' "${PILOT_APPOINTMENT_REF:-}"
  printf '  "pilot_consultation_ref": "%s",\n' "${PILOT_CONSULTATION_REF:-}"
  printf '  "pilot_signoff_ref": "%s",\n' "${PILOT_SIGNOFF_REF:-}"
  printf '  "pilot_prescription_ref": "%s",\n' "${PILOT_PRESCRIPTION_REF:-}"
  printf '  "pilot_run_result": "%s",\n' "${PILOT_RUN_RESULT:-}"
  printf '  "pilot_blockers": "%s",\n' "${PILOT_BLOCKERS:-}"
  printf '  "pilot_operator_notes": "%s"\n' "${PILOT_OPERATOR_NOTES:-}"
  printf '}\n'
} > "$TMP_DIR/operator_inputs.json"

if [ "${#missing[@]}" -gt 0 ] || [ "${#invalid[@]}" -gt 0 ]; then
  {
    echo "STATUS=BLOCKED"
    echo "REASON=Missing or invalid live variables"
    echo "MISSING_COUNT=${#missing[@]}"
    if [ "${#missing[@]}" -gt 0 ]; then
      for item in "${missing[@]}"; do echo "MISSING=$item"; done
    fi
    echo "INVALID_COUNT=${#invalid[@]}"
    if [ "${#invalid[@]}" -gt 0 ]; then
      for item in "${invalid[@]}"; do echo "INVALID=$item"; done
    fi
  } > "$TMP_DIR/active_run_status.txt"

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

  git -C "$ROOT_DIR" rev-parse HEAD > "$TMP_DIR/git_head.txt"

  for f in decision_log.txt operator_inputs.json active_run_status.txt checklist_status.txt execution_state.json git_head.txt; do
    mv "$TMP_DIR/$f" "$RUN_DIR/$f"
  done

  (
    cd "$RUN_DIR"
    find . -maxdepth 1 -type f | sed 's#^\./##' | sort > MANIFEST.txt
  )

  echo "EVIDENCE_RUN_DIR=$RUN_DIR"
  exit 1
fi

run_result_lower="$(printf '%s' "$PILOT_RUN_RESULT" | tr '[:upper:]' '[:lower:]')"

if [ "$run_result_lower" != "pass" ] && [ "$run_result_lower" != "failed" ] && [ "$run_result_lower" != "blocked" ]; then
  {
    echo "STATUS=BLOCKED"
    echo "REASON=Invalid PILOT_RUN_RESULT"
    echo "INVALID=PILOT_RUN_RESULT"
  } > "$TMP_DIR/active_run_status.txt"

  {
    echo "Pre-Run: PASS"
    echo "Live Run: BLOCKED"
    echo "Post-Run: NOT_STARTED"
  } > "$TMP_DIR/checklist_status.txt"

  {
    printf '{\n'
    printf '  "status": "blocked_invalid_run_result",\n'
    printf '  "app_source_of_truth_commit": "%s",\n' "$APP_SOURCE_OF_TRUTH_COMMIT"
    printf '  "run_dir": "%s"\n' "$RUN_DIR"
    printf '}\n'
  } > "$TMP_DIR/execution_state.json"

  git -C "$ROOT_DIR" rev-parse HEAD > "$TMP_DIR/git_head.txt"

  for f in decision_log.txt operator_inputs.json active_run_status.txt checklist_status.txt execution_state.json git_head.txt; do
    mv "$TMP_DIR/$f" "$RUN_DIR/$f"
  done

  (
    cd "$RUN_DIR"
    find . -maxdepth 1 -type f | sed 's#^\./##' | sort > MANIFEST.txt
  )

  echo "EVIDENCE_RUN_DIR=$RUN_DIR"
  exit 1
fi

if [ "$run_result_lower" = "pass" ]; then
  checklist_live="PASS"
  checklist_post="PASS"
  exec_status="pass"
elif [ "$run_result_lower" = "failed" ]; then
  checklist_live="FAILED"
  checklist_post="RECORDED"
  exec_status="failed"
else
  checklist_live="BLOCKED"
  checklist_post="RECORDED"
  exec_status="blocked"
fi

{
  echo "STATUS=$(printf '%s' "$exec_status" | tr '[:lower:]' '[:upper:]')"
  echo "REASON=Real live pilot outcome recorded"
  echo "APPOINTMENT_REF=$PILOT_APPOINTMENT_REF"
  echo "CONSULTATION_REF=$PILOT_CONSULTATION_REF"
  echo "SIGNOFF_REF=$PILOT_SIGNOFF_REF"
  echo "PRESCRIPTION_REF=${PILOT_PRESCRIPTION_REF:-NONE_RECORDED}"
  echo "OWNER_CASE_REF=$PILOT_OWNER_CASE_1_REF"
  echo "CLINIC_NAME=$PILOT_CLINIC_NAME"
  echo "VET_NAME=$PILOT_VET_1_NAME"
} > "$TMP_DIR/active_run_status.txt"

{
  echo "Pre-Run: PASS"
  echo "Live Run: $checklist_live"
  echo "Post-Run: $checklist_post"
} > "$TMP_DIR/checklist_status.txt"

{
  printf '{\n'
  printf '  "status": "%s",\n' "$exec_status"
  printf '  "app_source_of_truth_commit": "%s",\n' "$APP_SOURCE_OF_TRUTH_COMMIT"
  printf '  "run_dir": "%s"\n' "$RUN_DIR"
  printf '}\n'
} > "$TMP_DIR/execution_state.json"

{
  echo "PH6 ACTIVE RUN SUMMARY"
  echo "app_source_of_truth_commit=$APP_SOURCE_OF_TRUTH_COMMIT"
  echo "pilot_operator=$PILOT_OPERATOR"
  echo "pilot_incident_channel=$PILOT_INCIDENT_CHANNEL"
  echo "pilot_approval_ref=$PILOT_APPROVAL_REF"
  echo "pilot_execution_window_utc=$PILOT_EXECUTION_WINDOW_UTC"
  echo "pilot_clinic_name=$PILOT_CLINIC_NAME"
  echo "pilot_clinic_license_ref=$PILOT_CLINIC_LICENSE_REF"
  echo "pilot_vet_1_name=$PILOT_VET_1_NAME"
  echo "pilot_vet_1_license_ref=$PILOT_VET_1_LICENSE_REF"
  echo "pilot_owner_case_1_ref=$PILOT_OWNER_CASE_1_REF"
  echo "pilot_production_url=$PILOT_PRODUCTION_URL"
  echo "pilot_appointment_ref=$PILOT_APPOINTMENT_REF"
  echo "pilot_consultation_ref=$PILOT_CONSULTATION_REF"
  echo "pilot_signoff_ref=$PILOT_SIGNOFF_REF"
  echo "pilot_prescription_ref=${PILOT_PRESCRIPTION_REF:-NONE_RECORDED}"
  echo "pilot_run_result=$PILOT_RUN_RESULT"
  echo "pilot_blockers=${PILOT_BLOCKERS:-NONE_RECORDED}"
  echo "pilot_operator_notes=$PILOT_OPERATOR_NOTES"
} > "$TMP_DIR/implementation_summary.txt"

git -C "$ROOT_DIR" rev-parse HEAD > "$TMP_DIR/git_head.txt"

for f in decision_log.txt operator_inputs.json active_run_status.txt checklist_status.txt execution_state.json implementation_summary.txt git_head.txt; do
  mv "$TMP_DIR/$f" "$RUN_DIR/$f"
done

(
  cd "$RUN_DIR"
  find . -maxdepth 1 -type f | sed 's#^\./##' | sort > MANIFEST.txt
)

echo "EVIDENCE_RUN_DIR=$RUN_DIR"
