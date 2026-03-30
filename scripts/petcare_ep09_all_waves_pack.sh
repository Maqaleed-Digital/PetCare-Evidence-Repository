#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-BUILD-EP09-FINANCIAL-OPERATIONS-AND-RECONCILIATION"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

export PYTHONPATH="${REPO_ROOT}/petcare_runtime/src:${PYTHONPATH:-}"

python3 -m pytest "petcare_runtime/tests/financial_operations/test_financial_operations.py" -q | tee "${RUN_DIR}/pytest.log"

cat > "${RUN_DIR}/phase_assertions.txt" <<'ASSERT'
live_payment_rails_enabled=false
ai_execution_authority=false
reconciliation_auto_resolution_enabled=false
export_mode=non_autonomous_export_only
ep09_operational_finance_layer=true
ASSERT

find \
  "petcare_execution/EP09" \
  "petcare_runtime/src/petcare/financial_operations" \
  "petcare_runtime/tests/financial_operations" \
  "petcare_runtime/migrations/0009_ep09_financial_operations_checkpoint.sql" \
  "scripts/petcare_ep09_all_waves_pack.sh" \
  -type f | sort > "${RUN_DIR}/file_listing.txt"

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
    "petcare_execution/EP09/EP09_EXECUTION_MASTER_SPEC.md",
    "petcare_execution/EP09/EP09_HARD_GATES.md",
    "petcare_execution/EP09/EP09_NOTION_EXECUTION_MAP.md",
    "petcare_runtime/src/petcare/financial_operations/__init__.py",
    "petcare_runtime/src/petcare/financial_operations/models.py",
    "petcare_runtime/src/petcare/financial_operations/invoices.py",
    "petcare_runtime/src/petcare/financial_operations/payment_tracking.py",
    "petcare_runtime/src/petcare/financial_operations/reconciliation_ops.py",
    "petcare_runtime/src/petcare/financial_operations/disputes.py",
    "petcare_runtime/src/petcare/financial_operations/statements.py",
    "petcare_runtime/src/petcare/financial_operations/visibility.py",
    "petcare_runtime/src/petcare/financial_operations/audit.py",
    "petcare_runtime/tests/financial_operations/test_financial_operations.py",
    "petcare_runtime/migrations/0009_ep09_financial_operations_checkpoint.sql",
    "scripts/petcare_ep09_all_waves_pack.sh",
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
printf 'GOVERNANCE_POSITION  : financial_operations_layer_non_autonomous\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
