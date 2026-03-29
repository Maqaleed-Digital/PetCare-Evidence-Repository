from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class EvalCaseRecord:
    id: str
    species: str
    symptom_cluster: str
    context_type: str
    expected_risk_flags: List[str] = field(default_factory=list)
    expected_requires_approval: bool = False
    expected_decision_class: str = "assistive"
    status: str = "active"
    created_at: str = ""
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class EvalRunRecord:
    id: str
    suite_name: str
    suite_version: str
    model_name: str
    model_version: str
    provider: str
    total_cases: int
    passed_cases: int
    pass_rate: float
    approval_alignment_rate: float
    risk_flag_alignment_rate: float
    regression_threshold_pass_rate: float
    status: str
    created_at: str
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class DriftSnapshotRecord:
    id: str
    model_name: str
    model_version: str
    provider: str
    baseline_pass_rate: float
    current_pass_rate: float
    baseline_approval_alignment_rate: float
    current_approval_alignment_rate: float
    baseline_risk_flag_alignment_rate: float
    current_risk_flag_alignment_rate: float
    pass_rate_delta: float
    approval_alignment_delta: float
    risk_flag_alignment_delta: float
    alert_status: str
    thresholds: Dict[str, float]
    created_at: str
    ai_execution_authority: bool = False
