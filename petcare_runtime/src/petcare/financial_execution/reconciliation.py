from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from .models import ExecutionInstruction, ReconciliationReport, ReconciliationVariance, q


def reconcile_instruction_against_actuals(
    instruction: ExecutionInstruction,
    actuals: Dict[str, Decimal | str],
    report_id: str,
    checked_at: str,
) -> ReconciliationReport:
    variances: List[ReconciliationVariance] = []

    expected = {
        "gross_total": instruction.gross_total,
        "platform_fee_total": instruction.platform_fee_total,
        "net_payout_total": instruction.net_payout_total,
    }

    for field_name, expected_amount in expected.items():
        actual_amount = q(actuals.get(field_name, "0.00"))
        if actual_amount != expected_amount:
            variances.append(
                ReconciliationVariance(
                    field_name=field_name,
                    expected_amount=expected_amount,
                    actual_amount=actual_amount,
                )
            )

    return ReconciliationReport(
        report_id=report_id,
        instruction_id=instruction.instruction_id,
        checked_at=checked_at,
        currency=instruction.currency,
        matched=len(variances) == 0,
        variances=variances,
    )
