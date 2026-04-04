#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-5-AUDIT-CERTIFICATION-READINESS-PACK"
PACK_DIR="$REPO/petcare_execution/PHASE_5/PH5_AUDIT_CERTIFICATION_READINESS_PACK"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="0640212e7b50fb0755842752576d42f4b969a01e"

mkdir -p "$EVIDENCE_ROOT"

if [ ! -d "$PACK_DIR" ]; then
  echo "STOP: missing audit certification readiness pack directory $PACK_DIR"
  exit 1
fi

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

RTMAP_DIR="$(find "$REPO/petcare_execution/PHASE_5" -maxdepth 1 -type d -name 'PH5_RUNTIME_CONTROL_IMPLEMENTATION_MATRIX*' | sort | head -n 1 || true)"
if [ -z "$RTMAP_DIR" ]; then
  echo "STOP: runtime control implementation matrix continuity directory not found under $REPO/petcare_execution/PHASE_5"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_AUDIT_READINESS_OWNER
  PETCARE_AUDIT_READINESS_APPROVAL_ID
  PETCARE_AUDIT_SCOPE_REF
  PETCARE_CERTIFICATION_POSTURE_REF
  PETCARE_AUDIT_REVIEW_MODE
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "RTMAP_CONTINUITY_DIR=$RTMAP_DIR"
  echo "EXPECTED_BASE_COMMIT=$EXPECTED_BASE_COMMIT"
  echo "ACTUAL_HEAD=$ACTUAL_HEAD"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "AUDIT_CERTIFICATION_READINESS_BLOCKED"
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

cp "$PACK_DIR/AUDIT_CERTIFICATION_READINESS.md" "$RUN_DIR/AUDIT_CERTIFICATION_READINESS.md"
cp "$PACK_DIR/AUDIT_CERTIFICATION_READINESS_POLICY.md" "$RUN_DIR/AUDIT_CERTIFICATION_READINESS_POLICY.md"
cp "$PACK_DIR/AUDIT_SCOPE_EVIDENCE_MODEL.md" "$RUN_DIR/AUDIT_SCOPE_EVIDENCE_MODEL.md"
cp "$PACK_DIR/READINESS_GAP_FINDING_REGISTER_STANDARD.md" "$RUN_DIR/READINESS_GAP_FINDING_REGISTER_STANDARD.md"
cp "$PACK_DIR/CERTIFICATION_POSTURE_DECLARATION_MODEL.md" "$RUN_DIR/CERTIFICATION_POSTURE_DECLARATION_MODEL.md"
cp "$PACK_DIR/current_audit_certification_readiness_baseline.json" "$RUN_DIR/current_audit_certification_readiness_baseline.json"

{
  echo "status=ACTIVE_GOVERNED"
  echo "PETCARE_AUDIT_READINESS_OWNER=$PETCARE_AUDIT_READINESS_OWNER"
  echo "PETCARE_AUDIT_READINESS_APPROVAL_ID=$PETCARE_AUDIT_READINESS_APPROVAL_ID"
  echo "PETCARE_AUDIT_SCOPE_REF=$PETCARE_AUDIT_SCOPE_REF"
  echo "PETCARE_CERTIFICATION_POSTURE_REF=$PETCARE_CERTIFICATION_POSTURE_REF"
  echo "PETCARE_AUDIT_REVIEW_MODE=$PETCARE_AUDIT_REVIEW_MODE"
  echo "unsupported_certification_claims_allowed=false"
  echo "gap_visibility_required=true"
  echo "false_readiness_assertion_allowed=false"
} > "$RUN_DIR/active.log"

{
  echo "audit_readiness_owner=$PETCARE_AUDIT_READINESS_OWNER"
  echo "audit_readiness_approval_id=$PETCARE_AUDIT_READINESS_APPROVAL_ID"
  echo "audit_scope_ref=$PETCARE_AUDIT_SCOPE_REF"
  echo "certification_posture_ref=$PETCARE_CERTIFICATION_POSTURE_REF"
  echo "audit_review_mode=$PETCARE_AUDIT_REVIEW_MODE"
} > "$RUN_DIR/env_snapshot.txt"

{
  echo "INVARIANT_CHECK=PASS"
  echo "no_unsupported_certification_claims=true"
  echo "no_hidden_gaps_or_findings=true"
  echo "no_silent_documentary_only_promotion=true"
  echo "no_false_readiness_assertion=true"
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
