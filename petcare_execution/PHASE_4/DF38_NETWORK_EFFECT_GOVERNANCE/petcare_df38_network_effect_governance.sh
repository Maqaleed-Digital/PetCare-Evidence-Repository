#!/usr/bin/env bash
set -euo pipefail

PHASE_DIR="petcare_execution/PHASE_4/DF38_NETWORK_EFFECT_GOVERNANCE"

REQUIRED_FILES=(
  "DF38_NETWORK_EFFECT_MODEL.md"
  "DF38_VALUE_LOOP_CONTROL_POLICY.md"
  "DF38_NETWORK_RULE_CATALOG.md"
  "DF38_NETWORK_EVIDENCE_MODEL.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$PHASE_DIR/$file" ]; then
    echo "DF38 VALIDATION FAILED: missing $file"
    exit 1
  fi
done

grep -q "no coercive participation loops" "$PHASE_DIR/DF38_NETWORK_EFFECT_MODEL.md"
grep -q "PROHIBITED LOOPS" "$PHASE_DIR/DF38_VALUE_LOOP_CONTROL_POLICY.md"
grep -q "PROHIBITED RULES" "$PHASE_DIR/DF38_NETWORK_RULE_CATALOG.md"
grep -q "every blocked output must produce evidence" "$PHASE_DIR/DF38_NETWORK_EVIDENCE_MODEL.md"

echo "DF38 VALIDATION PASSED"
