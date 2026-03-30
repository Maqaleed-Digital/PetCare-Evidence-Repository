from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .dispatch import DispatchRecord, DispatchStatus


class FinalizationStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    FINALIZED = "finalized"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class FinalizationRecord:
    finalization_id: str
    execution_id: str
    status: FinalizationStatus
    finalized_at: str
    finalized_by: str
    reconciliation_required: bool
    ledger_link_required: bool

    def __post_init__(self) -> None:
        if not self.finalization_id:
            raise ValueError("finalization_id is required")
        if not self.execution_id:
            raise ValueError("execution_id is required")
        if not self.finalized_at:
            raise ValueError("finalized_at is required")
        if not self.finalized_by:
            raise ValueError("finalized_by is required")


def finalize_settlement(
    finalization_id: str,
    execution_id: str,
    dispatch: DispatchRecord,
    finalized_at: str,
    finalized_by: str,
) -> FinalizationRecord:
    status = FinalizationStatus.FINALIZED if dispatch.status == DispatchStatus.DISPATCHED else FinalizationStatus.BLOCKED
    return FinalizationRecord(
        finalization_id=finalization_id,
        execution_id=execution_id,
        status=status,
        finalized_at=finalized_at,
        finalized_by=finalized_by,
        reconciliation_required=True,
        ledger_link_required=True,
    )
