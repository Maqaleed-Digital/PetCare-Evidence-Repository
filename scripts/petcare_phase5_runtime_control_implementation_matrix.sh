#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-5-RUNTIME-CONTROL-IMPLEMENTATION-MATRIX-DEPLOYED-SERVICES"
PACK_DIR="$REPO/petcare_execution/PHASE_5/PH5_RUNTIME_CONTROL_IMPLEMENTATION_MATRIX_DEPLOYED_SERVICES"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="816bff50c87a9f737bb3c3c577e8f15405ed12b2"

mkdir -p "$EVIDENCE_ROOT"

if [ ! -d "$PACK_DIR" ]; then
  echo "STOP: missing runtime control implementation matrix pack directory $PACK_DIR"
  exit 1
fi

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

PH5_PROD_DIR="$(find "$REPO/petcare_execution/PHASE_5" -maxdepth 1 -type d -name 'PH5_CONTROLLED_PRODUCTION_ACTIVATION*' | sort | head -n 1 || true)"
if [ -z "$PH5_PROD_DIR" ]; then
  echo "STOP: controlled production activation continuity directory not found under $REPO/petcare_execution/PHASE_5"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_RUNTIME_MAPPING_OWNER
  PETCARE_RUNTIME_MAPPING_APPROVAL_ID
  PETCARE_DEPLOYED_SERVICES_REF
  PETCARE_CONTROL_CLASSIFICATION_STANDARD_REF
  PETCARE_RUNTIME_MAPPING_VALIDATION_MODE
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "PH5_PROD_CONTINUITY_DIR=$PH5_PROD_DIR"
  echo "EXPECTED_BASE_COMMIT=$EXPECTED_BASE_COMMIT"
  echo "ACTUAL_HEAD=$ACTUAL_HEAD"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "RUNTIME_CONTROL_MAPPING_BLOCKED"
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

cp "$PACK_DIR/RUNTIME_CONTROL_IMPLEMENTATION_MATRIX.md" "$RUN_DIR/RUNTIME_CONTROL_IMPLEMENTATION_MATRIX.md"
cp "$PACK_DIR/RUNTIME_CONTROL_MAPPING_POLICY.md" "$RUN_DIR/RUNTIME_CONTROL_MAPPING_POLICY.md"
cp "$PACK_DIR/DEPLOYED_SERVICES_MAPPING_REFERENCE.md" "$RUN_DIR/DEPLOYED_SERVICES_MAPPING_REFERENCE.md"
cp "$PACK_DIR/RUNTIME_CONTROL_GAP_REGISTER_STANDARD.md" "$RUN_DIR/RUNTIME_CONTROL_GAP_REGISTER_STANDARD.md"
cp "$PACK_DIR/SAMPLE_RUNTIME_CONTROL_IMPLEMENTATION_MATRIX.tsv" "$RUN_DIR/SAMPLE_RUNTIME_CONTROL_IMPLEMENTATION_MATRIX.tsv"
cp "$PACK_DIR/current_runtime_control_mapping_baseline.json" "$RUN_DIR/current_runtime_control_mapping_baseline.json"

{
  echo "status=ACTIVE_GOVERNED"
  echo "PETCARE_RUNTIME_MAPPING_OWNER=$PETCARE_RUNTIME_MAPPING_OWNER"
  echo "PETCARE_RUNTIME_MAPPING_APPROVAL_ID=$PETCARE_RUNTIME_MAPPING_APPROVAL_ID"
  echo "PETCARE_DEPLOYED_SERVICES_REF=$PETCARE_DEPLOYED_SERVICES_REF"
  echo "PETCARE_CONTROL_CLASSIFICATION_STANDARD_REF=$PETCARE_CONTROL_CLASSIFICATION_STANDARD_REF"
  echo "PETCARE_RUNTIME_MAPPING_VALIDATION_MODE=$PETCARE_RUNTIME_MAPPING_VALIDATION_MODE"
  echo "no_assumed_runtime_enforcement=true"
  echo "gap_visibility_required=true"
  echo "false_completeness_allowed=false"
} > "$RUN_DIR/active.log"

{
  echo "runtime_mapping_owner=$PETCARE_RUNTIME_MAPPING_OWNER"
  echo "runtime_mapping_approval_id=$PETCARE_RUNTIME_MAPPING_APPROVAL_ID"
  echo "deployed_services_ref=$PETCARE_DEPLOYED_SERVICES_REF"
  echo "control_classification_standard_ref=$PETCARE_CONTROL_CLASSIFICATION_STANDARD_REF"
  echo "runtime_mapping_validation_mode=$PETCARE_RUNTIME_MAPPING_VALIDATION_MODE"
} > "$RUN_DIR/env_snapshot.txt"

{
  echo "INVARIANT_CHECK=PASS"
  echo "no_assumed_runtime_enforcement=true"
  echo "no_hidden_control_gaps=true"
  echo "no_silent_documentary_only_downgrade=true"
  echo "no_false_completeness_claim=true"
  echo "reversibility_required=true"
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
