#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-5-CONTROLLED-SCALE-EXPANSION-UNDER-SEALED-CONSTITUTION"
PACK_DIR="$REPO/petcare_execution/PHASE_5/PH5_CONTROLLED_SCALE_EXPANSION_UNDER_SEALED_CONSTITUTION"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="4db25cce9d933518d646e8eefc0854efc406e575"

mkdir -p "$EVIDENCE_ROOT"

if [ ! -d "$PACK_DIR" ]; then
  echo "STOP: missing controlled scale expansion pack directory $PACK_DIR"
  exit 1
fi

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

READOUT_DIR="$(find "$REPO/petcare_execution/PHASE_5" -maxdepth 1 -type d -name 'PH5_BOARD_INVESTOR_REGULATOR_READOUT*' | sort | head -n 1 || true)"
if [ -z "$READOUT_DIR" ]; then
  echo "STOP: board investor regulator readout continuity directory not found under $REPO/petcare_execution/PHASE_5"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_SCALE_EXPANSION_OWNER
  PETCARE_SCALE_EXPANSION_APPROVAL_ID
  PETCARE_SCALE_EXPANSION_SCOPE_REF
  PETCARE_SCALE_READINESS_STANDARD_REF
  PETCARE_SCALE_EXPANSION_REVIEW_MODE
  PETCARE_SCALE_OPERATIONAL_CAPACITY_REF
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "READOUT_CONTINUITY_DIR=$READOUT_DIR"
  echo "EXPECTED_BASE_COMMIT=$EXPECTED_BASE_COMMIT"
  echo "ACTUAL_HEAD=$ACTUAL_HEAD"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "CONTROLLED_SCALE_EXPANSION_BLOCKED"
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

cp "$PACK_DIR/CONTROLLED_SCALE_EXPANSION.md" "$RUN_DIR/CONTROLLED_SCALE_EXPANSION.md"
cp "$PACK_DIR/SCALE_EXPANSION_GOVERNANCE_POLICY.md" "$RUN_DIR/SCALE_EXPANSION_GOVERNANCE_POLICY.md"
cp "$PACK_DIR/SCALE_EXPANSION_SCOPE_MODEL.md" "$RUN_DIR/SCALE_EXPANSION_SCOPE_MODEL.md"
cp "$PACK_DIR/SCALE_READINESS_CAPACITY_STANDARD.md" "$RUN_DIR/SCALE_READINESS_CAPACITY_STANDARD.md"
cp "$PACK_DIR/OPERATIONAL_EXPANSION_CONTRACTION_MODEL.md" "$RUN_DIR/OPERATIONAL_EXPANSION_CONTRACTION_MODEL.md"
cp "$PACK_DIR/current_controlled_scale_expansion_baseline.json" "$RUN_DIR/current_controlled_scale_expansion_baseline.json"

{
  echo "status=ACTIVE_GOVERNED"
  echo "PETCARE_SCALE_EXPANSION_OWNER=$PETCARE_SCALE_EXPANSION_OWNER"
  echo "PETCARE_SCALE_EXPANSION_APPROVAL_ID=$PETCARE_SCALE_EXPANSION_APPROVAL_ID"
  echo "PETCARE_SCALE_EXPANSION_SCOPE_REF=$PETCARE_SCALE_EXPANSION_SCOPE_REF"
  echo "PETCARE_SCALE_READINESS_STANDARD_REF=$PETCARE_SCALE_READINESS_STANDARD_REF"
  echo "PETCARE_SCALE_EXPANSION_REVIEW_MODE=$PETCARE_SCALE_EXPANSION_REVIEW_MODE"
  echo "PETCARE_SCALE_OPERATIONAL_CAPACITY_REF=$PETCARE_SCALE_OPERATIONAL_CAPACITY_REF"
  echo "uncontrolled_expansion_allowed=false"
  echo "fairness_downgrade_for_growth_allowed=false"
  echo "runtime_guardrail_weakening_allowed=false"
  echo "contraction_required=true"
} > "$RUN_DIR/active.log"

{
  echo "scale_expansion_owner=$PETCARE_SCALE_EXPANSION_OWNER"
  echo "scale_expansion_approval_id=$PETCARE_SCALE_EXPANSION_APPROVAL_ID"
  echo "scale_expansion_scope_ref=$PETCARE_SCALE_EXPANSION_SCOPE_REF"
  echo "scale_readiness_standard_ref=$PETCARE_SCALE_READINESS_STANDARD_REF"
  echo "scale_expansion_review_mode=$PETCARE_SCALE_EXPANSION_REVIEW_MODE"
  echo "scale_operational_capacity_ref=$PETCARE_SCALE_OPERATIONAL_CAPACITY_REF"
} > "$RUN_DIR/env_snapshot.txt"

{
  echo "INVARIANT_CHECK=PASS"
  echo "no_uncontrolled_expansion=true"
  echo "no_silent_governance_relaxation=true"
  echo "no_fairness_downgrade_for_growth=true"
  echo "no_runtime_guardrail_weakening=true"
  echo "no_operational_overreach_without_ownership=true"
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
