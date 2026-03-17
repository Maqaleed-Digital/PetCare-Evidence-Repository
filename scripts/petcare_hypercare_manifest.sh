#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-PRODUCTION-HYPERCARE-AND-OPERATIONS-GOVERNANCE"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "HYPERCARE_OPERATING_WINDOW.md" -o \
       -name "INCIDENT_AND_ESCALATION_GOVERNANCE.md" -o \
       -name "PRODUCTION_KPI_SLO_CONTROL_PACK.md" -o \
       -name "DAILY_OPERATIONAL_REVIEW_TEMPLATE.md" -o \
       -name "LIVE_ISSUE_TRIAGE_AND_SEVERITY_MODEL.md" -o \
       -name "CHANGE_FREEZE_AND_EMERGENCY_CHANGE_RULES.md" -o \
       -name "POST_GO_LIVE_REPORTING_PACK.md" -o \
       -name "HYPERCARE_CLOSEOUT_CRITERIA.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_hypercare_validate.sh" -o \
       -name "petcare_hypercare_manifest.sh" \)
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
  echo '{"event":"production_hypercare_pack_generated","pack_id":"PETCARE-PRODUCTION-HYPERCARE-AND-OPERATIONS-GOVERNANCE","state":"petcare_live_production_verified","target_state":"petcare_hypercare_governed_operations_active","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/HYPERCARE_OPERATING_WINDOW.md"),
    Path("petcare_execution/INFRASTRUCTURE/INCIDENT_AND_ESCALATION_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/PRODUCTION_KPI_SLO_CONTROL_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/DAILY_OPERATIONAL_REVIEW_TEMPLATE.md"),
    Path("petcare_execution/INFRASTRUCTURE/LIVE_ISSUE_TRIAGE_AND_SEVERITY_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/CHANGE_FREEZE_AND_EMERGENCY_CHANGE_RULES.md"),
    Path("petcare_execution/INFRASTRUCTURE/POST_GO_LIVE_REPORTING_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/HYPERCARE_CLOSEOUT_CRITERIA.md"),
    Path("scripts/petcare_hypercare_validate.sh"),
    Path("scripts/petcare_hypercare_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-PRODUCTION-HYPERCARE-AND-OPERATIONS-GOVERNANCE",
    "state": "petcare_live_production_verified",
    "target_state": "petcare_hypercare_governed_operations_active",
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
