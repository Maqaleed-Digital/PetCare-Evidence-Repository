from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecommendationClass(str, Enum):
    REVIEW = "review"
    RETRY = "retry"
    CANCEL = "cancel"
    ESCALATE = "escalate"
    PRIORITIZE = "prioritize"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"


class OperatorDisposition(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    OVERRIDE = "override"


@dataclass(frozen=True)
class RecommendationRecord:
    recommendation_id: str
    subject_id: str
    recommendation_class: RecommendationClass
    status: RecommendationStatus
    created_at: str
    rationale: str
    visible_to_operator: bool

    def __post_init__(self) -> None:
        if not self.recommendation_id:
            raise ValueError("recommendation_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.created_at:
            raise ValueError("created_at is required")
        if not self.rationale:
            raise ValueError("rationale is required")
        if not self.visible_to_operator:
            raise ValueError("recommendation must be visible_to_operator")


def create_recommendation(
    recommendation_id: str,
    subject_id: str,
    recommendation_class: RecommendationClass,
    created_at: str,
    rationale: str,
) -> RecommendationRecord:
    return RecommendationRecord(
        recommendation_id=recommendation_id,
        subject_id=subject_id,
        recommendation_class=recommendation_class,
        status=RecommendationStatus.PENDING,
        created_at=created_at,
        rationale=rationale,
        visible_to_operator=True,
    )


def set_recommendation_disposition(
    record: RecommendationRecord,
    disposition: OperatorDisposition,
) -> RecommendationRecord:
    mapped = {
        OperatorDisposition.ACCEPT: RecommendationStatus.ACCEPTED,
        OperatorDisposition.REJECT: RecommendationStatus.REJECTED,
        OperatorDisposition.OVERRIDE: RecommendationStatus.OVERRIDDEN,
    }
    return RecommendationRecord(
        recommendation_id=record.recommendation_id,
        subject_id=record.subject_id,
        recommendation_class=record.recommendation_class,
        status=mapped[disposition],
        created_at=record.created_at,
        rationale=record.rationale,
        visible_to_operator=record.visible_to_operator,
    )
