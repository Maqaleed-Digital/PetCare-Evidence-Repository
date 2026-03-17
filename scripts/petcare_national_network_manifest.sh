#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-NATIONAL-SERVICE-NETWORK-AND-REGIONAL-OPERATING-GOVERNANCE"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "NATIONAL_SERVICE_NETWORK_GOVERNANCE_MODEL.md" -o \
       -name "REGIONAL_OPERATING_UNIT_GOVERNANCE.md" -o \
       -name "CROSS_REGION_SERVICE_CONSISTENCY_CONTROLS.md" -o \
       -name "NATIONAL_PARTNER_NETWORK_GOVERNANCE.md" -o \
       -name "REGIONAL_PERFORMANCE_REVIEW_PACK.md" -o \
       -name "INTER_CLINIC_ESCALATION_AND_REFERRAL_GOVERNANCE.md" -o \
       -name "NATIONAL_CAPACITY_BALANCING_MODEL.md" -o \
       -name "REGIONAL_RISK_AND_RESILIENCE_GOVERNANCE.md" -o \
       -name "SCALE_TO_NETWORK_TRANSITION_CLOSEOUT.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_national_network_validate.sh" -o \
       -name "petcare_national_network_manifest.sh" \)
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
  echo '{"event":"national_network_pack_generated","pack_id":"PETCARE-NATIONAL-SERVICE-NETWORK-AND-REGIONAL-OPERATING-GOVERNANCE","state":"petcare_multi_clinic_scale_execution_governed","target_state":"petcare_national_service_network_governed","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_SERVICE_NETWORK_GOVERNANCE_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/REGIONAL_OPERATING_UNIT_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/CROSS_REGION_SERVICE_CONSISTENCY_CONTROLS.md"),
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_PARTNER_NETWORK_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/REGIONAL_PERFORMANCE_REVIEW_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/INTER_CLINIC_ESCALATION_AND_REFERRAL_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_CAPACITY_BALANCING_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/REGIONAL_RISK_AND_RESILIENCE_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/SCALE_TO_NETWORK_TRANSITION_CLOSEOUT.md"),
    Path("scripts/petcare_national_network_validate.sh"),
    Path("scripts/petcare_national_network_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-NATIONAL-SERVICE-NETWORK-AND-REGIONAL-OPERATING-GOVERNANCE",
    "state": "petcare_multi_clinic_scale_execution_governed",
    "target_state": "petcare_national_service_network_governed",
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
