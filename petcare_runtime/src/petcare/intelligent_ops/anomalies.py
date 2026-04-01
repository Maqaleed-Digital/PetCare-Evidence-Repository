from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AnomalyCategory(str, Enum):
    PAYMENT = "payment"
    RECONCILIATION = "reconciliation"
    DISPUTE = "dispute"
    SETTLEMENT = "settlement"


class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AnomalySignal:
    anomaly_id: str
    subject_id: str
    category: AnomalyCategory
    severity: AnomalySeverity
    detected_at: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.anomaly_id:
            raise ValueError("anomaly_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.detected_at:
            raise ValueError("detected_at is required")
        if not self.rationale:
            raise ValueError("rationale is required")


def detect_anomaly_signal(
    anomaly_id: str,
    subject_id: str,
    category: AnomalyCategory,
    severity: AnomalySeverity,
    detected_at: str,
    rationale: str,
) -> AnomalySignal:
    return AnomalySignal(
        anomaly_id=anomaly_id,
        subject_id=subject_id,
        category=category,
        severity=severity,
        detected_at=detected_at,
        rationale=rationale,
    )
