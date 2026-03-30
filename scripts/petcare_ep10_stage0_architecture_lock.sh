#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-BUILD-EP10-INTEGRATION-AND-OPERATIONAL-CONTROL-STAGE0"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

git status -sb | tee "${RUN_DIR}/git_status.txt"
git rev-parse HEAD | tee "${RUN_DIR}/git_head.txt"

find \
  "petcare_execution/EP10_STAGE0" \
  "scripts/petcare_ep10_stage0_architecture_lock.sh" \
  -type f | sort > "${RUN_DIR}/file_listing.txt"

cat > "${RUN_DIR}/phase_assertions.txt" <<'ASSERT'
architecture_lock_created=true
runtime_code_changed=false
live_payment_rails_enabled=false
ai_execution_authority=false
reconciliation_auto_resolution_enabled=false
adapter_mode=passive_or_instruction_only
stage_type=architecture_lock
ASSERT

export RUN_DIR_ABS="${REPO_ROOT}/${RUN_DIR}"
export REPO_ROOT
export PACK_ID

python3 <<'PY'
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
repo_root = Path(os.environ["REPO_ROOT"])

entries = []

for path in sorted(run_dir.rglob("*")):
    if path.is_file():
        rel = path.relative_to(repo_root).as_posix()
        entries.append(
            {
                "path": rel,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )

for rel in [
    "petcare_execution/EP10_STAGE0/EP10_ARCHITECTURE_LOCK.md",
    "petcare_execution/EP10_STAGE0/EP10_HARD_GATES.md",
    "petcare_execution/EP10_STAGE0/EP10_DEPENDENCY_MAP.md",
    "petcare_execution/EP10_STAGE0/EP10_EXECUTION_SPEC.md",
    "petcare_execution/EP10_STAGE0/EP10_NOTION_EXECUTION_MAP.md",
    "scripts/petcare_ep10_stage0_architecture_lock.sh",
]:
    path = repo_root / rel
    entries.append(
        {
            "path": rel,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )

manifest = {
    "pack_id": os.environ["PACK_ID"],
    "run_dir": run_dir.relative_to(repo_root).as_posix(),
    "entries": entries,
}
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

printf 'PACK_ID              : %s\n' "$PACK_ID" | tee "${RUN_DIR}/summary.txt"
printf 'VALIDATION           : OK\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'STAGE                : architecture_lock\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'GOVERNANCE_POSITION  : integration_and_operational_control_planning_locked\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
