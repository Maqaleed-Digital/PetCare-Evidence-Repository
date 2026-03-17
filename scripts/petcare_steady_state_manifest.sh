#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-STEADY-STATE-OPERATIONS-AND-CONTINUOUS-IMPROVEMENT-GOVERNANCE"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "STEADY_STATE_OPERATING_MODEL.md" -o \
       -name "WEEKLY_SERVICE_REVIEW_GOVERNANCE.md" -o \
       -name "MONTHLY_KPI_SLO_BOARD_PACK.md" -o \
       -name "PROBLEM_MANAGEMENT_AND_RCA_GOVERNANCE.md" -o \
       -name "CAPACITY_AND_AVAILABILITY_PLANNING.md" -o \
       -name "RELEASE_CALENDAR_GOVERNANCE.md" -o \
       -name "VENDOR_AND_PARTNER_OPERATIONS_REVIEW.md" -o \
       -name "CONTINUOUS_IMPROVEMENT_BACKLOG_GOVERNANCE.md" -o \
       -name "HYPERCARE_TO_BAU_TRANSITION_CLOSEOUT.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_steady_state_validate.sh" -o \
       -name "petcare_steady_state_manifest.sh" \)
} | LC_ALL=C sort > "${RUN_DIR}/file_listing.txt"

{
  echo "PACK_ID=${PACK_ID}"
  echo "TIMESTAMP=${STAMP}"
  echo "SOURCE_OF_TRUTH_BEFORE=$(git rev-parse HEAD)"
  echo "WORKTREE_STATUS_START"
  git status --short
  echo "WORKTREE_STATUS_END"
} > "${RUN_DIR}/test_log_sample.txt"

{
  echo '{"event":"steady_state_operations_pack_generated","pack_id":"PETCARE-STEADY-STATE-OPERATIONS-AND-CONTINUOUS-IMPROVEMENT-GOVERNANCE","state":"petcare_hypercare_governed_operations_active","target_state":"petcare_steady_state_governed_operations_active","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/STEADY_STATE_OPERATING_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/WEEKLY_SERVICE_REVIEW_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/MONTHLY_KPI_SLO_BOARD_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/PROBLEM_MANAGEMENT_AND_RCA_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/CAPACITY_AND_AVAILABILITY_PLANNING.md"),
    Path("petcare_execution/INFRASTRUCTURE/RELEASE_CALENDAR_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/VENDOR_AND_PARTNER_OPERATIONS_REVIEW.md"),
    Path("petcare_execution/INFRASTRUCTURE/CONTINUOUS_IMPROVEMENT_BACKLOG_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/HYPERCARE_TO_BAU_TRANSITION_CLOSEOUT.md"),
    Path("scripts/petcare_steady_state_validate.sh"),
    Path("scripts/petcare_steady_state_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-STEADY-STATE-OPERATIONS-AND-CONTINUOUS-IMPROVEMENT-GOVERNANCE",
    "state": "petcare_hypercare_governed_operations_active",
    "target_state": "petcare_steady_state_governed_operations_active",
    "files": [],
}
for path in tracked:
    data = path.read_bytes()
    manifest["files"].append({
        "path": str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
    })
print(json.dumps(manifest, indent=2))
PY

echo "${RUN_DIR}"
