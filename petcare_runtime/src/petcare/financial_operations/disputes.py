from __future__ import annotations

from .models import (
    DisputeCase,
    DisputeEvidenceRef,
    DisputeResolutionRecord,
    DisputeStatus,
    InvoiceLifecycleRecord,
    InvoiceOpsStatus,
)


def create_dispute(
    dispute_id: str,
    invoice: InvoiceLifecycleRecord,
    opened_at: str,
    opened_by: str,
    reason: str,
    evidence_refs: list[DisputeEvidenceRef],
) -> tuple[DisputeCase, InvoiceLifecycleRecord]:
    if invoice.status not in {InvoiceOpsStatus.ISSUED, InvoiceOpsStatus.ACKNOWLEDGED}:
        raise ValueError("invoice cannot enter dispute from current state")

    dispute = DisputeCase(
        dispute_id=dispute_id,
        invoice_id=invoice.invoice_id,
        partner_id=invoice.partner_id,
        status=DisputeStatus.OPEN,
        opened_at=opened_at,
        opened_by=opened_by,
        reason=reason,
        evidence_refs=evidence_refs,
    )

    disputed_invoice = InvoiceLifecycleRecord(
        invoice_id=invoice.invoice_id,
        partner_id=invoice.partner_id,
        settlement_id=invoice.settlement_id,
        currency=invoice.currency,
        issued_at=invoice.issued_at,
        status=InvoiceOpsStatus.DISPUTED,
        gross_total=invoice.gross_total,
        platform_fee_total=invoice.platform_fee_total,
        net_total=invoice.net_total,
        last_transition_at=opened_at,
        acknowledged_at=invoice.acknowledged_at,
        closed_at=invoice.closed_at,
        dispute_case_id=dispute_id,
    )
    return dispute, disputed_invoice


def resolve_dispute(
    dispute: DisputeCase,
    resolved_at: str,
    resolved_by: str,
    reason: str,
) -> DisputeCase:
    if dispute.status not in {DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW}:
        raise ValueError("dispute cannot be resolved from current state")
    return DisputeCase(
        dispute_id=dispute.dispute_id,
        invoice_id=dispute.invoice_id,
        partner_id=dispute.partner_id,
        status=DisputeStatus.RESOLVED,
        opened_at=dispute.opened_at,
        opened_by=dispute.opened_by,
        reason=dispute.reason,
        evidence_refs=dispute.evidence_refs,
        resolution=DisputeResolutionRecord(
            resolution_id=f"{dispute.dispute_id}-resolution",
            resolved_by=resolved_by,
            resolved_at=resolved_at,
            reason=reason,
        ),
        closed_at=dispute.closed_at,
    )
