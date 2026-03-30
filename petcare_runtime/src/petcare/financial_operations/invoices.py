from __future__ import annotations

from .models import InvoiceLifecycleRecord, InvoiceOpsStatus


_ALLOWED_TRANSITIONS: dict[InvoiceOpsStatus, set[InvoiceOpsStatus]] = {
    InvoiceOpsStatus.DRAFT: {InvoiceOpsStatus.ISSUED},
    InvoiceOpsStatus.ISSUED: {InvoiceOpsStatus.ACKNOWLEDGED, InvoiceOpsStatus.DISPUTED, InvoiceOpsStatus.CLOSED},
    InvoiceOpsStatus.ACKNOWLEDGED: {InvoiceOpsStatus.DISPUTED, InvoiceOpsStatus.RESOLVED, InvoiceOpsStatus.CLOSED},
    InvoiceOpsStatus.DISPUTED: {InvoiceOpsStatus.RESOLVED},
    InvoiceOpsStatus.RESOLVED: {InvoiceOpsStatus.CLOSED},
    InvoiceOpsStatus.CLOSED: set(),
}


def _require_transition_allowed(current: InvoiceOpsStatus, target: InvoiceOpsStatus) -> None:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"invalid invoice transition: {current.value} -> {target.value}")


def issue_invoice(
    invoice: InvoiceLifecycleRecord,
    issued_at: str,
) -> InvoiceLifecycleRecord:
    _require_transition_allowed(invoice.status, InvoiceOpsStatus.ISSUED)
    return InvoiceLifecycleRecord(
        invoice_id=invoice.invoice_id,
        partner_id=invoice.partner_id,
        settlement_id=invoice.settlement_id,
        currency=invoice.currency,
        issued_at=issued_at,
        status=InvoiceOpsStatus.ISSUED,
        gross_total=invoice.gross_total,
        platform_fee_total=invoice.platform_fee_total,
        net_total=invoice.net_total,
        last_transition_at=issued_at,
        acknowledged_at=invoice.acknowledged_at,
        closed_at=invoice.closed_at,
        dispute_case_id=invoice.dispute_case_id,
    )


def record_invoice_acknowledgement(
    invoice: InvoiceLifecycleRecord,
    acknowledged_at: str,
) -> InvoiceLifecycleRecord:
    _require_transition_allowed(invoice.status, InvoiceOpsStatus.ACKNOWLEDGED)
    return InvoiceLifecycleRecord(
        invoice_id=invoice.invoice_id,
        partner_id=invoice.partner_id,
        settlement_id=invoice.settlement_id,
        currency=invoice.currency,
        issued_at=invoice.issued_at,
        status=InvoiceOpsStatus.ACKNOWLEDGED,
        gross_total=invoice.gross_total,
        platform_fee_total=invoice.platform_fee_total,
        net_total=invoice.net_total,
        last_transition_at=acknowledged_at,
        acknowledged_at=acknowledged_at,
        closed_at=invoice.closed_at,
        dispute_case_id=invoice.dispute_case_id,
    )


def close_invoice(
    invoice: InvoiceLifecycleRecord,
    closed_at: str,
) -> InvoiceLifecycleRecord:
    _require_transition_allowed(invoice.status, InvoiceOpsStatus.CLOSED)
    return InvoiceLifecycleRecord(
        invoice_id=invoice.invoice_id,
        partner_id=invoice.partner_id,
        settlement_id=invoice.settlement_id,
        currency=invoice.currency,
        issued_at=invoice.issued_at,
        status=InvoiceOpsStatus.CLOSED,
        gross_total=invoice.gross_total,
        platform_fee_total=invoice.platform_fee_total,
        net_total=invoice.net_total,
        last_transition_at=closed_at,
        acknowledged_at=invoice.acknowledged_at,
        closed_at=closed_at,
        dispute_case_id=invoice.dispute_case_id,
    )
