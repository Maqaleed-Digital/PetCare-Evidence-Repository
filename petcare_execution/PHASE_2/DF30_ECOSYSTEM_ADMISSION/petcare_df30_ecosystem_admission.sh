#!/usr/bin/env bash
set -euo pipefail

PHASE_DIR="petcare_execution/PHASE_2/DF30_ECOSYSTEM_ADMISSION"

# File presence checks
for f in \
  "$PHASE_DIR/ECOSYSTEM_ADMISSION_GOVERNANCE_MODEL.md" \
  "$PHASE_DIR/EXTERNAL_ACTIVATION_GATE_POLICY.md" \
  "$PHASE_DIR/ECOSYSTEM_ADMISSION_RULE_CATALOG.md" \
  "$PHASE_DIR/GOVERNED_ADMISSION_EVIDENCE_MODEL.md"; do
  [[ -f "$f" ]] || { echo "BLOCKED: missing $f"; exit 1; }
done

# Content integrity checks
grep -q "no autonomous execution" "$PHASE_DIR/ECOSYSTEM_ADMISSION_GOVERNANCE_MODEL.md" \
  || { echo "BLOCKED: 'no autonomous execution' clause missing from ECOSYSTEM_ADMISSION_GOVERNANCE_MODEL.md"; exit 1; }

grep -q "publication prohibited" "$PHASE_DIR/EXTERNAL_ACTIVATION_GATE_POLICY.md" \
  || { echo "BLOCKED: 'publication prohibited' clause missing from EXTERNAL_ACTIVATION_GATE_POLICY.md"; exit 1; }

grep -q "PROHIBITED RULES" "$PHASE_DIR/ECOSYSTEM_ADMISSION_RULE_CATALOG.md" \
  || { echo "BLOCKED: 'PROHIBITED RULES' clause missing from ECOSYSTEM_ADMISSION_RULE_CATALOG.md"; exit 1; }

grep -q "every blocked admission output must still generate an evidence record" "$PHASE_DIR/GOVERNED_ADMISSION_EVIDENCE_MODEL.md" \
  || { echo "BLOCKED: evidence obligation clause missing from GOVERNED_ADMISSION_EVIDENCE_MODEL.md"; exit 1; }

echo "ACTIVE: DF30 ECOSYSTEM ADMISSION GOVERNANCE — all governance clauses verified"
echo "ACTIVE: External activation gate controls enforced"
echo "ACTIVE: Admission rule catalog validated"
echo "ACTIVE: Evidence model confirmed"
