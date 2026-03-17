#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-SCALE-EXPANSION-READINESS-AND-MULTI-CLINIC-EXECUTION-GOVERNANCE"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "MULTI_CLINIC_SCALE_GOVERNANCE_MODEL.md" -o \
       -name "EXPANSION_WAVE_PLANNING_PACK.md" -o \
       -name "CLINIC_LAUNCH_READINESS_CHECKLIST.md" -o \
       -name "SCALED_SERVICE_CAPACITY_MODEL.md" -o \
       -name "REGIONAL_PARTNER_ONBOARDING_GOVERNANCE.md" -o \
       -name "EXPANSION_RISK_REGISTER.md" -o \
       -name "ROLLOUT_SEQUENCING_AND_DEPENDENCY_CONTROL.md" -o \
       -name "POST_EXPANSION_STABILIZATION_GOVERNANCE.md" -o \
       -name "EXECUTIVE_SCALE_REVIEW_PACK.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_scale_execution_validate.sh" -o \
       -name "petcare_scale_execution_manifest.sh" \)
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
  echo '{"event":"scale_execution_pack_generated","pack_id":"PETCARE-SCALE-EXPANSION-READINESS-AND-MULTI-CLINIC-EXECUTION-GOVERNANCE","state":"petcare_executive_service_governance_active","target_state":"petcare_multi_clinic_scale_execution_governed","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/MULTI_CLINIC_SCALE_GOVERNANCE_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/EXPANSION_WAVE_PLANNING_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/CLINIC_LAUNCH_READINESS_CHECKLIST.md"),
    Path("petcare_execution/INFRASTRUCTURE/SCALED_SERVICE_CAPACITY_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/REGIONAL_PARTNER_ONBOARDING_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/EXPANSION_RISK_REGISTER.md"),
    Path("petcare_execution/INFRASTRUCTURE/ROLLOUT_SEQUENCING_AND_DEPENDENCY_CONTROL.md"),
    Path("petcare_execution/INFRASTRUCTURE/POST_EXPANSION_STABILIZATION_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/EXECUTIVE_SCALE_REVIEW_PACK.md"),
    Path("scripts/petcare_scale_execution_validate.sh"),
    Path("scripts/petcare_scale_execution_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-SCALE-EXPANSION-READINESS-AND-MULTI-CLINIC-EXECUTION-GOVERNANCE",
    "state": "petcare_executive_service_governance_active",
    "target_state": "petcare_multi_clinic_scale_execution_governed",
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
