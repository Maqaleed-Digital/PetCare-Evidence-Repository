#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-BUILD-EP08-FINANCIAL-EXECUTION"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

python3 -m pytest "petcare_runtime/tests/financial_execution/test_financial_execution.py" -q | tee "${RUN_DIR}/pytest.log"

find "petcare_execution/EP08" "petcare_runtime/src/petcare/financial_execution" "petcare_runtime/tests/financial_execution" "petcare_runtime/migrations/0008_ep08_financial_execution_checkpoint.sql" "scripts/petcare_ep08_all_waves_pack.sh" -type f | sort > "${RUN_DIR}/file_listing.txt"

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
manifest_entries = []

for path in sorted(run_dir.rglob("*")):
    if path.is_file():
        rel = path.relative_to(repo_root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_entries.append({"path": rel, "sha256": digest})

for rel in [
    "petcare_execution/EP08/EP08_EXECUTION_MASTER_SPEC.md",
    "petcare_execution/EP08/EP08_HARD_GATES.md",
    "petcare_execution/EP08/EP08_NOTION_EXECUTION_MAP.md",
    "petcare_runtime/src/petcare/financial_execution/__init__.py",
    "petcare_runtime/src/petcare/financial_execution/models.py",
    "petcare_runtime/src/petcare/financial_execution/approval.py",
    "petcare_runtime/src/petcare/financial_execution/orchestrator.py",
    "petcare_runtime/src/petcare/financial_execution/payouts.py",
    "petcare_runtime/src/petcare/financial_execution/invoices.py",
    "petcare_runtime/src/petcare/financial_execution/settlement_executor.py",
    "petcare_runtime/src/petcare/financial_execution/reconciliation.py",
    "petcare_runtime/src/petcare/financial_execution/ledger_adapter.py",
    "petcare_runtime/src/petcare/financial_execution/export_adapter.py",
    "petcare_runtime/tests/financial_execution/test_financial_execution.py",
    "petcare_runtime/migrations/0008_ep08_financial_execution_checkpoint.sql",
    "scripts/petcare_ep08_all_waves_pack.sh",
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
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
printf 'GOVERNANCE_POSITION  : controlled_financial_execution_non_autonomous\n' | tee -a "${RUN_DIR}/summary.txt"
