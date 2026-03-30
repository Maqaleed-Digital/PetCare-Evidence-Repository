from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class EPClosureChecklistRecord:
    tenant_id: str
    epic_id: str
    has_logging_foundation: bool
    has_hitl_foundation: bool
    has_eval_foundation: bool
    has_runtime_activation: bool
    has_resolution_binding: bool
    has_dashboard_read_models: bool
    has_evidence_exports: bool
    has_governance_reports: bool
    has_no_pending_gates: bool
    has_no_drift_alerts: bool
    seal_ready: bool
    generated_at: str
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class EPGovernanceSealRecord:
    id: str
    tenant_id: str
    epic_id: str
    seal_status: str
    checklist_hash: str
    source_commit: str
    sealed_by: str
    sealed_at: str
    ai_execution_authority: bool = False
