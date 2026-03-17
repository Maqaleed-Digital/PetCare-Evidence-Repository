#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-EXECUTIVE-OPERATING-SYSTEM-AND-PORTFOLIO-SERVICE-GOVERNANCE"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "EXECUTIVE_SERVICE_GOVERNANCE_MODEL.md" -o \
       -name "QUARTERLY_OPERATING_REVIEW_PACK.md" -o \
       -name "SERVICE_PORTFOLIO_HEALTH_MODEL.md" -o \
       -name "STRATEGIC_RISK_AND_DEPENDENCY_GOVERNANCE.md" -o \
       -name "CLINIC_EXPANSION_READINESS_GOVERNANCE.md" -o \
       -name "PARTNER_PERFORMANCE_GOVERNANCE.md" -o \
       -name "SERVICE_INVESTMENT_PRIORITIZATION_MODEL.md" -o \
       -name "ANNUAL_OPERATING_PLAN_LINKAGE.md" -o \
       -name "BAU_TO_SCALE_TRANSITION_CONTROL.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_executive_governance_validate.sh" -o \
       -name "petcare_executive_governance_manifest.sh" \)
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
  echo '{"event":"executive_service_governance_pack_generated","pack_id":"PETCARE-EXECUTIVE-OPERATING-SYSTEM-AND-PORTFOLIO-SERVICE-GOVERNANCE","state":"petcare_steady_state_governed_operations_active","target_state":"petcare_executive_service_governance_active","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/EXECUTIVE_SERVICE_GOVERNANCE_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/QUARTERLY_OPERATING_REVIEW_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/SERVICE_PORTFOLIO_HEALTH_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/STRATEGIC_RISK_AND_DEPENDENCY_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/CLINIC_EXPANSION_READINESS_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/PARTNER_PERFORMANCE_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/SERVICE_INVESTMENT_PRIORITIZATION_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/ANNUAL_OPERATING_PLAN_LINKAGE.md"),
    Path("petcare_execution/INFRASTRUCTURE/BAU_TO_SCALE_TRANSITION_CONTROL.md"),
    Path("scripts/petcare_executive_governance_validate.sh"),
    Path("scripts/petcare_executive_governance_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-EXECUTIVE-OPERATING-SYSTEM-AND-PORTFOLIO-SERVICE-GOVERNANCE",
    "state": "petcare_steady_state_governed_operations_active",
    "target_state": "petcare_executive_service_governance_active",
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
