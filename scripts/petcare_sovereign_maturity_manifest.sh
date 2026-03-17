#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-SOVEREIGN-PLATFORM-MATURITY-AND-BOARD-LEVEL-NATIONAL-CONTROL-GOVERNANCE"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "SOVEREIGN_NATIONAL_CONTROL_MODEL.md" -o \
       -name "BOARD_LEVEL_NATIONAL_SERVICE_OVERSIGHT_PACK.md" -o \
       -name "ENTERPRISE_GOVERNANCE_MATURITY_SCORECARD.md" -o \
       -name "NATIONAL_RESILIENCE_AND_CONTINUITY_GOVERNANCE.md" -o \
       -name "REGULATOR_AND_COMPLIANCE_OVERSIGHT_PACK.md" -o \
       -name "NATIONAL_AI_AND_AUDIT_ASSURANCE_REVIEW.md" -o \
       -name "STRATEGIC_CAPITAL_AND_SCALE_INVESTMENT_GOVERNANCE.md" -o \
       -name "PLATFORM_MATURITY_TRANSITION_CLOSEOUT.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_sovereign_maturity_validate.sh" -o \
       -name "petcare_sovereign_maturity_manifest.sh" \)
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
  echo '{"event":"sovereign_maturity_pack_generated","pack_id":"PETCARE-SOVEREIGN-PLATFORM-MATURITY-AND-BOARD-LEVEL-NATIONAL-CONTROL-GOVERNANCE","state":"petcare_enterprise_network_orchestration_governed","target_state":"petcare_sovereign_platform_maturity_governed","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/SOVEREIGN_NATIONAL_CONTROL_MODEL.md"),
    Path("petcare_execution/INFRASTRUCTURE/BOARD_LEVEL_NATIONAL_SERVICE_OVERSIGHT_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/ENTERPRISE_GOVERNANCE_MATURITY_SCORECARD.md"),
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_RESILIENCE_AND_CONTINUITY_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/REGULATOR_AND_COMPLIANCE_OVERSIGHT_PACK.md"),
    Path("petcare_execution/INFRASTRUCTURE/NATIONAL_AI_AND_AUDIT_ASSURANCE_REVIEW.md"),
    Path("petcare_execution/INFRASTRUCTURE/STRATEGIC_CAPITAL_AND_SCALE_INVESTMENT_GOVERNANCE.md"),
    Path("petcare_execution/INFRASTRUCTURE/PLATFORM_MATURITY_TRANSITION_CLOSEOUT.md"),
    Path("scripts/petcare_sovereign_maturity_validate.sh"),
    Path("scripts/petcare_sovereign_maturity_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-SOVEREIGN-PLATFORM-MATURITY-AND-BOARD-LEVEL-NATIONAL-CONTROL-GOVERNANCE",
    "state": "petcare_enterprise_network_orchestration_governed",
    "target_state": "petcare_sovereign_platform_maturity_governed",
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
