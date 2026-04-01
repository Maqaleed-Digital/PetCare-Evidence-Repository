"""Intelligent operations domain for PetCare EP-12."""

from .anomalies import (
    AnomalyCategory,
    AnomalySignal,
    AnomalySeverity,
    detect_anomaly_signal,
)
from .audit import (
    AuditEvent,
    anomaly_event_name,
    recommendation_event_name,
    trace_event_name,
    build_audit_event,
)
from .explainability import (
    ExplanationRecord,
    RecommendationTraceRecord,
    record_recommendation_trace,
)
from .optimization import (
    OptimizationSuggestion,
    OptimizationTarget,
    SuggestionPriority,
    suggest_queue_priority_adjustment,
    suggest_workload_balance,
)
from .predictive import (
    PredictiveSignal,
    PredictiveSignalType,
    create_predictive_signal,
)
from .recommendations import (
    OperatorDisposition,
    RecommendationClass,
    RecommendationRecord,
    RecommendationStatus,
    create_recommendation,
    set_recommendation_disposition,
)
from .risk import (
    RiskFactor,
    RiskScore,
    RiskScoreBand,
    calculate_risk_score,
)

__all__ = [
    "AnomalyCategory",
    "AnomalySeverity",
    "AnomalySignal",
    "AuditEvent",
    "ExplanationRecord",
    "OperatorDisposition",
    "OptimizationSuggestion",
    "OptimizationTarget",
    "PredictiveSignal",
    "PredictiveSignalType",
    "RecommendationClass",
    "RecommendationRecord",
    "RecommendationStatus",
    "RecommendationTraceRecord",
    "RiskFactor",
    "RiskScore",
    "RiskScoreBand",
    "SuggestionPriority",
    "anomaly_event_name",
    "build_audit_event",
    "calculate_risk_score",
    "create_predictive_signal",
    "create_recommendation",
    "detect_anomaly_signal",
    "record_recommendation_trace",
    "recommendation_event_name",
    "set_recommendation_disposition",
    "suggest_queue_priority_adjustment",
    "suggest_workload_balance",
    "trace_event_name",
]
