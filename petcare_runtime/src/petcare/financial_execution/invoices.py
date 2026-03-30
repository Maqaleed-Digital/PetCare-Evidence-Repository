from __future__ import annotations

from decimal import Decimal

from .models import Invoice, InvoiceLine, SettlementPackage, q


def generate_partner_invoice(
    settlement: SettlementPackage,
    invoice_id: str,
    partner_id: str,
    issued_at: str,
) -> Invoice:
    partner_lines = [line for line in settlement.lines if line.partner_id == partner_id]
    if not partner_lines:
        raise ValueError("partner has no settlement lines")

    invoice_lines = [
        InvoiceLine(
            order_id=line.order_id,
            gross_amount=line.gross_amount,
            platform_fee_amount=line.platform_fee_amount,
            net_amount=line.net_payout_amount,
        )
        for line in partner_lines
    ]

    gross_total = q(sum(line.gross_amount for line in invoice_lines))
    platform_fee_total = q(sum(line.platform_fee_amount for line in invoice_lines))
    net_total = q(sum(line.net_amount for line in invoice_lines))

    return Invoice(
        invoice_id=invoice_id,
        partner_id=partner_id,
        settlement_id=settlement.settlement_id,
        currency=partner_lines[0].currency,
        issued_at=issued_at,
        lines=invoice_lines,
        gross_total=gross_total,
        platform_fee_total=platform_fee_total,
        net_total=net_total,
    )
