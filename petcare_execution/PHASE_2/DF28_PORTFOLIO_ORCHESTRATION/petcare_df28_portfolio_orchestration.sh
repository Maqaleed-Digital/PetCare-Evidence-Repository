#!/usr/bin/env bash
set -euo pipefail

PHASE_DIR="petcare_execution/PHASE_2/DF28_PORTFOLIO_ORCHESTRATION"

REQUIRED_FILES=(
  "PORTFOLIO_ORCHESTRATION_MODEL.md"
  "CROSS_UNIT_OPTIMIZATION_CONTROL_POLICY.md"
  "PORTFOLIO_ORCHESTRATION_RULE_CATALOG.md"
  "GOVERNED_OPTIMIZATION_EVIDENCE_MODEL.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$PHASE_DIR/$file" ]; then
    echo "DF28 VALIDATION FAILED: missing $file"
    exit 1
  fi
done

grep -q "no autonomous execution" "$PHASE_DIR/PORTFOLIO_ORCHESTRATION_MODEL.md"
grep -q "optimization publication prohibited" "$PHASE_DIR/CROSS_UNIT_OPTIMIZATION_CONTROL_POLICY.md"
grep -q "PROHIBITED RULES" "$PHASE_DIR/PORTFOLIO_ORCHESTRATION_RULE_CATALOG.md"
grep -q "every blocked optimization output must still generate an evidence record" "$PHASE_DIR/GOVERNED_OPTIMIZATION_EVIDENCE_MODEL.md"

echo "DF28 VALIDATION PASSED"
