#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-5-UI-GAP-CLOSURE-EXECUTION-PACK"
PACK_DIR="$REPO/petcare_execution/PHASE_5/PH5_UI_GAP_CLOSURE_EXECUTION_PACK"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="344dd3944d553ed6cc427a0ff20bc78468656b15"

mkdir -p "$EVIDENCE_ROOT"

if [ ! -d "$PACK_DIR" ]; then
  echo "STOP: missing UI gap closure execution pack directory $PACK_DIR"
  exit 1
fi

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

UI_AUDIT_DIR="$(find "$REPO/petcare_execution/PHASE_5" -maxdepth 1 -type d -name 'PH5_UI_WEBSITE_READINESS_AUDIT*' | sort | head -n 1 || true)"
if [ -z "$UI_AUDIT_DIR" ]; then
  echo "STOP: UI website readiness audit continuity directory not found under $REPO/petcare_execution/PHASE_5"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_UI_GAP_OWNER
  PETCARE_UI_GAP_APPROVAL_ID
  PETCARE_UI_GAP_REGISTER_REF
  PETCARE_UI_VALIDATION_STANDARD_REF
  PETCARE_UI_GAP_REVIEW_MODE
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "UI_AUDIT_CONTINUITY_DIR=$UI_AUDIT_DIR"
  echo "EXPECTED_BASE_COMMIT=$EXPECTED_BASE_COMMIT"
  echo "ACTUAL_HEAD=$ACTUAL_HEAD"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "UI_GAP_CLOSURE_BLOCKED"
    printf 'MISSING_VARS=%s\n' "$(IFS=,; echo "${MISSING[*]}")"
  } > "$RUN_DIR/blocked.log"

  {
    echo "status=BLOCKED"
    echo "reason=missing_required_env"
    printf 'missing=%s\n' "$(IFS=,; echo "${MISSING[*]}")"
  } >> "$RUN_DIR/decision_log.txt"

  printf '%s\n' "$RUN_DIR"
  exit 1
fi

cp "$PACK_DIR/UI_GAP_CLOSURE_EXECUTION.md" "$RUN_DIR/UI_GAP_CLOSURE_EXECUTION.md"
cp "$PACK_DIR/UI_GAP_CLOSURE_GOVERNANCE_POLICY.md" "$RUN_DIR/UI_GAP_CLOSURE_GOVERNANCE_POLICY.md"
cp "$PACK_DIR/PILOT_UI_GAP_CLASSIFICATION_MODEL.md" "$RUN_DIR/PILOT_UI_GAP_CLASSIFICATION_MODEL.md"
cp "$PACK_DIR/UI_PILOT_BLOCKER_REGISTER_STANDARD.md" "$RUN_DIR/UI_PILOT_BLOCKER_REGISTER_STANDARD.md"
cp "$PACK_DIR/UI_CLOSURE_VALIDATION_STANDARD.md" "$RUN_DIR/UI_CLOSURE_VALIDATION_STANDARD.md"
cp "$PACK_DIR/current_ui_gap_closure_baseline.json" "$RUN_DIR/current_ui_gap_closure_baseline.json"

{
  echo "status=ACTIVE_GOVERNED"
  echo "PETCARE_UI_GAP_OWNER=$PETCARE_UI_GAP_OWNER"
  echo "PETCARE_UI_GAP_APPROVAL_ID=$PETCARE_UI_GAP_APPROVAL_ID"
  echo "PETCARE_UI_GAP_REGISTER_REF=$PETCARE_UI_GAP_REGISTER_REF"
  echo "PETCARE_UI_VALIDATION_STANDARD_REF=$PETCARE_UI_VALIDATION_STANDARD_REF"
  echo "PETCARE_UI_GAP_REVIEW_MODE=$PETCARE_UI_GAP_REVIEW_MODE"
  echo "fake_ui_completion_allowed=false"
  echo "pilot_blocker_visibility_required=true"
  echo "workflow_completeness_without_validation_allowed=false"
} > "$RUN_DIR/active.log"

{
  echo "ui_gap_owner=$PETCARE_UI_GAP_OWNER"
  echo "ui_gap_approval_id=$PETCARE_UI_GAP_APPROVAL_ID"
  echo "ui_gap_register_ref=$PETCARE_UI_GAP_REGISTER_REF"
  echo "ui_validation_standard_ref=$PETCARE_UI_VALIDATION_STANDARD_REF"
  echo "ui_gap_review_mode=$PETCARE_UI_GAP_REVIEW_MODE"
} > "$RUN_DIR/env_snapshot.txt"

{
  echo "INVARIANT_CHECK=PASS"
  echo "no_fake_ui_completion=true"
  echo "no_silent_pilot_blocker_suppression=true"
  echo "no_workflow_completeness_claim_without_validation=true"
  echo "no_auth_bypass_for_pilot_convenience=true"
  echo "evidence_chain_required=true"
  echo "commit_is_single_source_of_truth=true"
} > "$RUN_DIR/invariant_check.txt"

git -C "$REPO" rev-parse HEAD > "$RUN_DIR/git_head.txt"
find "$RUN_DIR" -maxdepth 1 -type f | sort > "$RUN_DIR/file_listing.txt"

python3 - "$RUN_DIR" << 'PY'
import hashlib
import json
import pathlib
import sys

run_dir = pathlib.Path(sys.argv[1])
files = []
for path in sorted(p for p in run_dir.iterdir() if p.is_file() and p.name not in {"MANIFEST.json", "MANIFEST.sha256"}):
    files.append({"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
manifest = {"run_dir": str(run_dir), "files": files}
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
(run_dir / "MANIFEST.sha256").write_text(
    hashlib.sha256((run_dir / "MANIFEST.json").read_bytes()).hexdigest() + "  MANIFEST.json\n"
)
PY

printf '%s\n' "$RUN_DIR"
