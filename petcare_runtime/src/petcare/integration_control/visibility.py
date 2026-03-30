from __future__ import annotations

from dataclasses import dataclass

from .exceptions import ExceptionCase, ExceptionStatus
from .queues import OperationalQueue, QueueItemStatus


@dataclass(frozen=True)
class OperationalControlSnapshot:
    snapshot_id: str
    generated_at: str
    open_queue_item_count: int
    claimed_queue_item_count: int
    escalated_exception_count: int
    open_exception_count: int

    def __post_init__(self) -> None:
        if not self.snapshot_id:
            raise ValueError("snapshot_id is required")
        if not self.generated_at:
            raise ValueError("generated_at is required")


def build_operational_control_snapshot(
    snapshot_id: str,
    generated_at: str,
    queues: list[OperationalQueue],
    exception_cases: list[ExceptionCase],
) -> OperationalControlSnapshot:
    items = [item for queue in queues for item in queue.items]
    open_queue_item_count = sum(1 for item in items if item.status in {QueueItemStatus.OPEN, QueueItemStatus.RELEASED})
    claimed_queue_item_count = sum(1 for item in items if item.status == QueueItemStatus.CLAIMED)
    escalated_exception_count = sum(1 for case in exception_cases if case.status == ExceptionStatus.ESCALATED)
    open_exception_count = sum(1 for case in exception_cases if case.status in {ExceptionStatus.OPEN, ExceptionStatus.ESCALATED})

    return OperationalControlSnapshot(
        snapshot_id=snapshot_id,
        generated_at=generated_at,
        open_queue_item_count=open_queue_item_count,
        claimed_queue_item_count=claimed_queue_item_count,
        escalated_exception_count=escalated_exception_count,
        open_exception_count=open_exception_count,
    )
