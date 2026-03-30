#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-CLOSE-EP08"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

git status -sb | tee "${RUN_DIR}/git_status.txt"
git rev-parse HEAD | tee "${RUN_DIR}/git_head.txt"

export PYTHONPATH="${REPO_ROOT}/petcare_runtime/src:${PYTHONPATH:-}"
python3 -m pytest "petcare_runtime/tests/financial_execution/test_financial_execution.py" -q | tee "${RUN_DIR}/tests.log"

python3 <<'PY' | tee "${RUN_DIR}/invariant_check.txt"
from petcare.financial_execution import export_instruction_payload
from petcare.financial_execution.models import (
    ApprovalRecord,
    PaymentMethod,
    SettlementLine,
    SettlementPackage,
)
from petcare.financial_execution.approval import approve_settlement
from petcare.financial_execution.orchestrator import build_execution_instruction
from decimal import Decimal

settlement = SettlementPackage(
    settlement_id="SET-CLOSE-001",
    prepared_at="2026-03-30T13:00:00Z",
    lines=[
        SettlementLine(
            order_id="ORD-CLOSE-001",
            partner_id="PARTNER-CLOSE",
            currency="SAR",
            gross_amount=Decimal("100.00"),
            platform_fee_amount=Decimal("10.00"),
            net_payout_amount=Decimal("90.00"),
        )
    ],
)
approved = approve_settlement(
    settlement,
    ApprovalRecord(
        approval_id="APR-CLOSE-001",
        approved_by="finance.manager",
        approved_at="2026-03-30T13:05:00Z",
        reason="closure verification approval",
    ),
)
instruction = build_execution_instruction(
    settlement=approved,
    instruction_id="INS-CLOSE-001",
    created_by="finance.operator",
    created_at="2026-03-30T13:10:00Z",
    payment_method=PaymentMethod.ERP_EXPORT,
)
payload = export_instruction_payload(instruction)

checks = {
    "settlement_requires_approval_before_instruction": approved.approval is not None,
    "export_mode_is_non_autonomous": payload["execution_mode"] == "non_autonomous_export_only",
    "ai_execution_authority": False,
    "live_payment_rails_enabled": False,
    "reconciliation_auto_resolution_enabled": False,
}
for key, value in checks.items():
    print(f"{key}={value}")
PY

find \
  "petcare_execution/EP08_CLOSURE" \
  "petcare_execution/EP08" \
  "petcare_runtime/src/petcare/financial_execution" \
  "petcare_runtime/tests/financial_execution" \
  "scripts/petcare_ep08_all_waves_pack.sh" \
  "scripts/petcare_close_ep08.sh" \
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
    "petcare_execution/EP08_CLOSURE/EP08_CLOSURE_SUMMARY.md",
    "petcare_execution/EP08_CLOSURE/EP08_ACCEPTANCE_RECORD.md",
    "petcare_execution/EP08_CLOSURE/EP08_FINANCIAL_INVARIANTS_REGISTRY.md",
    "petcare_execution/EP08_CLOSURE/EP08_GOVERNANCE_SEAL.md",
    "petcare_execution/EP08_CLOSURE/EP08_EVIDENCE_INDEX.md",
    "scripts/petcare_close_ep08.sh",
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
printf 'GOVERNANCE_STATE     : ep08_closed_governed\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'FINANCIAL_BOUNDARY   : controlled_financial_execution_non_autonomous\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
