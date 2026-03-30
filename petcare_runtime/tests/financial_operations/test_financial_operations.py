from __future__ import annotations

from decimal import Decimal

import pytest

from petcare.financial_execution.models import ApprovalRecord, ExecutionInstruction, PaymentMethod, SettlementLine, SettlementPackage
from petcare.financial_execution.approval import approve_settlement
from petcare.financial_execution.orchestrator import build_execution_instruction
from petcare.financial_operations import (
    DisputeEvidenceRef,
    InvoiceLifecycleRecord,
    InvoiceOpsStatus,
    PaymentTrackingStatus,
    ReconciliationResolutionRecord,
    build_audit_event,
    build_partner_statement,
    build_visibility_snapshot,
    close_invoice,
    create_dispute,
    detect_reconciliation_case,
    dispute_transition_event_name,
    invoice_transition_event_name,
    issue_invoice,
    record_external_signal,
    record_invoice_acknowledgement,
    reconciliation_transition_event_name,
    resolve_dispute,
    resolve_reconciliation_case,
    start_payment_tracking,
    transition_payment_tracking,
)


def _sample_instruction() -> ExecutionInstruction:
    settlement = SettlementPackage(
        settlement_id="SET-EP09-001",
        prepared_at="2026-03-30T19:00:00Z",
        lines=[
            SettlementLine(
                order_id="ORD-EP09-001",
                partner_id="PARTNER-A",
                currency="SAR",
                gross_amount=Decimal("120.00"),
                platform_fee_amount=Decimal("20.00"),
                net_payout_amount=Decimal("100.00"),
            )
        ],
    )
    approved = approve_settlement(
        settlement,
        ApprovalRecord(
            approval_id="APR-EP09-001",
            approved_by="finance.manager",
            approved_at="2026-03-30T19:02:00Z",
            reason="approved for operations test",
        ),
    )
    return build_execution_instruction(
        settlement=approved,
        instruction_id="INS-EP09-001",
        created_by="finance.operator",
        created_at="2026-03-30T19:05:00Z",
        payment_method=PaymentMethod.ERP_EXPORT,
    )


def _draft_invoice() -> InvoiceLifecycleRecord:
    return InvoiceLifecycleRecord(
        invoice_id="INV-EP09-001",
        partner_id="PARTNER-A",
        settlement_id="SET-EP09-001",
        currency="SAR",
        issued_at=None,
        status=InvoiceOpsStatus.DRAFT,
        gross_total=Decimal("120.00"),
        platform_fee_total=Decimal("20.00"),
        net_total=Decimal("100.00"),
        last_transition_at="2026-03-30T19:00:00Z",
    )


def test_invoice_lifecycle_requires_permitted_transitions() -> None:
    draft = _draft_invoice()
    issued = issue_invoice(draft, "2026-03-30T19:10:00Z")
    acknowledged = record_invoice_acknowledgement(issued, "2026-03-30T19:15:00Z")
    closed = close_invoice(acknowledged, "2026-03-30T19:20:00Z")

    assert issued.status == InvoiceOpsStatus.ISSUED
    assert acknowledged.status == InvoiceOpsStatus.ACKNOWLEDGED
    assert closed.status == InvoiceOpsStatus.CLOSED

    with pytest.raises(ValueError):
        issue_invoice(closed, "2026-03-30T19:25:00Z")


def test_payment_status_tracking_is_external_aware_but_not_autonomous() -> None:
    record = start_payment_tracking(
        instruction_id="INS-EP09-001",
        started_at="2026-03-30T19:00:00Z",
        external_reference_id="EXT-REF-001",
    )
    signaled = record_external_signal(
        record,
        signaled_at="2026-03-30T19:05:00Z",
        signal_source="gateway.webhook",
        payload_ref="obj://signal/001",
    )
    reviewed = transition_payment_tracking(
        signaled,
        target_status=PaymentTrackingStatus.UNDER_REVIEW,
        transitioned_at="2026-03-30T19:07:00Z",
    )
    matched = transition_payment_tracking(
        reviewed,
        target_status=PaymentTrackingStatus.MATCHED,
        transitioned_at="2026-03-30T19:10:00Z",
    )

    assert matched.status == PaymentTrackingStatus.MATCHED
    assert matched.last_signal_source == "gateway.webhook"


def test_reconciliation_case_requires_human_resolution_record() -> None:
    case = detect_reconciliation_case(
        case_id="REC-EP09-001",
        instruction_id="INS-EP09-001",
        currency="SAR",
        expected_total=Decimal("100.00"),
        actual_total=Decimal("90.00"),
        detected_at="2026-03-30T19:30:00Z",
    )
    resolved = resolve_reconciliation_case(
        case,
        ReconciliationResolutionRecord(
            resolution_id="RES-REC-001",
            resolved_by="finance.reviewer",
            resolved_at="2026-03-30T19:35:00Z",
            reason="approved documented adjustment",
        ),
    )

    assert case.variance_total == Decimal("-10.00")
    assert resolved.status.value == "resolved"
    assert resolved.resolution is not None


def test_dispute_workflow_links_invoice_and_requires_reason() -> None:
    issued = issue_invoice(_draft_invoice(), "2026-03-30T19:10:00Z")
    dispute, disputed_invoice = create_dispute(
        dispute_id="DSP-001",
        invoice=issued,
        opened_at="2026-03-30T19:12:00Z",
        opened_by="partner.user",
        reason="fee discrepancy claimed",
        evidence_refs=[
            DisputeEvidenceRef(
                evidence_id="EVD-001",
                reference_uri="obj://evidence/dispute-001",
                uploaded_at="2026-03-30T19:12:30Z",
            )
        ],
    )
    resolved = resolve_dispute(
        dispute,
        resolved_at="2026-03-30T19:20:00Z",
        resolved_by="finance.manager",
        reason="fee calculation validated and explained",
    )

    assert disputed_invoice.status == InvoiceOpsStatus.DISPUTED
    assert disputed_invoice.dispute_case_id == "DSP-001"
    assert resolved.status.value == "resolved"


def test_partner_statement_and_visibility_are_deterministic() -> None:
    issued = issue_invoice(_draft_invoice(), "2026-03-30T19:10:00Z")
    closed = close_invoice(record_invoice_acknowledgement(issued, "2026-03-30T19:12:00Z"), "2026-03-30T19:30:00Z")

    second_invoice = InvoiceLifecycleRecord(
        invoice_id="INV-EP09-002",
        partner_id="PARTNER-A",
        settlement_id="SET-EP09-002",
        currency="SAR",
        issued_at="2026-03-30T19:11:00Z",
        status=InvoiceOpsStatus.DISPUTED,
        gross_total=Decimal("80.00"),
        platform_fee_total=Decimal("10.00"),
        net_total=Decimal("70.00"),
        last_transition_at="2026-03-30T19:14:00Z",
        dispute_case_id="DSP-002",
    )

    statement = build_partner_statement(
        statement_id="STM-001",
        partner_id="PARTNER-A",
        generated_at="2026-03-30T19:40:00Z",
        invoices=[closed, second_invoice],
    )

    rec_case = detect_reconciliation_case(
        case_id="REC-002",
        instruction_id="INS-EP09-002",
        currency="SAR",
        expected_total=Decimal("70.00"),
        actual_total=Decimal("65.00"),
        detected_at="2026-03-30T19:41:00Z",
    )

    visibility = build_visibility_snapshot(
        snapshot_id="VIS-001",
        generated_at="2026-03-30T19:45:00Z",
        invoices=[closed, second_invoice],
        disputes=[],
        reconciliation_cases=[rec_case],
    )

    assert str(statement.gross_total) == "200.00"
    assert str(statement.net_total) == "170.00"
    assert statement.open_invoice_count == 1
    assert visibility.open_invoice_count == 1
    assert visibility.disputed_invoice_count == 1
    assert visibility.unresolved_variance_count == 1
    assert str(visibility.partner_exposure_total) == "70.00"


def test_ep09_audit_event_names_are_scoped() -> None:
    invoice_event = build_audit_event(
        event_id="AUD-001",
        event_name=invoice_transition_event_name("issued"),
        entity_id="INV-EP09-001",
        occurred_at="2026-03-30T19:10:00Z",
        actor_id="finance.operator",
    )
    dispute_event = build_audit_event(
        event_id="AUD-002",
        event_name=dispute_transition_event_name("resolved"),
        entity_id="DSP-001",
        occurred_at="2026-03-30T19:20:00Z",
        actor_id="finance.manager",
    )
    reconciliation_event = build_audit_event(
        event_id="AUD-003",
        event_name=reconciliation_transition_event_name("resolved"),
        entity_id="REC-001",
        occurred_at="2026-03-30T19:35:00Z",
        actor_id="finance.reviewer",
    )

    assert invoice_event.event_name == "financial_ops.invoice.issued"
    assert dispute_event.event_name == "financial_ops.dispute.resolved"
    assert reconciliation_event.event_name == "financial_ops.reconciliation.resolved"
