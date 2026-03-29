from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class GovernanceOverviewRecord:
    tenant_id: str
    total_prompt_logs: int
    total_output_logs: int
    total_pending_gates: int
    total_approved_gates: int
    total_rejected_gates: int
    total_eval_runs: int
    total_drift_alerts: int
    total_ai_intake_records: int
    total_vet_copilot_records: int
    total_resolutions: int
    total_signoffs: int
    generated_at: str
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class OperationalAlertRecord:
    tenant_id: str
    category: str
    severity: str
    reference_id: str
    case_id: str
    message: str
    generated_at: str
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class CaseGovernanceViewRecord:
    tenant_id: str
    case_id: str
    prompt_log_ids: List[str] = field(default_factory=list)
    output_log_ids: List[str] = field(default_factory=list)
    gate_statuses: List[str] = field(default_factory=list)
    runtime_artifact_ids: List[str] = field(default_factory=list)
    resolution_ids: List[str] = field(default_factory=list)
    signoff_ids: List[str] = field(default_factory=list)
    latest_drift_alert_status: str = "none"
    governance_state: str = "unreviewed"
    generated_at: str = ""
    ai_execution_authority: bool = False
