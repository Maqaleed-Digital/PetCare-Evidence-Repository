from __future__ import annotations

from decimal import Decimal

from petcare.intelligent_ops import (
    AnomalyCategory,
    AnomalySeverity,
    OperatorDisposition,
    PredictiveSignalType,
    RecommendationClass,
    SuggestionPriority,
    anomaly_event_name,
    build_audit_event,
    calculate_risk_score,
    create_predictive_signal,
    create_recommendation,
    detect_anomaly_signal,
    recommendation_event_name,
    record_recommendation_trace,
    set_recommendation_disposition,
    suggest_queue_priority_adjustment,
    suggest_workload_balance,
    trace_event_name,
)
from petcare.intelligent_ops.risk import RiskFactor
from petcare.intelligent_ops.explainability import ExplanationRecord


def test_anomaly_and_risk_models_are_advisory() -> None:
    anomaly = detect_anomaly_signal(
        anomaly_id="ANM-001",
        subject_id="EXEC-001",
        category=AnomalyCategory.PAYMENT,
        severity=AnomalySeverity.HIGH,
        detected_at="2026-03-31T00:00:00Z",
        rationale="unexpected payment timing deviation",
    )
    risk = calculate_risk_score(
        score_id="RSK-001",
        subject_id="EXEC-001",
        factors=[
            RiskFactor(name="timing_deviation", weight=Decimal("0.35"), rationale="payment timing outlier"),
            RiskFactor(name="partner_history", weight=Decimal("0.20"), rationale="previous dispute history"),
        ],
        calculated_at="2026-03-31T00:01:00Z",
    )

    assert anomaly.category.value == "payment"
    assert risk.band.value == "high"


def test_recommendations_are_visible_and_overrideable() -> None:
    rec = create_recommendation(
        recommendation_id="REC-001",
        subject_id="QUEUE-001",
        recommendation_class=RecommendationClass.PRIORITIZE,
        created_at="2026-03-31T00:02:00Z",
        rationale="high backlog and aging detected",
    )
    overridden = set_recommendation_disposition(rec, OperatorDisposition.OVERRIDE)

    assert rec.visible_to_operator is True
    assert overridden.status.value == "overridden"


def test_optimization_suggestions_are_visible_only() -> None:
    queue_suggestion = suggest_queue_priority_adjustment(
        suggestion_id="OPT-001",
        subject_id="QUEUE-001",
        priority=SuggestionPriority.HIGH,
        rationale="critical items aging faster than SLA threshold",
    )
    workload_suggestion = suggest_workload_balance(
        suggestion_id="OPT-002",
        subject_id="TEAM-001",
        priority=SuggestionPriority.MEDIUM,
        rationale="operator workload imbalance detected",
    )

    assert queue_suggestion.visible_to_operator is True
    assert workload_suggestion.visible_to_operator is True


def test_predictive_signals_remain_advisory_only() -> None:
    signal = create_predictive_signal(
        signal_id="PRD-001",
        subject_id="PARTNER-001",
        signal_type=PredictiveSignalType.DISPUTE_LIKELIHOOD,
        created_at="2026-03-31T00:03:00Z",
        rationale="historical dispute clustering indicates elevated likelihood",
    )

    assert signal.advisory_only is True
    assert signal.signal_type.value == "dispute_likelihood"


def test_explainability_and_traceability_are_required() -> None:
    rec = create_recommendation(
        recommendation_id="REC-002",
        subject_id="EXEC-002",
        recommendation_class=RecommendationClass.REVIEW,
        created_at="2026-03-31T00:04:00Z",
        rationale="combined anomaly and risk score justify review",
    )
    explanation = ExplanationRecord(
        explanation_id="EXP-001",
        recommendation_id=rec.recommendation_id,
        rationale="payment anomaly high severity plus elevated partner risk",
        visible_to_operator=True,
    )
    trace = record_recommendation_trace(
        trace_id="TRC-001",
        recommendation=rec,
        created_at="2026-03-31T00:05:00Z",
        source="rule+signal",
        operator_disposition=OperatorDisposition.REJECT,
    )

    assert explanation.visible_to_operator is True
    assert trace.operator_disposition.value == "reject"


def test_ep12_audit_events_are_scoped() -> None:
    anomaly_event = build_audit_event(
        event_id="AUD-001",
        event_name=anomaly_event_name("detected"),
        entity_id="ANM-001",
        occurred_at="2026-03-31T00:06:00Z",
        actor_id="system",
    )
    recommendation_event = build_audit_event(
        event_id="AUD-002",
        event_name=recommendation_event_name("created"),
        entity_id="REC-001",
        occurred_at="2026-03-31T00:07:00Z",
        actor_id="system",
    )
    trace_event = build_audit_event(
        event_id="AUD-003",
        event_name=trace_event_name("recorded"),
        entity_id="TRC-001",
        occurred_at="2026-03-31T00:08:00Z",
        actor_id="operator.a",
    )

    assert anomaly_event.event_name == "intelligent_ops.anomaly.detected"
    assert recommendation_event.event_name == "intelligent_ops.recommendation.created"
    assert trace_event.event_name == "intelligent_ops.trace.recorded"
