from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class QueueType(str, Enum):
    FINANCE_REVIEW = "finance_review"
    RECONCILIATION_REVIEW = "reconciliation_review"
    DISPUTE_REVIEW = "dispute_review"
    APPROVAL = "approval"
    EXCEPTION = "exception"


class QueueItemStatus(str, Enum):
    OPEN = "open"
    CLAIMED = "claimed"
    RELEASED = "released"
    CLOSED = "closed"


@dataclass(frozen=True)
class QueueItem:
    item_id: str
    queue_type: QueueType
    subject_id: str
    priority_rank: int
    status: QueueItemStatus
    created_at: str
    claimed_by: str | None = None
    claimed_at: str | None = None

    def __post_init__(self) -> None:
        if not self.item_id:
            raise ValueError("item_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if self.priority_rank < 0:
            raise ValueError("priority_rank must be non-negative")
        if not self.created_at:
            raise ValueError("created_at is required")


@dataclass(frozen=True)
class OperationalQueue:
    queue_id: str
    queue_type: QueueType
    items: list[QueueItem]

    def __post_init__(self) -> None:
        if not self.queue_id:
            raise ValueError("queue_id is required")


def build_queue(queue_id: str, queue_type: QueueType) -> OperationalQueue:
    return OperationalQueue(queue_id=queue_id, queue_type=queue_type, items=[])


def enqueue_item(queue: OperationalQueue, item: QueueItem) -> OperationalQueue:
    items = list(queue.items) + [item]
    items = sorted(items, key=lambda x: (x.priority_rank, x.created_at, x.item_id))
    return OperationalQueue(queue_id=queue.queue_id, queue_type=queue.queue_type, items=items)


def reorder_queue(queue: OperationalQueue) -> OperationalQueue:
    items = sorted(queue.items, key=lambda x: (x.priority_rank, x.created_at, x.item_id))
    return OperationalQueue(queue_id=queue.queue_id, queue_type=queue.queue_type, items=items)
