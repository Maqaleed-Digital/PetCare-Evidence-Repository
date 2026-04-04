#!/usr/bin/env bash
set -euo pipefail
DF33_DIR="petcare_execution/PHASE_3/DF33_LIMITED_PRODUCTION_ACCESS"
REQUIRED_FILES=("DF33_LIMITED_PRODUCTION_ACCESS_MODEL.md" "DF33_SCOPED_LIVE_ACCESS_POLICY.md" "DF33_LIMITED_PRODUCTION_EVIDENCE_MODEL.md")
for file in "${REQUIRED_FILES[@]}"; do
  [ -f "$DF33_DIR/$file" ] || { echo "DF33 VALIDATION FAILED: missing $file"; exit 1; }
done
grep -q "rollback must remain available" "$DF33_DIR/DF33_LIMITED_PRODUCTION_ACCESS_MODEL.md"
grep -q "publication prohibited" "$DF33_DIR/DF33_SCOPED_LIVE_ACCESS_POLICY.md"
grep -q "every blocked output must still produce evidence" "$DF33_DIR/DF33_LIMITED_PRODUCTION_EVIDENCE_MODEL.md"
echo "DF33 VALIDATION PASSED"
