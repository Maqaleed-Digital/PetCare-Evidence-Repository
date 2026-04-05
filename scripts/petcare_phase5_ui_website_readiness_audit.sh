#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-5-UI-WEBSITE-READINESS-AUDIT-PILOT-SURFACE-VALIDATION"
PACK_DIR="$REPO/petcare_execution/PHASE_5/PH5_UI_WEBSITE_READINESS_AUDIT_PILOT_SURFACE_VALIDATION"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_UI_OWNER
  PETCARE_UI_APPROVAL_ID
  PETCARE_UI_DEPLOYMENT_URL
  PETCARE_UI_VALIDATION_MODE
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

if [ "${#MISSING[@]}" -gt 0 ]; then
  echo "UI_BLOCKED" > "$RUN_DIR/blocked.log"
  printf '%s\n' "$RUN_DIR"
  exit 1
fi

echo "ACTIVE_GOVERNED" > "$RUN_DIR/active.log"

touch "$RUN_DIR/invariant_check.txt"
touch "$RUN_DIR/git_head.txt"
touch "$RUN_DIR/file_listing.txt"

printf '%s\n' "$RUN_DIR"
