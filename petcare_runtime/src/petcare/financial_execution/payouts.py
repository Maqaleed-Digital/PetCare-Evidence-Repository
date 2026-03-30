from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Tuple

from .models import q, SettlementPackage


def build_partner_payouts(settlement: SettlementPackage) -> List[Dict[str, str]]:
    grouped: Dict[Tuple[str, str], Decimal] = defaultdict(lambda: Decimal("0.00"))

    for line in settlement.lines:
        key = (line.partner_id, line.currency)
        grouped[key] = q(grouped[key] + line.net_payout_amount)

    payout_rows: List[Dict[str, str]] = []
    for (partner_id, currency), amount in sorted(grouped.items()):
        payout_rows.append(
            {
                "settlement_id": settlement.settlement_id,
                "partner_id": partner_id,
                "currency": currency,
                "net_payout_total": str(q(amount)),
            }
        )
    return payout_rows
