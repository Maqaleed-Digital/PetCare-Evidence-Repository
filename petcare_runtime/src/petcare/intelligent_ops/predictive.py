from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PredictiveSignalType(str, Enum):
    EXPECTED_DELAY = "expected_delay"
    DISPUTE_LIKELIHOOD = "dispute_likelihood"
    LIQUIDITY_PRESSURE = "liquidity_pressure"


@dataclass(frozen=True)
class PredictiveSignal:
    signal_id: str
    subject_id: str
    signal_type: PredictiveSignalType
    created_at: str
    rationale: str
    advisory_only: bool

    def __post_init__(self) -> None:
        if not self.signal_id:
            raise ValueError("signal_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.created_at:
            raise ValueError("created_at is required")
        if not self.rationale:
            raise ValueError("rationale is required")
        if not self.advisory_only:
            raise ValueError("predictive signal must be advisory_only")


def create_predictive_signal(
    signal_id: str,
    subject_id: str,
    signal_type: PredictiveSignalType,
    created_at: str,
    rationale: str,
) -> PredictiveSignal:
    return PredictiveSignal(
        signal_id=signal_id,
        subject_id=subject_id,
        signal_type=signal_type,
        created_at=created_at,
        rationale=rationale,
        advisory_only=True,
    )
