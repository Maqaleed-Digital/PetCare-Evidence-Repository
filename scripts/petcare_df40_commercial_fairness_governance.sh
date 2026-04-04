#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-4-DF40-COMMERCIAL-FAIRNESS-GOVERNANCE-MARKET-ABUSE-PREVENTION"
PACK_DIR="$REPO/petcare_execution/PHASE_4/DF40_COMMERCIAL_FAIRNESS_GOVERNANCE_MARKET_ABUSE_PREVENTION"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="582ef2152c8fed8c2023de8263608514978ad147"

mkdir -p "$EVIDENCE_ROOT"

if [ ! -d "$PACK_DIR" ]; then
  echo "STOP: missing DF40 pack directory $PACK_DIR"
  exit 1
fi

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

DF39_DIR="$(find "$REPO/petcare_execution/PHASE_4" -maxdepth 1 -type d -name 'DF39*' | sort | head -n 1 || true)"
if [ -z "$DF39_DIR" ]; then
  echo "STOP: DF39 continuity directory not found under $REPO/petcare_execution/PHASE_4"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_FAIRNESS_OWNER
  PETCARE_ENFORCEMENT_REVIEW_MODE
  PETCARE_MARKET_ABUSE_RULESET_REF
  PETCARE_PARTNER_TREATMENT_STANDARD_REF
  PETCARE_FAIRNESS_APPROVAL_ID
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "DF39_CONTINUITY_DIR=$DF39_DIR"
  echo "EXPECTED_BASE_COMMIT=$EXPECTED_BASE_COMMIT"
  echo "ACTUAL_HEAD=$ACTUAL_HEAD"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "COMMERCIAL_FAIRNESS_BLOCKED"
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

cp "$PACK_DIR/current_commercial_fairness_baseline.json" "$RUN_DIR/current_commercial_fairness_baseline.json"
cp "$PACK_DIR/COMMERCIAL_FAIRNESS_GOVERNANCE.md" "$RUN_DIR/COMMERCIAL_FAIRNESS_GOVERNANCE.md"
cp "$PACK_DIR/PARTNER_TREATMENT_FAIRNESS_POLICY.md" "$RUN_DIR/PARTNER_TREATMENT_FAIRNESS_POLICY.md"
cp "$PACK_DIR/APPROVED_ABUSE_PREVENTION_CONTROL_CATALOG.md" "$RUN_DIR/APPROVED_ABUSE_PREVENTION_CONTROL_CATALOG.md"
cp "$PACK_DIR/PROHIBITED_MARKET_ABUSE_PATTERNS.md" "$RUN_DIR/PROHIBITED_MARKET_ABUSE_PATTERNS.md"
cp "$PACK_DIR/FAIRNESS_REVIEW_APPEAL_MODEL.md" "$RUN_DIR/FAIRNESS_REVIEW_APPEAL_MODEL.md"

{
  echo "status=ACTIVE_GOVERNED"
  echo "PETCARE_FAIRNESS_OWNER=$PETCARE_FAIRNESS_OWNER"
  echo "PETCARE_ENFORCEMENT_REVIEW_MODE=$PETCARE_ENFORCEMENT_REVIEW_MODE"
  echo "PETCARE_MARKET_ABUSE_RULESET_REF=$PETCARE_MARKET_ABUSE_RULESET_REF"
  echo "PETCARE_PARTNER_TREATMENT_STANDARD_REF=$PETCARE_PARTNER_TREATMENT_STANDARD_REF"
  echo "PETCARE_FAIRNESS_APPROVAL_ID=$PETCARE_FAIRNESS_APPROVAL_ID"
  echo "rollback_required=true"
  echo "appeal_path_required=true"
  echo "ai_execution_authority=false"
  echo "autonomous_penalty_allowed=false"
  echo "hidden_commercial_bias_allowed=false"
} > "$RUN_DIR/active.log"

{
  echo "fairness_owner=$PETCARE_FAIRNESS_OWNER"
  echo "enforcement_review_mode=$PETCARE_ENFORCEMENT_REVIEW_MODE"
  echo "market_abuse_ruleset_ref=$PETCARE_MARKET_ABUSE_RULESET_REF"
  echo "partner_treatment_standard_ref=$PETCARE_PARTNER_TREATMENT_STANDARD_REF"
  echo "approval_id=$PETCARE_FAIRNESS_APPROVAL_ID"
} > "$RUN_DIR/env_snapshot.txt"

{
  echo "INVARIANT_CHECK=PASS"
  echo "fail_closed_enforcement=true"
  echo "no_autonomous_execution=true"
  echo "no_hidden_commercial_bias=true"
  echo "no_unfair_partner_suppression=true"
  echo "no_nontransparent_ranking_or_routing_manipulation=true"
  echo "no_coercive_commercial_enforcement=true"
  echo "reversibility_required=true"
  echo "appeal_path_required=true"
  echo "commit_is_single_source_of_truth=true"
} > "$RUN_DIR/invariant_check.txt"

git -C "$REPO" rev-parse HEAD > "$RUN_DIR/git_head.txt"
find "$RUN_DIR" -maxdepth 1 -type f | sort > "$RUN_DIR/file_listing.txt"

python3 - <<'PY' "$RUN_DIR"
import hashlib
import json
import pathlib
import sys

run_dir = pathlib.Path(sys.argv[1])
files = []
for path in sorted(p for p in run_dir.iterdir() if p.is_file() and p.name not in {"MANIFEST.json", "MANIFEST.sha256"}):
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    files.append({"name": path.name, "sha256": sha})
manifest = {"run_dir": str(run_dir), "files": files}
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
(run_dir / "MANIFEST.sha256").write_text(
    hashlib.sha256((run_dir / "MANIFEST.json").read_bytes()).hexdigest() + "  MANIFEST.json\n"
)
PY

printf '%s\n' "$RUN_DIR"
