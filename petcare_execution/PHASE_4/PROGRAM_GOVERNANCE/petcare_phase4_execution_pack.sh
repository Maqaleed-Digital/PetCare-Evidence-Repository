#!/usr/bin/env bash
set -euo pipefail

PROGRAM_DIR="petcare_execution/PHASE_4/PROGRAM_GOVERNANCE"

REQUIRED_FILES=(
  "PHASE_4_PROGRAM_MODEL.md"
  "PHASE_4_EXECUTION_SEQUENCE_PLAN.md"
  "PHASE_4_CONTROL_TOWER_MAP.md"
  "PHASE_4_EVIDENCE_CONTRACT.md"
  "PHASE_4_SCOPE_AND_CONSTRAINT_MAP.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$PROGRAM_DIR/$file" ]; then
    echo "PHASE 4 PACK VALIDATION FAILED: missing $file"
    exit 1
  fi
done

grep -q "no autonomous execution" "$PROGRAM_DIR/PHASE_4_PROGRAM_MODEL.md"
grep -q "DF42" "$PROGRAM_DIR/PHASE_4_EXECUTION_SEQUENCE_PLAN.md"
grep -q "dominance_sustainability_state" "$PROGRAM_DIR/PHASE_4_CONTROL_TOWER_MAP.md"
grep -q "MANIFEST.json" "$PROGRAM_DIR/PHASE_4_EVIDENCE_CONTRACT.md"
grep -q "reputation must never be uncited" "$PROGRAM_DIR/PHASE_4_SCOPE_AND_CONSTRAINT_MAP.md"

echo "PHASE 4 EXECUTION PACK VALIDATION PASSED"
