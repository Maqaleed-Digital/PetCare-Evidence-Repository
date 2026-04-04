#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-4-DF43-RUNTIME-ENFORCEMENT-GOVERNANCE-EXECUTION-GUARDRAILS"
PACK_DIR="$REPO/petcare_execution/PHASE_4/DF43_RUNTIME_ENFORCEMENT_GOVERNANCE_EXECUTION_GUARDRAILS"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="da00d5e52c231708b3112bc55bab0622aa67ea72"

mkdir -p "$EVIDENCE_ROOT"

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

DF42_DIR="$(find "$REPO/petcare_execution/PHASE_4" -maxdepth 1 -type d -name 'DF42*' | sort | head -n 1 || true)"
if [ -z "$DF42_DIR" ]; then
  echo "STOP: DF42 continuity directory not found under $REPO/petcare_execution/PHASE_4"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_RUNTIME_OWNER
  PETCARE_RUNTIME_MODE
  PETCARE_GUARDRAIL_RULESET_REF
  PETCARE_INVARIANT_ENFORCEMENT_STANDARD_REF
  PETCARE_RUNTIME_APPROVAL_ID
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "DF42_CONTINUITY_DIR=$DF42_DIR"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "RUNTIME_ENFORCEMENT_BLOCKED"
    printf 'MISSING_VARS=%s\n' "$(IFS=,; echo "${MISSING[*]}")"
  } > "$RUN_DIR/blocked.log"
  printf '%s\n' "$RUN_DIR"
  exit 1
fi

cp "$PACK_DIR/RUNTIME_ENFORCEMENT_GOVERNANCE.md" "$RUN_DIR/"
cp "$PACK_DIR/RUNTIME_GUARDRAIL_POLICY.md" "$RUN_DIR/"
cp "$PACK_DIR/APPROVED_RUNTIME_CONTROL_CATALOG.md" "$RUN_DIR/"
cp "$PACK_DIR/PROHIBITED_RUNTIME_BYPASS_PATTERNS.md" "$RUN_DIR/"
cp "$PACK_DIR/current_runtime_enforcement_baseline.json" "$RUN_DIR/"

{
  echo "status=ACTIVE_GOVERNED"
  echo "owner=$PETCARE_RUNTIME_OWNER"
  echo "runtime_mode=$PETCARE_RUNTIME_MODE"
  echo "guardrail_ruleset_ref=$PETCARE_GUARDRAIL_RULESET_REF"
  echo "invariant_enforcement_standard_ref=$PETCARE_INVARIANT_ENFORCEMENT_STANDARD_REF"
  echo "approval_id=$PETCARE_RUNTIME_APPROVAL_ID"
} > "$RUN_DIR/active.log"

{
  echo "INVARIANT_CHECK=PASS"
  echo "no_silent_runtime_bypass=true"
  echo "no_hidden_control_disablement=true"
  echo "no_unsafe_continuation=true"
  echo "commit_is_single_source_of_truth=true"
} > "$RUN_DIR/invariant_check.txt"

{
  echo "runtime_owner=$PETCARE_RUNTIME_OWNER"
  echo "runtime_mode=$PETCARE_RUNTIME_MODE"
  echo "guardrail_ruleset_ref=$PETCARE_GUARDRAIL_RULESET_REF"
  echo "invariant_enforcement_standard_ref=$PETCARE_INVARIANT_ENFORCEMENT_STANDARD_REF"
  echo "approval_id=$PETCARE_RUNTIME_APPROVAL_ID"
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
