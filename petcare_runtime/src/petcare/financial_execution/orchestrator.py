from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Dict

from .models import ExecutionInstruction, PaymentMethod, SettlementPackage, SettlementStatus, q


def calculate_totals(settlement: SettlementPackage) -> Dict[str, Decimal | str]:
    currency = settlement.lines[0].currency
    gross_total = q(sum(line.gross_amount for line in settlement.lines))
    platform_fee_total = q(sum(line.platform_fee_amount for line in settlement.lines))
    net_payout_total = q(sum(line.net_payout_amount for line in settlement.lines))

    if gross_total != platform_fee_total + net_payout_total:
        raise ValueError("settlement totals do not balance")

    return {
        "currency": currency,
        "gross_total": gross_total,
        "platform_fee_total": platform_fee_total,
        "net_payout_total": net_payout_total,
    }


def _instruction_checksum(payload: Dict[str, str]) -> str:
    packed = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(packed).hexdigest()


def build_execution_instruction(
    settlement: SettlementPackage,
    instruction_id: str,
    created_by: str,
    created_at: str,
    payment_method: PaymentMethod = PaymentMethod.ERP_EXPORT,
) -> ExecutionInstruction:
    if settlement.status != SettlementStatus.APPROVED:
        raise ValueError("approved settlement required before instruction creation")
    if settlement.approval is None:
        raise ValueError("approval record required before instruction creation")

    totals = calculate_totals(settlement)
    checksum_payload = {
        "instruction_id": instruction_id,
        "settlement_id": settlement.settlement_id,
        "payment_method": payment_method.value,
        "currency": str(totals["currency"]),
        "gross_total": str(totals["gross_total"]),
        "platform_fee_total": str(totals["platform_fee_total"]),
        "net_payout_total": str(totals["net_payout_total"]),
        "created_by": created_by,
        "created_at": created_at,
        "settlement_approval_id": settlement.approval.approval_id,
    }
    checksum = _instruction_checksum(checksum_payload)

    return ExecutionInstruction(
        instruction_id=instruction_id,
        settlement_id=settlement.settlement_id,
        payment_method=payment_method,
        currency=str(totals["currency"]),
        gross_total=totals["gross_total"],
        platform_fee_total=totals["platform_fee_total"],
        net_payout_total=totals["net_payout_total"],
        created_by=created_by,
        created_at=created_at,
        settlement_approval_id=settlement.approval.approval_id,
        payload_checksum=checksum,
    )
