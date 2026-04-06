#!/bin/bash
set -euo pipefail

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
ROOT_DIR="/Users/waheebmahmoud/dev/petcare-evidence-repository"
RUN_DIR="$ROOT_DIR/petcare_execution/EVIDENCE/PETCARE-PH6-3-CLOSURE-AND-NEXT-PHASE-HANDOFF/$TIMESTAMP"

mkdir -p "$RUN_DIR"

echo "PETCARE PH6.3 CLOSURE AND NEXT-PHASE HANDOFF" > "$RUN_DIR/summary.txt"
echo "TIMESTAMP=$TIMESTAMP" >> "$RUN_DIR/summary.txt"
echo "SOURCE_OF_TRUTH_COMMIT=$(git -C "$ROOT_DIR" rev-parse --short HEAD)" >> "$RUN_DIR/summary.txt"
echo "PH6_3_STATUS=GOVERNED_PACK_COMPLETE_OPERATIONAL_VALIDATION_PENDING" >> "$RUN_DIR/summary.txt"
echo "" >> "$RUN_DIR/summary.txt"

cat > "$RUN_DIR/closure_status.txt" <<'EOT'
COMPLETE
- governed PH6.3 pack exists
- issuance register template exists
- authenticated validation checklist exists
- evidence runner exists
- public live probes passed

PENDING_HUMAN_ACTION
- issue owner credential
- issue vet credential
- issue admin credential
- complete A-01
- complete A-02
- complete A-03
EOT

cat > "$RUN_DIR/next_phase.txt" <<'EOT'
NEXT_PHASE=PETCARE-PHASE-6.4-FIRST-CONTROLLED-PILOT-WORKFLOW-EXECUTION

ENTRY_CONDITION
- owner authenticated validation complete
- vet authenticated validation complete
- admin authenticated validation complete
- controlled pilot credentials issued and recorded
EOT

find "$RUN_DIR" -type f -exec shasum -a 256 {} \; | sort > "$RUN_DIR/MANIFEST.sha256"

echo "RUN COMPLETE" >> "$RUN_DIR/summary.txt"
echo "EVIDENCE_RUN_DIR=$RUN_DIR" >> "$RUN_DIR/summary.txt"

printf '%s\n' "$RUN_DIR"
