#!/usr/bin/env bash
set -euo pipefail
DF34_DIR="petcare_execution/PHASE_3/DF34_MONITORING_ROLLBACK_GOVERNANCE"
REQUIRED_FILES=("DF34_LIVE_INTERACTION_MONITORING_MODEL.md" "DF34_ROLLBACK_KILLSWITCH_POLICY.md" "DF34_MONITORING_ROLLBACK_EVIDENCE_MODEL.md")
for file in "${REQUIRED_FILES[@]}"; do
  [ -f "$DF34_DIR/$file" ] || { echo "DF34 VALIDATION FAILED: missing $file"; exit 1; }
done
grep -q "rollback must remain available" "$DF34_DIR/DF34_LIVE_INTERACTION_MONITORING_MODEL.md"
grep -q "publication prohibited" "$DF34_DIR/DF34_ROLLBACK_KILLSWITCH_POLICY.md"
grep -q "every blocked output must still produce evidence" "$DF34_DIR/DF34_MONITORING_ROLLBACK_EVIDENCE_MODEL.md"
echo "DF34 VALIDATION PASSED"
