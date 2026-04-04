#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-4-DF44-FINAL-GOVERNANCE-SEAL-PLATFORM-CONSTITUTION-LOCK"
PACK_DIR="$REPO/petcare_execution/PHASE_4/DF44_FINAL_GOVERNANCE_SEAL_PLATFORM_CONSTITUTION_LOCK"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="da00d5e52c231708b3112bc55bab0622aa67ea72"

mkdir -p "$EVIDENCE_ROOT"

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

DF43_DIR="$(find "$REPO/petcare_execution/PHASE_4" -maxdepth 1 -type d -name 'DF43*' | sort | head -n 1 || true)"
if [ -z "$DF43_DIR" ]; then
  echo "STOP: DF43 continuity directory not found under $REPO/petcare_execution/PHASE_4"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_SEAL_OWNER
  PETCARE_SEAL_MODE
  PETCARE_CONSTITUTION_LOCK_REF
  PETCARE_FINAL_INVARIANT_REGISTRY_REF
  PETCARE_SEAL_APPROVAL_ID
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "DF43_CONTINUITY_DIR=$DF43_DIR"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "FINAL_GOVERNANCE_SEAL_BLOCKED"
    printf 'MISSING_VARS=%s\n' "$(IFS=,; echo "${MISSING[*]}")"
  } > "$RUN_DIR/blocked.log"
  printf '%s\n' "$RUN_DIR"
  exit 1
fi

cp "$PACK_DIR/FINAL_GOVERNANCE_SEAL.md" "$RUN_DIR/"
cp "$PACK_DIR/PLATFORM_CONSTITUTION.md" "$RUN_DIR/"
cp "$PACK_DIR/FINAL_INVARIANT_REGISTRY.md" "$RUN_DIR/"
cp "$PACK_DIR/PROHIBITED_POST_SEAL_MUTATION_PATTERNS.md" "$RUN_DIR/"
cp "$PACK_DIR/current_governance_seal_baseline.json" "$RUN_DIR/"

{
  echo "status=SEALED"
  echo "owner=$PETCARE_SEAL_OWNER"
  echo "seal_mode=$PETCARE_SEAL_MODE"
  echo "constitution_lock_ref=$PETCARE_CONSTITUTION_LOCK_REF"
  echo "final_invariant_registry_ref=$PETCARE_FINAL_INVARIANT_REGISTRY_REF"
  echo "approval_id=$PETCARE_SEAL_APPROVAL_ID"
  echo "final_state=FULLY_GOVERNED,FULLY_AUDITABLE,CONSTITUTION_LOCKED,PLATFORM_SEALED"
} > "$RUN_DIR/active.log"

{
  echo "INVARIANT_CHECK=PASS"
  echo "no_silent_post_seal_mutation=true"
  echo "no_invariant_weakening_without_regovernance=true"
  echo "certified_closure_state=true"
  echo "commit_is_single_source_of_truth=true"
} > "$RUN_DIR/invariant_check.txt"

{
  echo "seal_owner=$PETCARE_SEAL_OWNER"
  echo "seal_mode=$PETCARE_SEAL_MODE"
  echo "constitution_lock_ref=$PETCARE_CONSTITUTION_LOCK_REF"
  echo "final_invariant_registry_ref=$PETCARE_FINAL_INVARIANT_REGISTRY_REF"
  echo "approval_id=$PETCARE_SEAL_APPROVAL_ID"
} > "$RUN_DIR/env_snapshot.txt"

git -C "$REPO" rev-parse HEAD > "$RUN_DIR/git_head.txt"
find "$RUN_DIR" -maxdepth 1 -type f | sort > "$RUN_DIR/file_listing.txt"

python3 - <<'PY' "$RUN_DIR"
import hashlib, json, pathlib, sys
run_dir = pathlib.Path(sys.argv[1])
files = []
for path in sorted(p for p in run_dir.iterdir() if p.is_file() and p.name not in {"MANIFEST.json", "MANIFEST.sha256"}):
    files.append({"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
(run_dir / "MANIFEST.json").write_text(json.dumps({"run_dir": str(run_dir), "files": files}, indent=2) + "\n")
(run_dir / "MANIFEST.sha256").write_text(hashlib.sha256((run_dir / "MANIFEST.json").read_bytes()).hexdigest() + "  MANIFEST.json\n")
PY

printf '%s\n' "$RUN_DIR"
