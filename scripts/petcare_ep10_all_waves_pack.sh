#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-BUILD-EP10-INTEGRATION-AND-OPERATIONAL-CONTROL"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

export PYTHONPATH="${REPO_ROOT}/petcare_runtime/src:${PYTHONPATH:-}"

python3 -m pytest "petcare_runtime/tests/integration_control/test_integration_control.py" -q | tee "${RUN_DIR}/pytest.log"

cat > "${RUN_DIR}/phase_assertions.txt" <<'ASSERT'
live_payment_rails_enabled=false
ai_execution_authority=false
reconciliation_auto_resolution_enabled=false
adapter_mode=passive_or_instruction_only
ep10_real_world_operability_layer=true
ASSERT

find \
  "petcare_execution/EP10" \
  "petcare_runtime/src/petcare/integration_control" \
  "petcare_runtime/tests/integration_control" \
  "petcare_runtime/migrations/0010_ep10_integration_operational_control_checkpoint.sql" \
  "scripts/petcare_ep10_all_waves_pack.sh" \
  -type f | sort > "${RUN_DIR}/file_listing.txt"

export RUN_DIR_ABS="${REPO_ROOT}/${RUN_DIR}"
export PACK_ID

python3 <<'PY'
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
repo_root = run_dir.parents[3]
manifest_entries = []

for path in sorted(run_dir.rglob("*")):
    if path.is_file():
        rel = path.relative_to(repo_root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_entries.append({"path": rel, "sha256": digest})

for rel in [
    "petcare_execution/EP10/EP10_EXECUTION_MASTER_SPEC.md",
    "petcare_execution/EP10/EP10_HARD_GATES.md",
    "petcare_execution/EP10/EP10_NOTION_EXECUTION_MAP.md",
    "petcare_runtime/src/petcare/integration_control/__init__.py",
    "petcare_runtime/src/petcare/integration_control/adapters.py",
    "petcare_runtime/src/petcare/integration_control/signals.py",
    "petcare_runtime/src/petcare/integration_control/queues.py",
    "petcare_runtime/src/petcare/integration_control/tasks.py",
    "petcare_runtime/src/petcare/integration_control/actions.py",
    "petcare_runtime/src/petcare/integration_control/exceptions.py",
    "petcare_runtime/src/petcare/integration_control/visibility.py",
    "petcare_runtime/src/petcare/integration_control/audit.py",
    "petcare_runtime/tests/integration_control/test_integration_control.py",
    "petcare_runtime/migrations/0010_ep10_integration_operational_control_checkpoint.sql",
    "scripts/petcare_ep10_all_waves_pack.sh",
]:
    path = repo_root / rel
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_entries.append({"path": rel, "sha256": digest})

manifest = {
    "pack_id": os.environ["PACK_ID"],
    "run_dir": run_dir.relative_to(repo_root).as_posix(),
    "entries": manifest_entries,
}
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

printf '\nPACK_ID              : %s\n' "$PACK_ID" | tee "${RUN_DIR}/summary.txt"
printf 'VALIDATION           : OK\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'GOVERNANCE_POSITION  : integration_and_operational_control_non_autonomous\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
