#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

{
  find "petcare_execution/INFRASTRUCTURE" -maxdepth 1 -type f \
    \( -name "PRODUCTION_ENVIRONMENT_VARIABLE_CONTRACT.md" -o \
       -name "PRODUCTION_DEPLOYMENT_RUNBOOK.md" -o \
       -name "PRODUCTION_ROLLBACK_RUNBOOK.md" -o \
       -name "BREAK_GLASS_ACCESS_PROCEDURE.md" -o \
       -name "RELEASE_APPROVAL_WORKFLOW.md" -o \
       -name "GO_LIVE_VALIDATION_GATE.md" -o \
       -name "POST_DEPLOY_VERIFICATION_PACK.md" \)
  find "scripts" -maxdepth 1 -type f \
    \( -name "petcare_production_readiness_validate.sh" -o \
       -name "petcare_production_readiness_manifest.sh" \)
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
  echo '{"event":"production_environment_readiness_pack_generated","pack_id":"PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS","state":"production_infrastructure_activation","target_state":"petcare_production_environment_ready","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

RUN_DIR_ABS="$RUN_DIR" python3 - <<'PY' > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
tracked = [
    Path("petcare_execution/INFRASTRUCTURE/PRODUCTION_ENVIRONMENT_VARIABLE_CONTRACT.md"),
    Path("petcare_execution/INFRASTRUCTURE/PRODUCTION_DEPLOYMENT_RUNBOOK.md"),
    Path("petcare_execution/INFRASTRUCTURE/PRODUCTION_ROLLBACK_RUNBOOK.md"),
    Path("petcare_execution/INFRASTRUCTURE/BREAK_GLASS_ACCESS_PROCEDURE.md"),
    Path("petcare_execution/INFRASTRUCTURE/RELEASE_APPROVAL_WORKFLOW.md"),
    Path("petcare_execution/INFRASTRUCTURE/GO_LIVE_VALIDATION_GATE.md"),
    Path("petcare_execution/INFRASTRUCTURE/POST_DEPLOY_VERIFICATION_PACK.md"),
    Path("scripts/petcare_production_readiness_validate.sh"),
    Path("scripts/petcare_production_readiness_manifest.sh"),
    run_dir / "file_listing.txt",
    run_dir / "test_log_sample.txt",
    run_dir / "audit_log_sample.txt",
]
manifest = {
    "pack_id": "PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS",
    "state": "production_infrastructure_activation",
    "target_state": "petcare_production_environment_ready",
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
