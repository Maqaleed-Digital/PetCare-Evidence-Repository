from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ApprovalGateRecord:
    output_id: str
    prompt_id: str
    case_id: str
    tenant_id: str
    context_type: str
    decision_class: str
    requires_approval: bool
    allowed_roles: List[str] = field(default_factory=list)
    status: str = "pending"
    created_at: str = ""
    updated_at: str = ""
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class ApprovalDecisionRecord:
    id: str
    output_id: str
    decision: str
    approver_id: str
    approver_role: str
    reason_code: str
    notes: Optional[str]
    decided_at: str
    ai_execution_authority: bool = False
