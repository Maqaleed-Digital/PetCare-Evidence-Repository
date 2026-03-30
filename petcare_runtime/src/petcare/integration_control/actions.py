from __future__ import annotations

from dataclasses import dataclass

from .queues import OperationalQueue, QueueItem, QueueItemStatus
from .tasks import OperatorTask, TaskAssignmentStatus, TaskPriority


@dataclass(frozen=True)
class OperatorActionRecord:
    action_id: str
    action_name: str
    actor_id: str
    entity_id: str
    occurred_at: str
    outcome: str

    def __post_init__(self) -> None:
        if not self.action_id:
            raise ValueError("action_id is required")
        if not self.action_name:
            raise ValueError("action_name is required")
        if not self.actor_id:
            raise ValueError("actor_id is required")
        if not self.entity_id:
            raise ValueError("entity_id is required")
        if not self.occurred_at:
            raise ValueError("occurred_at is required")
        if not self.outcome:
            raise ValueError("outcome is required")


def claim_queue_item(item: QueueItem, actor_id: str, claimed_at: str) -> QueueItem:
    if item.status not in {QueueItemStatus.OPEN, QueueItemStatus.RELEASED}:
        raise ValueError("queue item cannot be claimed from current state")
    return QueueItem(
        item_id=item.item_id,
        queue_type=item.queue_type,
        subject_id=item.subject_id,
        priority_rank=item.priority_rank,
        status=QueueItemStatus.CLAIMED,
        created_at=item.created_at,
        claimed_by=actor_id,
        claimed_at=claimed_at,
    )


def release_queue_item(item: QueueItem) -> QueueItem:
    if item.status != QueueItemStatus.CLAIMED:
        raise ValueError("only claimed queue items can be released")
    return QueueItem(
        item_id=item.item_id,
        queue_type=item.queue_type,
        subject_id=item.subject_id,
        priority_rank=item.priority_rank,
        status=QueueItemStatus.RELEASED,
        created_at=item.created_at,
        claimed_by=None,
        claimed_at=None,
    )


def assign_task(
    task_id: str,
    queue_item_id: str,
    assigned_to: str,
    assigned_at: str,
    priority: TaskPriority,
) -> OperatorTask:
    return OperatorTask(
        task_id=task_id,
        queue_item_id=queue_item_id,
        status=TaskAssignmentStatus.ASSIGNED,
        priority=priority,
        assigned_to=assigned_to,
        assigned_at=assigned_at,
        completed_at=None,
    )


def record_operator_action(
    action_id: str,
    action_name: str,
    actor_id: str,
    entity_id: str,
    occurred_at: str,
    outcome: str,
) -> OperatorActionRecord:
    return OperatorActionRecord(
        action_id=action_id,
        action_name=action_name,
        actor_id=actor_id,
        entity_id=entity_id,
        occurred_at=occurred_at,
        outcome=outcome,
    )
