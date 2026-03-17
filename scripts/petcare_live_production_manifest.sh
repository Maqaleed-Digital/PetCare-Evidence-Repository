#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "LIVE_PRODUCTION_DEPLOYMENT_EXECUTION_RECORD.md" -o \
       -name "LIVE_RELEASE_REGISTRATION.md" -o \
       -name "LIVE_HEALTH_VERIFICATION.md" -o \
       -name "LIVE_AUDIT_PATH_VERIFICATION.md" -o \
       -name "LIVE_AI_GOVERNANCE_PATH_VERIFICATION.md" -o \
       -name "LIVE_OBSERVABILITY_VERIFICATION.md" -o \
       -name "ROLLBACK_DRILL_CONFIRMATION.md" -o \
       -name "GO_LIVE_CLOSEOUT_EVIDENCE.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_live_production_validate.sh" -o \
       -name "petcare_live_production_manifest.sh" \)
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
  echo '{"event":"live_production_pack_generated","pack_id":"PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION","state":"petcare_production_environment_ready","target_state":"petcare_live_production_verified","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/LIVE_PRODUCTION_DEPLOYMENT_EXECUTION_RECORD.md"),
    Path("petcare_execution/INFRASTRUCTURE/LIVE_RELEASE_REGISTRATION.md"),
    Path("petcare_execution/INFRASTRUCTURE/LIVE_HEALTH_VERIFICATION.md"),
    Path("petcare_execution/INFRASTRUCTURE/LIVE_AUDIT_PATH_VERIFICATION.md"),
    Path("petcare_execution/INFRASTRUCTURE/LIVE_AI_GOVERNANCE_PATH_VERIFICATION.md"),
    Path("petcare_execution/INFRASTRUCTURE/LIVE_OBSERVABILITY_VERIFICATION.md"),
    Path("petcare_execution/INFRASTRUCTURE/ROLLBACK_DRILL_CONFIRMATION.md"),
    Path("petcare_execution/INFRASTRUCTURE/GO_LIVE_CLOSEOUT_EVIDENCE.md"),
    Path("scripts/petcare_live_production_validate.sh"),
    Path("scripts/petcare_live_production_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION",
    "state": "petcare_production_environment_ready",
    "target_state": "petcare_live_production_verified",
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
