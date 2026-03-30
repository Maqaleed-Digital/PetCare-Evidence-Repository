from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class EvidenceExportRecord:
    id: str
    tenant_id: str
    case_id: str
    export_type: str
    prompt_log_ids: List[str] = field(default_factory=list)
    output_log_ids: List[str] = field(default_factory=list)
    gate_ids: List[str] = field(default_factory=list)
    runtime_artifact_ids: List[str] = field(default_factory=list)
    resolution_ids: List[str] = field(default_factory=list)
    signoff_ids: List[str] = field(default_factory=list)
    report_id: str = ""
    manifest_hash: str = ""
    created_at: str = ""
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class GovernanceReportRecord:
    id: str
    tenant_id: str
    scope_type: str
    scope_id: str
    summary_counts: Dict[str, int]
    risk_summary: Dict[str, int]
    governance_state: str
    report_hash: str
    created_at: str
    ai_execution_authority: bool = False
