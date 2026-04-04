#!/usr/bin/env bash
set -euo pipefail

PHASE_DIR="petcare_execution/PHASE_2/DF29_ECOSYSTEM_EXPANSION"

REQUIRED_FILES=(
  "ECOSYSTEM_EXPANSION_READINESS_MODEL.md"
  "EXTERNAL_INTERACTION_BOUNDARY_POLICY.md"
  "ECOSYSTEM_INTERACTION_RULE_CATALOG.md"
  "GOVERNED_EXTERNAL_INTERACTION_EVIDENCE_MODEL.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$PHASE_DIR/$file" ]; then
    echo "DF29 VALIDATION FAILED: missing $file"
    exit 1
  fi
done

grep -q "no autonomous execution" "$PHASE_DIR/ECOSYSTEM_EXPANSION_READINESS_MODEL.md"
grep -q "publication prohibited" "$PHASE_DIR/EXTERNAL_INTERACTION_BOUNDARY_POLICY.md"
grep -q "PROHIBITED RULES" "$PHASE_DIR/ECOSYSTEM_INTERACTION_RULE_CATALOG.md"
grep -q "every blocked boundary output must still generate an evidence record" "$PHASE_DIR/GOVERNED_EXTERNAL_INTERACTION_EVIDENCE_MODEL.md"

echo "DF29 VALIDATION PASSED"
