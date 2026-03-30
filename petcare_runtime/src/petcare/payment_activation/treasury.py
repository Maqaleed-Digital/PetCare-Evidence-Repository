from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class TreasuryStatus(str, Enum):
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class TreasuryCheckRecord:
    check_id: str
    execution_id: str
    available_balance: Decimal
    required_amount: Decimal
    status: TreasuryStatus
    checked_at: str
    checked_by: str

    def __post_init__(self) -> None:
        if not self.check_id:
            raise ValueError("check_id is required")
        if not self.execution_id:
            raise ValueError("execution_id is required")
        if not self.checked_at:
            raise ValueError("checked_at is required")
        if not self.checked_by:
            raise ValueError("checked_by is required")


def run_treasury_check(
    check_id: str,
    execution_id: str,
    available_balance: Decimal,
    required_amount: Decimal,
    checked_at: str,
    checked_by: str,
) -> TreasuryCheckRecord:
    status = TreasuryStatus.SUFFICIENT if available_balance >= required_amount else TreasuryStatus.INSUFFICIENT
    return TreasuryCheckRecord(
        check_id=check_id,
        execution_id=execution_id,
        available_balance=available_balance,
        required_amount=required_amount,
        status=status,
        checked_at=checked_at,
        checked_by=checked_by,
    )
