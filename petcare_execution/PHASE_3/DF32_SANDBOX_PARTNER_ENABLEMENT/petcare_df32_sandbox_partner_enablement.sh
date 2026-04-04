#!/usr/bin/env bash
set -euo pipefail
DF32_DIR="petcare_execution/PHASE_3/DF32_SANDBOX_PARTNER_ENABLEMENT"
REQUIRED_FILES=("DF32_SANDBOX_PARTNER_ENABLEMENT_MODEL.md" "DF32_SANDBOX_ISOLATION_CONTROL_POLICY.md" "DF32_SANDBOX_PARTNER_EVIDENCE_MODEL.md")
for file in "${REQUIRED_FILES[@]}"; do
  [ -f "$DF32_DIR/$file" ] || { echo "DF32 VALIDATION FAILED: missing $file"; exit 1; }
done
grep -q "no production data" "$DF32_DIR/DF32_SANDBOX_PARTNER_ENABLEMENT_MODEL.md"
grep -q "publication prohibited" "$DF32_DIR/DF32_SANDBOX_ISOLATION_CONTROL_POLICY.md"
grep -q "every blocked output must still produce evidence" "$DF32_DIR/DF32_SANDBOX_PARTNER_EVIDENCE_MODEL.md"
echo "DF32 VALIDATION PASSED"
