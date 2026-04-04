#!/usr/bin/env bash
set -euo pipefail
DF35_DIR="petcare_execution/PHASE_3/DF35_TRUST_CERTIFICATION"
REQUIRED_FILES=("DF35_PARTNER_TRUST_POSTURE_MODEL.md" "DF35_CERTIFICATION_READINESS_POLICY.md" "DF35_TRUST_CERTIFICATION_EVIDENCE_MODEL.md")
for file in "${REQUIRED_FILES[@]}"; do
  [ -f "$DF35_DIR/$file" ] || { echo "DF35 VALIDATION FAILED: missing $file"; exit 1; }
done
grep -q "trust posture must be evidence-backed" "$DF35_DIR/DF35_PARTNER_TRUST_POSTURE_MODEL.md"
grep -q "publication prohibited" "$DF35_DIR/DF35_CERTIFICATION_READINESS_POLICY.md"
grep -q "every blocked output must still produce evidence" "$DF35_DIR/DF35_TRUST_CERTIFICATION_EVIDENCE_MODEL.md"
echo "DF35 VALIDATION PASSED"
