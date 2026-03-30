from __future__ import annotations

from decimal import Decimal

import pytest

from petcare.financial_execution import (
    ApprovalRecord,
    LedgerTraceStore,
    PaymentMethod,
    SettlementLine,
    SettlementPackage,
    approve_execution,
    approve_settlement,
    build_execution_instruction,
    build_ledger_entry,
    build_partner_payouts,
    calculate_totals,
    execute_instruction,
    export_instruction_payload,
    generate_partner_invoice,
    reconcile_instruction_against_actuals,
)


def _sample_settlement() -> SettlementPackage:
    lines = [
        SettlementLine(
            order_id="ORD-001",
            partner_id="PARTNER-A",
            currency="SAR",
            gross_amount=Decimal("120.00"),
            platform_fee_amount=Decimal("20.00"),
            net_payout_amount=Decimal("100.00"),
        ),
        SettlementLine(
            order_id="ORD-002",
            partner_id="PARTNER-A",
            currency="SAR",
            gross_amount=Decimal("80.00"),
            platform_fee_amount=Decimal("10.00"),
            net_payout_amount=Decimal("70.00"),
        ),
        SettlementLine(
            order_id="ORD-003",
            partner_id="PARTNER-B",
            currency="SAR",
            gross_amount=Decimal("50.00"),
            platform_fee_amount=Decimal("5.00"),
            net_payout_amount=Decimal("45.00"),
        ),
    ]
    return SettlementPackage(
        settlement_id="SET-001",
        prepared_at="2026-03-30T12:00:00Z",
        lines=lines,
    )


def test_cannot_build_instruction_without_approval() -> None:
    settlement = _sample_settlement()
    with pytest.raises(ValueError):
        build_execution_instruction(
            settlement=settlement,
            instruction_id="INS-001",
            created_by="finance.operator",
            created_at="2026-03-30T12:05:00Z",
        )


def test_instruction_checksum_is_deterministic() -> None:
    settlement = approve_settlement(
        _sample_settlement(),
        ApprovalRecord(
            approval_id="APR-001",
            approved_by="finance.manager",
            approved_at="2026-03-30T12:03:00Z",
            reason="approved for scheduled payout run",
        ),
    )

    first = build_execution_instruction(
        settlement=settlement,
        instruction_id="INS-001",
        created_by="finance.operator",
        created_at="2026-03-30T12:05:00Z",
        payment_method=PaymentMethod.ERP_EXPORT,
    )
    second = build_execution_instruction(
        settlement=settlement,
        instruction_id="INS-001",
        created_by="finance.operator",
        created_at="2026-03-30T12:05:00Z",
        payment_method=PaymentMethod.ERP_EXPORT,
    )

    assert first.payload_checksum == second.payload_checksum


def test_partner_payout_aggregation() -> None:
    payout_rows = build_partner_payouts(_sample_settlement())
    assert payout_rows == [
        {
            "settlement_id": "SET-001",
            "partner_id": "PARTNER-A",
            "currency": "SAR",
            "net_payout_total": "170.00",
        },
        {
            "settlement_id": "SET-001",
            "partner_id": "PARTNER-B",
            "currency": "SAR",
            "net_payout_total": "45.00",
        },
    ]


def test_invoice_generation_totals() -> None:
    invoice = generate_partner_invoice(
        settlement=_sample_settlement(),
        invoice_id="INV-001",
        partner_id="PARTNER-A",
        issued_at="2026-03-30T12:10:00Z",
    )
    assert str(invoice.gross_total) == "200.00"
    assert str(invoice.platform_fee_total) == "30.00"
    assert str(invoice.net_total) == "170.00"


def test_reconciliation_detects_mismatch() -> None:
    settlement = approve_settlement(
        _sample_settlement(),
        ApprovalRecord(
            approval_id="APR-001",
            approved_by="finance.manager",
            approved_at="2026-03-30T12:03:00Z",
            reason="approved for scheduled payout run",
        ),
    )
    instruction = build_execution_instruction(
        settlement=settlement,
        instruction_id="INS-001",
        created_by="finance.operator",
        created_at="2026-03-30T12:05:00Z",
    )
    report = reconcile_instruction_against_actuals(
        instruction=instruction,
        actuals={
            "gross_total": Decimal("260.00"),
            "platform_fee_total": Decimal("40.00"),
            "net_payout_total": Decimal("220.00"),
        },
        report_id="REC-001",
        checked_at="2026-03-30T12:20:00Z",
    )
    assert report.matched is False
    assert len(report.variances) == 3


def test_execution_requires_approval_and_ledgers_are_append_only() -> None:
    settlement = approve_settlement(
        _sample_settlement(),
        ApprovalRecord(
            approval_id="APR-SET-001",
            approved_by="finance.manager",
            approved_at="2026-03-30T12:03:00Z",
            reason="settlement approved",
        ),
    )
    instruction = build_execution_instruction(
        settlement=settlement,
        instruction_id="INS-001",
        created_by="finance.operator",
        created_at="2026-03-30T12:05:00Z",
    )
    execution = execute_instruction(
        instruction=instruction,
        execution_id="EXE-001",
        executed_by="finance.executor",
        executed_at="2026-03-30T12:15:00Z",
        execution_approval=approve_execution(
            ApprovalRecord(
                approval_id="APR-EXE-001",
                approved_by="finance.director",
                approved_at="2026-03-30T12:14:00Z",
                reason="execute approved instruction",
            )
        ),
    )
    ledger = LedgerTraceStore()
    ledger.append(
        build_ledger_entry(
            entry_id="LED-001",
            settlement_id="SET-001",
            reference_id=instruction.instruction_id,
            event_type="instruction_created",
            occurred_at="2026-03-30T12:05:00Z",
            payload_checksum=instruction.payload_checksum,
            metadata={"status": "instruction_ready"},
        )
    )
    ledger.append(
        build_ledger_entry(
            entry_id="LED-002",
            settlement_id="SET-001",
            reference_id=execution.execution_id,
            event_type="instruction_executed",
            occurred_at="2026-03-30T12:15:00Z",
            payload_checksum=instruction.payload_checksum,
            metadata={"status": execution.status.value},
        )
    )

    exported = export_instruction_payload(instruction)

    assert execution.execution_approval_id == "APR-EXE-001"
    assert len(ledger.list_entries()) == 2
    assert exported["execution_mode"] == "non_autonomous_export_only"
