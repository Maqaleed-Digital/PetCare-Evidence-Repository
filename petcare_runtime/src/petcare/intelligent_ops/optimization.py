from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OptimizationTarget(str, Enum):
    QUEUE_PRIORITY = "queue_priority"
    WORKLOAD_BALANCE = "workload_balance"
    BOTTLENECK = "bottleneck"


class SuggestionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class OptimizationSuggestion:
    suggestion_id: str
    target: OptimizationTarget
    subject_id: str
    priority: SuggestionPriority
    rationale: str
    visible_to_operator: bool

    def __post_init__(self) -> None:
        if not self.suggestion_id:
            raise ValueError("suggestion_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.rationale:
            raise ValueError("rationale is required")
        if not self.visible_to_operator:
            raise ValueError("optimization suggestion must be visible")


def suggest_queue_priority_adjustment(
    suggestion_id: str,
    subject_id: str,
    priority: SuggestionPriority,
    rationale: str,
) -> OptimizationSuggestion:
    return OptimizationSuggestion(
        suggestion_id=suggestion_id,
        target=OptimizationTarget.QUEUE_PRIORITY,
        subject_id=subject_id,
        priority=priority,
        rationale=rationale,
        visible_to_operator=True,
    )


def suggest_workload_balance(
    suggestion_id: str,
    subject_id: str,
    priority: SuggestionPriority,
    rationale: str,
) -> OptimizationSuggestion:
    return OptimizationSuggestion(
        suggestion_id=suggestion_id,
        target=OptimizationTarget.WORKLOAD_BALANCE,
        subject_id=subject_id,
        priority=priority,
        rationale=rationale,
        visible_to_operator=True,
    )
