from __future__ import annotations

from .models import InvoiceLifecycleRecord, InvoiceOpsStatus, PartnerStatement, PartnerStatementLine, q


def build_partner_statement(
    statement_id: str,
    partner_id: str,
    generated_at: str,
    invoices: list[InvoiceLifecycleRecord],
) -> PartnerStatement:
    if not invoices:
        raise ValueError("at least one invoice is required")
    if len({invoice.partner_id for invoice in invoices}) != 1:
        raise ValueError("all invoices must belong to the same partner")
    if len({invoice.currency for invoice in invoices}) != 1:
        raise ValueError("all invoices must have the same currency")

    lines = [
        PartnerStatementLine(
            invoice_id=invoice.invoice_id,
            settlement_id=invoice.settlement_id,
            invoice_status=invoice.status.value,
            gross_total=invoice.gross_total,
            net_total=invoice.net_total,
        )
        for invoice in invoices
    ]
    gross_total = q(sum(line.gross_total for line in lines))
    net_total = q(sum(line.net_total for line in lines))
    open_invoice_count = sum(1 for invoice in invoices if invoice.status != InvoiceOpsStatus.CLOSED)

    return PartnerStatement(
        statement_id=statement_id,
        partner_id=partner_id,
        currency=invoices[0].currency,
        generated_at=generated_at,
        lines=lines,
        gross_total=gross_total,
        net_total=net_total,
        open_invoice_count=open_invoice_count,
    )
