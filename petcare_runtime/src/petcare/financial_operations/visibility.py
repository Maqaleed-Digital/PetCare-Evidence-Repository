from __future__ import annotations

from .models import (
    DisputeCase,
    FinancialVisibilitySnapshot,
    InvoiceLifecycleRecord,
    InvoiceOpsStatus,
    ReconciliationCase,
    ReconciliationStatus,
    q,
)


def build_visibility_snapshot(
    snapshot_id: str,
    generated_at: str,
    invoices: list[InvoiceLifecycleRecord],
    disputes: list[DisputeCase],
    reconciliation_cases: list[ReconciliationCase],
) -> FinancialVisibilitySnapshot:
    open_invoice_count = sum(1 for invoice in invoices if invoice.status != InvoiceOpsStatus.CLOSED)
    disputed_invoice_count = sum(1 for invoice in invoices if invoice.status == InvoiceOpsStatus.DISPUTED)
    unresolved_variance_count = sum(1 for case in reconciliation_cases if case.status != ReconciliationStatus.CLOSED)
    partner_exposure_total = q(sum(invoice.net_total for invoice in invoices if invoice.status != InvoiceOpsStatus.CLOSED))

    return FinancialVisibilitySnapshot(
        snapshot_id=snapshot_id,
        generated_at=generated_at,
        open_invoice_count=open_invoice_count,
        disputed_invoice_count=disputed_invoice_count,
        unresolved_variance_count=unresolved_variance_count,
        partner_exposure_total=partner_exposure_total,
    )
