#!/usr/bin/env bash
set -euo pipefail

PHASE_DIR="petcare_execution/PHASE_2/DF27_PORTFOLIO_INTELLIGENCE"

REQUIRED_FILES=(
  "PORTFOLIO_INTELLIGENCE_MODEL.md"
  "CROSS_UNIT_VISIBILITY_POLICY.md"
  "PORTFOLIO_SIGNAL_CATALOG.md"
  "GOVERNED_VISIBILITY_EVIDENCE_MODEL.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$PHASE_DIR/$file" ]; then
    echo "DF27 VALIDATION FAILED: missing $file"
    exit 1
  fi
done

grep -q "no autonomous execution" "$PHASE_DIR/PORTFOLIO_INTELLIGENCE_MODEL.md"
grep -q "publication prohibited" "$PHASE_DIR/CROSS_UNIT_VISIBILITY_POLICY.md"
grep -q "PROHIBITED SIGNALS" "$PHASE_DIR/PORTFOLIO_SIGNAL_CATALOG.md"
grep -q "every blocked output must still produce an evidence record" "$PHASE_DIR/GOVERNED_VISIBILITY_EVIDENCE_MODEL.md"

echo "DF27 VALIDATION PASSED"
