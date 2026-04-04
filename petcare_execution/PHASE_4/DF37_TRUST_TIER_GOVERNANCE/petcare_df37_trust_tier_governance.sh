#!/usr/bin/env bash
set -euo pipefail

PHASE_DIR="petcare_execution/PHASE_4/DF37_TRUST_TIER_GOVERNANCE"

REQUIRED_FILES=(
  "DF37_TRUST_FRAMEWORK_MODEL.md"
  "DF37_PARTNER_TIER_GOVERNANCE_POLICY.md"
  "DF37_TRUST_TIER_RULE_CATALOG.md"
  "DF37_TRUST_TIER_EVIDENCE_MODEL.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$PHASE_DIR/$file" ]; then
    echo "DF37 VALIDATION FAILED: missing $file"
    exit 1
  fi
done

grep -q "trust must be evidence-backed" "$PHASE_DIR/DF37_TRUST_FRAMEWORK_MODEL.md"
grep -q "publication prohibited" "$PHASE_DIR/DF37_PARTNER_TIER_GOVERNANCE_POLICY.md"
grep -q "PROHIBITED RULES" "$PHASE_DIR/DF37_TRUST_TIER_RULE_CATALOG.md"
grep -q "every blocked output must still generate an evidence record" "$PHASE_DIR/DF37_TRUST_TIER_EVIDENCE_MODEL.md"

echo "DF37 VALIDATION PASSED"
