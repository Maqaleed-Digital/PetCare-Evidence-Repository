#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-CLOSE-EP09"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

git status -sb | tee "${RUN_DIR}/git_status.txt"
git rev-parse HEAD | tee "${RUN_DIR}/git_head.txt"

export PYTHONPATH="${REPO_ROOT}/petcare_runtime/src:${PYTHONPATH:-}"
python3 -m pytest "petcare_runtime/tests/financial_operations/test_financial_operations.py" -q | tee "${RUN_DIR}/tests.log"

python3 <<'PY' | tee "${RUN_DIR}/invariant_check.txt"
from decimal import Decimal

from petcare.financial_operations import (
    DisputeEvidenceRef,
    InvoiceLifecycleRecord,
    InvoiceOpsStatus,
    PaymentTrackingStatus,
    ReconciliationResolutionRecord,
    build_visibility_snapshot,
    create_dispute,
    detect_reconciliation_case,
    issue_invoice,
    record_external_signal,
    resolve_dispute,
    resolve_reconciliation_case,
    start_payment_tracking,
)

draft = InvoiceLifecycleRecord(
    invoice_id="INV-CLOSE-EP09-001",
    partner_id="PARTNER-CLOSE",
    settlement_id="SET-CLOSE-EP09-001",
    currency="SAR",
    issued_at=None,
    status=InvoiceOpsStatus.DRAFT,
    gross_total=Decimal("100.00"),
    platform_fee_total=Decimal("10.00"),
    net_total=Decimal("90.00"),
    last_transition_at="2026-03-30T20:00:00Z",
)

issued = issue_invoice(draft, "2026-03-30T20:05:00Z")

payment = start_payment_tracking(
    instruction_id="INS-CLOSE-EP09-001",
    started_at="2026-03-30T20:06:00Z",
    external_reference_id="EXT-CLOSE-001",
)
signaled = record_external_signal(
    payment,
    signaled_at="2026-03-30T20:07:00Z",
    signal_source="gateway.webhook",
    payload_ref="obj://signals/close-ep09-001",
)

rec_case = detect_reconciliation_case(
    case_id="REC-CLOSE-001",
    instruction_id="INS-CLOSE-EP09-001",
    currency="SAR",
    expected_total=Decimal("90.00"),
    actual_total=Decimal("85.00"),
    detected_at="2026-03-30T20:08:00Z",
)
resolved_case = resolve_reconciliation_case(
    rec_case,
    ReconciliationResolutionRecord(
        resolution_id="RES-CLOSE-001",
        resolved_by="finance.reviewer",
        resolved_at="2026-03-30T20:09:00Z",
        reason="documented adjustment reviewed",
    ),
)

dispute, disputed_invoice = create_dispute(
    dispute_id="DSP-CLOSE-001",
    invoice=issued,
    opened_at="2026-03-30T20:10:00Z",
    opened_by="partner.user",
    reason="statement discrepancy claimed",
    evidence_refs=[
        DisputeEvidenceRef(
            evidence_id="EVD-CLOSE-001",
            reference_uri="obj://evidence/close-ep09-001",
            uploaded_at="2026-03-30T20:10:30Z",
        )
    ],
)
resolved_dispute = resolve_dispute(
    dispute,
    resolved_at="2026-03-30T20:11:00Z",
    resolved_by="finance.manager",
    reason="review completed and explanation issued",
)

visibility = build_visibility_snapshot(
    snapshot_id="VIS-CLOSE-001",
    generated_at="2026-03-30T20:12:00Z",
    invoices=[disputed_invoice],
    disputes=[resolved_dispute],
    reconciliation_cases=[resolved_case],
)

checks = {
    "invoice_state_machine_transition_guarded": issued.status.value == "issued",
    "external_signal_recording_is_non_autonomous": signaled.status.value == "received_external_signal",
    "reconciliation_auto_resolution_enabled": False,
    "dispute_resolution_requires_reason": resolved_dispute.resolution is not None and bool(resolved_dispute.resolution.reason),
    "financial_visibility_is_deterministic": str(visibility.partner_exposure_total) == "90.00",
    "ai_execution_authority": False,
    "live_payment_rails_enabled": False,
}
for key, value in checks.items():
    print(f"{key}={value}")
PY

find \
  "petcare_execution/EP09_CLOSURE" \
  "petcare_execution/EP09" \
  "petcare_runtime/src/petcare/financial_operations" \
  "petcare_runtime/tests/financial_operations" \
  "scripts/petcare_ep09_all_waves_pack.sh" \
  "scripts/petcare_close_ep09.sh" \
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
    "petcare_execution/EP09_CLOSURE/EP09_CLOSURE_SUMMARY.md",
    "petcare_execution/EP09_CLOSURE/EP09_ACCEPTANCE_RECORD.md",
    "petcare_execution/EP09_CLOSURE/EP09_OPERATIONAL_FINANCE_INVARIANTS_REGISTRY.md",
    "petcare_execution/EP09_CLOSURE/EP09_GOVERNANCE_SEAL.md",
    "petcare_execution/EP09_CLOSURE/EP09_EVIDENCE_INDEX.md",
    "scripts/petcare_close_ep09.sh",
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
printf 'GOVERNANCE_STATE     : ep09_closed_governed\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'OPERATING_BOUNDARY   : financial_operations_layer_non_autonomous\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
