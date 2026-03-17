#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACK_ID="PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT"
STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${STAMP}"

mkdir -p "$RUN_DIR"

find "petcare_execution/INFRASTRUCTURE" "scripts" -type f \
  \( -name "petcare_production_infra_*" -o -path "petcare_execution/INFRASTRUCTURE/*" \) \
  | LC_ALL=C sort > "${RUN_DIR}/file_listing.txt"

{
  echo "PACK_ID=${PACK_ID}"
  echo "TIMESTAMP=${STAMP}"
  echo "SOURCE_OF_TRUTH_BEFORE=$(git rev-parse HEAD)"
  echo "WORKTREE_STATUS_START"
  git status --short
  echo "WORKTREE_STATUS_END"
} > "${RUN_DIR}/test_log_sample.txt"

{
  echo '{"event":"production_infra_pack_generated","pack_id":"PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT","state":"production_infrastructure_activation","result":"ok"}'
  echo '{"event":"hard_gate_reference","gates":["G-S1","G-R1","G-A1","G-O1"],"result":"tracked"}'
} > "${RUN_DIR}/audit_log_sample.txt"

python3 - <<PY > "${RUN_DIR}/MANIFEST.json"
import hashlib
import json
from pathlib import Path

run_dir = Path("${RUN_DIR}")
files = []
for p in sorted(run_dir.parent.parent.parent.joinpath("INFRASTRUCTURE").glob("*")):
    if p.is_file():
        files.append(str(p))
for p in sorted(Path("scripts").glob("petcare_production_infra_*")):
    if p.is_file():
        files.append(str(p))
for extra in [run_dir / "file_listing.txt", run_dir / "test_log_sample.txt", run_dir / "audit_log_sample.txt"]:
    files.append(str(extra))

manifest = {
    "pack_id": "PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT",
    "state": "production_infrastructure_activation",
    "target_state": "petcare_production_environment_ready",
    "files": [],
}
for rel in files:
    path = Path(rel)
    data = path.read_bytes()
    manifest["files"].append({
        "path": rel,
        "sha256": hashlib.sha256(data).hexdigest(),
    })
print(json.dumps(manifest, indent=2))
PY

echo "${RUN_DIR}"
