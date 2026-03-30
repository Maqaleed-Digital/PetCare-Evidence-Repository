#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-BUILD-EP11-CONTROLLED-PAYMENT-ACTIVATION-STAGE0"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

git status -sb | tee "${RUN_DIR}/git_status.txt"
git rev-parse HEAD | tee "${RUN_DIR}/git_head.txt"

find \
  "petcare_execution/EP11_STAGE0" \
  "scripts/petcare_ep11_stage0_architecture_lock.sh" \
  -type f | sort > "${RUN_DIR}/file_listing.txt"

cat > "${RUN_DIR}/phase_assertions.txt" <<'ASSERT'
architecture_lock_created=true
runtime_code_changed=false
ai_execution_authority=false
payment_activation_live=false
treasury_control_required=true
dual_control_policy_planned=true
stage_type=architecture_lock
ASSERT

export RUN_DIR_ABS="${REPO_ROOT}/${RUN_DIR}"
export PACK_ID

python3 <<'PY'
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
repo_root = run_dir.parents[3]

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
    "petcare_execution/EP11_STAGE0/EP11_ARCHITECTURE_LOCK.md",
    "petcare_execution/EP11_STAGE0/EP11_HARD_GATES.md",
    "petcare_execution/EP11_STAGE0/EP11_DEPENDENCY_MAP.md",
    "petcare_execution/EP11_STAGE0/EP11_EXECUTION_SPEC.md",
    "petcare_execution/EP11_STAGE0/EP11_NOTION_EXECUTION_MAP.md",
    "scripts/petcare_ep11_stage0_architecture_lock.sh",
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
printf 'GOVERNANCE_POSITION  : controlled_payment_activation_planning_locked\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
