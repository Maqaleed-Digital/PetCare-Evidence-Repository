#!/usr/bin/env bash
set -euo pipefail
DF36_DIR="petcare_execution/PHASE_3/DF36_MULTI_PARTNER_SCALE"
REQUIRED_FILES=("DF36_MULTI_PARTNER_SCALE_MODEL.md" "DF36_MULTI_PARTNER_GOVERNANCE_POLICY.md" "DF36_MULTI_PARTNER_SCALE_EVIDENCE_MODEL.md")
for file in "${REQUIRED_FILES[@]}"; do
  [ -f "$DF36_DIR/$file" ] || { echo "DF36 VALIDATION FAILED: missing $file"; exit 1; }
done
grep -q "scale must remain governed" "$DF36_DIR/DF36_MULTI_PARTNER_SCALE_MODEL.md"
grep -q "publication prohibited" "$DF36_DIR/DF36_MULTI_PARTNER_GOVERNANCE_POLICY.md"
grep -q "every blocked output must still produce evidence" "$DF36_DIR/DF36_MULTI_PARTNER_SCALE_EVIDENCE_MODEL.md"
echo "DF36 VALIDATION PASSED"
