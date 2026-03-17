#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-ENTERPRISE-NETWORK-OPTIMIZATION-AND-NATIONAL-ORCHESTRATION-GOVERNANCE"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "ENTERPRISE_NETWORK_ORCHESTRATION_MODEL.md" -o \
       -name "NATIONAL_COMMAND_CADENCE.md" -o \
       -name "CROSS_REGION_OPTIMIZATION_GOVERNANCE.md" -o \
       -name "NATIONAL_REFERRAL_LOAD_BALANCING_GOVERNANCE.md" -o \
       -name "NETWORK_WIDE_SERVICE_QUALITY_SCORECARD.md" -o \
       -name "ENTERPRISE_DEPENDENCY_AND_RESILIENCE_CONTROL.md" -o \
       -name "EXPANSION_OPTIMIZATION_BACKLOG_GOVERNANCE.md" -o \
       -name "NATIONAL_OPERATING_REVIEW_PACK.md" -o \
       -name "NETWORK_MATURITY_TRANSITION_CLOSEOUT.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_enterprise_network_validate.sh" -o \
       -name "petcare_enterprise_network_manifest.sh" \)
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
  echo '{"event":"enterprise_network_pack_generated","pack_id":"PETCARE-ENTERPRISE-NETWORK-OPTIMIZATION-AND-NATIONAL-ORCHESTRATION-GOVERNANCE","state":"petcare_national_service_network_governed","target_state":"petcare_enterprise_network_orchestration_governed","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/ENTERPRISE_NETWORK_ORCHESTRATION_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_COMMAND_CADENCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/CROSS_REGION_OPTIMIZATION_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_REFERRAL_LOAD_BALANCING_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/NETWORK_WIDE_SERVICE_QUALITY_SCORECARD.md"),
    Path("petcare_execution/INFRASTRUCTURE/ENTERPRISE_DEPENDENCY_AND_RESILIENCE_CONTROL.md"),
    Path("petcare_execution/INFRASTRUCTURE/EXPANSION_OPTIMIZATION_BACKLOG_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_OPERATING_REVIEW_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/NETWORK_MATURITY_TRANSITION_CLOSEOUT.md"),
    Path("scripts/petcare_enterprise_network_validate.sh"),
    Path("scripts/petcare_enterprise_network_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-ENTERPRISE-NETWORK-OPTIMIZATION-AND-NATIONAL-ORCHESTRATION-GOVERNANCE",
    "state": "petcare_national_service_network_governed",
    "target_state": "petcare_enterprise_network_orchestration_governed",
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
