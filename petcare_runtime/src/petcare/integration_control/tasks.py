from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class TaskAssignmentStatus(str, Enum):
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    RELEASED = "released"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class OperatorTask:
    task_id: str
    queue_item_id: str
    status: TaskAssignmentStatus
    priority: TaskPriority
    assigned_to: str | None
    assigned_at: str | None
    completed_at: str | None

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.queue_item_id:
            raise ValueError("queue_item_id is required")
