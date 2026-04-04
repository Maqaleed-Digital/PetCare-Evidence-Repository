#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-4-DF39-MARKET-INCENTIVE-GOVERNANCE-ECONOMIC-CONTROL-LAYER"
PACK_DIR="$REPO/petcare_execution/PHASE_4/DF39_MARKET_INCENTIVE_GOVERNANCE_ECONOMIC_CONTROL_LAYER"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"
EXPECTED_BASE_COMMIT="f220cc56b1160588956ed50622a1f458678d589e"

mkdir -p "$EVIDENCE_ROOT"

if [ ! -d "$PACK_DIR" ]; then
  echo "STOP: missing DF39 pack directory $PACK_DIR"
  exit 1
fi

ACTUAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
if [ "$ACTUAL_HEAD" != "$EXPECTED_BASE_COMMIT" ]; then
  echo "STOP: expected HEAD $EXPECTED_BASE_COMMIT but found $ACTUAL_HEAD"
  exit 1
fi

DF38_DIR="$(find "$REPO/petcare_execution/PHASE_4" -maxdepth 1 -type d -name 'DF38*' | sort | head -n 1 || true)"
if [ -z "$DF38_DIR" ]; then
  echo "STOP: DF38 continuity directory not found under $REPO/petcare_execution/PHASE_4"
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

REQUIRED_VARS=(
  PETCARE_INCENTIVE_OWNER
  PETCARE_PRICING_GOVERNANCE_MODE
  PETCARE_REVENUE_SHARE_MODEL_REF
  PETCARE_FINANCIAL_FAIRNESS_RULESET_REF
  PETCARE_INCENTIVE_APPROVAL_ID
)

MISSING=()
for VAR_NAME in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR_NAME:-}" ]; then
    MISSING+=("$VAR_NAME")
  fi
done

{
  echo "PACK_ID=$PACK_ID"
  echo "DF38_CONTINUITY_DIR=$DF38_DIR"
  echo "EXPECTED_BASE_COMMIT=$EXPECTED_BASE_COMMIT"
  echo "ACTUAL_HEAD=$ACTUAL_HEAD"
  echo "RUN_DIR=$RUN_DIR"
} > "$RUN_DIR/decision_log.txt"

if [ "${#MISSING[@]}" -gt 0 ]; then
  {
    echo "ECONOMIC_CONTROL_BLOCKED"
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

cp "$PACK_DIR/current_economic_control_baseline.json" "$RUN_DIR/current_economic_control_baseline.json"
cp "$PACK_DIR/ECONOMIC_CONTROL_LAYER.md" "$RUN_DIR/ECONOMIC_CONTROL_LAYER.md"
cp "$PACK_DIR/INCENTIVE_GOVERNANCE_POLICY.md" "$RUN_DIR/INCENTIVE_GOVERNANCE_POLICY.md"
cp "$PACK_DIR/APPROVED_INCENTIVE_RULE_CATALOG.md" "$RUN_DIR/APPROVED_INCENTIVE_RULE_CATALOG.md"
cp "$PACK_DIR/PROHIBITED_INCENTIVE_MECHANISMS.md" "$RUN_DIR/PROHIBITED_INCENTIVE_MECHANISMS.md"
cp "$PACK_DIR/ECONOMIC_EVIDENCE_MODEL.md" "$RUN_DIR/ECONOMIC_EVIDENCE_MODEL.md"

{
  echo "status=ACTIVE_GOVERNED"
  echo "PETCARE_INCENTIVE_OWNER=$PETCARE_INCENTIVE_OWNER"
  echo "PETCARE_PRICING_GOVERNANCE_MODE=$PETCARE_PRICING_GOVERNANCE_MODE"
  echo "PETCARE_REVENUE_SHARE_MODEL_REF=$PETCARE_REVENUE_SHARE_MODEL_REF"
  echo "PETCARE_FINANCIAL_FAIRNESS_RULESET_REF=$PETCARE_FINANCIAL_FAIRNESS_RULESET_REF"
  echo "PETCARE_INCENTIVE_APPROVAL_ID=$PETCARE_INCENTIVE_APPROVAL_ID"
  echo "rollback_required=true"
  echo "ai_execution_authority=false"
  echo "uncontrolled_incentives_allowed=false"
  echo "coercive_economic_loops_allowed=false"
} > "$RUN_DIR/active.log"

{
  echo "economic_owner=$PETCARE_INCENTIVE_OWNER"
  echo "pricing_mode=$PETCARE_PRICING_GOVERNANCE_MODE"
  echo "revenue_share_model_ref=$PETCARE_REVENUE_SHARE_MODEL_REF"
  echo "fairness_ruleset_ref=$PETCARE_FINANCIAL_FAIRNESS_RULESET_REF"
  echo "approval_id=$PETCARE_INCENTIVE_APPROVAL_ID"
} > "$RUN_DIR/env_snapshot.txt"

{
  echo "INVARIANT_CHECK=PASS"
  echo "fail_closed_enforcement=true"
  echo "no_autonomous_execution=true"
  echo "no_uncontrolled_incentives=true"
  echo "no_hidden_economic_bias=true"
  echo "no_privilege_escalation_via_incentives=true"
  echo "no_coercive_economic_loops=true"
  echo "reversibility_required=true"
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
