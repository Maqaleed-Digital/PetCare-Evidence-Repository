from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class RiskScoreBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RiskFactor:
    name: str
    weight: Decimal
    rationale: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")
        if not self.rationale:
            raise ValueError("rationale is required")


@dataclass(frozen=True)
class RiskScore:
    score_id: str
    subject_id: str
    score_value: Decimal
    band: RiskScoreBand
    calculated_at: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.score_id:
            raise ValueError("score_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.calculated_at:
            raise ValueError("calculated_at is required")
        if not self.rationale:
            raise ValueError("rationale is required")


def calculate_risk_score(
    score_id: str,
    subject_id: str,
    factors: list[RiskFactor],
    calculated_at: str,
) -> RiskScore:
    total = sum(Decimal(str(f.weight)) for f in factors)
    if total < Decimal("0.25"):
        band = RiskScoreBand.LOW
    elif total < Decimal("0.50"):
        band = RiskScoreBand.MEDIUM
    elif total < Decimal("0.75"):
        band = RiskScoreBand.HIGH
    else:
        band = RiskScoreBand.CRITICAL

    rationale = "; ".join(f"{factor.name}: {factor.rationale}" for factor in factors)

    return RiskScore(
        score_id=score_id,
        subject_id=subject_id,
        score_value=total,
        band=band,
        calculated_at=calculated_at,
        rationale=rationale or "no factors",
    )
