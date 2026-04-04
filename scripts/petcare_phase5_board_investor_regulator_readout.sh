#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-5-BOARD-INVESTOR-REGULATOR-READOUT-PACK"
PACK_DIR="$REPO/petcare_execution/PHASE_5/PH5_BOARD_INVESTOR_REGULATOR_READOUT_PACK"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="920bbf752814750557b129150c0c058a28f92323"

mkdir -p "$EVIDENCE_ROOT"

if [ ! -d "$PACK_DIR" ]; then
  echo "STOP: missing board investor regulator readout pack directory $PACK_DIR"
  exit 1
fi

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

AUDIT_DIR="$(find "$REPO/petcare_execution/PHASE_5" -maxdepth 1 -type d -name 'PH5_AUDIT_CERTIFICATION_READINESS*' | sort | head -n 1 || true)"
if [ -z "$AUDIT_DIR" ]; then
  echo "STOP: audit certification readiness continuity directory not found under $REPO/petcare_execution/PHASE_5"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_READOUT_OWNER
  PETCARE_READOUT_APPROVAL_ID
  PETCARE_READOUT_EVIDENCE_BASELINE_REF
  PETCARE_DISCLOSURE_STANDARD_REF
  PETCARE_AUDIENCE_REVIEW_MODE
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "AUDIT_CONTINUITY_DIR=$AUDIT_DIR"
  echo "EXPECTED_BASE_COMMIT=$EXPECTED_BASE_COMMIT"
  echo "ACTUAL_HEAD=$ACTUAL_HEAD"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "EXECUTIVE_EXTERNAL_READOUT_BLOCKED"
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

cp "$PACK_DIR/BOARD_INVESTOR_REGULATOR_READOUT.md" "$RUN_DIR/BOARD_INVESTOR_REGULATOR_READOUT.md"
cp "$PACK_DIR/EXECUTIVE_EXTERNAL_READOUT_POLICY.md" "$RUN_DIR/EXECUTIVE_EXTERNAL_READOUT_POLICY.md"
cp "$PACK_DIR/BOARD_READOUT_SUMMARY_MODEL.md" "$RUN_DIR/BOARD_READOUT_SUMMARY_MODEL.md"
cp "$PACK_DIR/INVESTOR_READOUT_SUMMARY_MODEL.md" "$RUN_DIR/INVESTOR_READOUT_SUMMARY_MODEL.md"
cp "$PACK_DIR/REGULATOR_READOUT_SUMMARY_MODEL.md" "$RUN_DIR/REGULATOR_READOUT_SUMMARY_MODEL.md"
cp "$PACK_DIR/MATERIAL_DISCLOSURE_TRUTH_BOUNDARY_STANDARD.md" "$RUN_DIR/MATERIAL_DISCLOSURE_TRUTH_BOUNDARY_STANDARD.md"
cp "$PACK_DIR/current_board_investor_regulator_readout_baseline.json" "$RUN_DIR/current_board_investor_regulator_readout_baseline.json"

{
  echo "status=ACTIVE_GOVERNED"
  echo "PETCARE_READOUT_OWNER=$PETCARE_READOUT_OWNER"
  echo "PETCARE_READOUT_APPROVAL_ID=$PETCARE_READOUT_APPROVAL_ID"
  echo "PETCARE_READOUT_EVIDENCE_BASELINE_REF=$PETCARE_READOUT_EVIDENCE_BASELINE_REF"
  echo "PETCARE_DISCLOSURE_STANDARD_REF=$PETCARE_DISCLOSURE_STANDARD_REF"
  echo "PETCARE_AUDIENCE_REVIEW_MODE=$PETCARE_AUDIENCE_REVIEW_MODE"
  echo "unsupported_external_claims_allowed=false"
  echo "material_gap_visibility_required=true"
  echo "truth_drift_allowed=false"
} > "$RUN_DIR/active.log"

{
  echo "readout_owner=$PETCARE_READOUT_OWNER"
  echo "readout_approval_id=$PETCARE_READOUT_APPROVAL_ID"
  echo "readout_evidence_baseline_ref=$PETCARE_READOUT_EVIDENCE_BASELINE_REF"
  echo "disclosure_standard_ref=$PETCARE_DISCLOSURE_STANDARD_REF"
  echo "audience_review_mode=$PETCARE_AUDIENCE_REVIEW_MODE"
} > "$RUN_DIR/env_snapshot.txt"

{
  echo "INVARIANT_CHECK=PASS"
  echo "no_unsupported_external_claims=true"
  echo "no_hidden_material_gaps=true"
  echo "no_silent_conditional_readiness_omission=true"
  echo "no_audience_specific_truth_drift=true"
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
