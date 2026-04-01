from __future__ import annotations

from dataclasses import dataclass

from .recommendations import OperatorDisposition, RecommendationRecord


@dataclass(frozen=True)
class ExplanationRecord:
    explanation_id: str
    recommendation_id: str
    rationale: str
    visible_to_operator: bool

    def __post_init__(self) -> None:
        if not self.explanation_id:
            raise ValueError("explanation_id is required")
        if not self.recommendation_id:
            raise ValueError("recommendation_id is required")
        if not self.rationale:
            raise ValueError("rationale is required")
        if not self.visible_to_operator:
            raise ValueError("explanation must be visible")


@dataclass(frozen=True)
class RecommendationTraceRecord:
    trace_id: str
    recommendation_id: str
    subject_id: str
    operator_disposition: OperatorDisposition | None
    created_at: str
    source: str

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id is required")
        if not self.recommendation_id:
            raise ValueError("recommendation_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.created_at:
            raise ValueError("created_at is required")
        if not self.source:
            raise ValueError("source is required")


def record_recommendation_trace(
    trace_id: str,
    recommendation: RecommendationRecord,
    created_at: str,
    source: str,
    operator_disposition: OperatorDisposition | None = None,
) -> RecommendationTraceRecord:
    return RecommendationTraceRecord(
        trace_id=trace_id,
        recommendation_id=recommendation.recommendation_id,
        subject_id=recommendation.subject_id,
        operator_disposition=operator_disposition,
        created_at=created_at,
        source=source,
    )
