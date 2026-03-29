from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AIIntakeRecord:
    id: str
    tenant_id: str
    case_id: str
    pet_id: Optional[str]
    actor_id: str
    actor_role: str
    species: str
    symptom_summary: str
    urgency_level: str
    red_flags: List[str] = field(default_factory=list)
    structured_questions: List[str] = field(default_factory=list)
    disclaimer: str = ""
    prompt_log_id: str = ""
    output_log_id: str = ""
    approval_gate_id: Optional[str] = None
    hitl_required: bool = False
    status: str = "drafted"
    created_at: str = ""
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class VetCopilotDraftRecord:
    id: str
    tenant_id: str
    case_id: str
    pet_id: Optional[str]
    actor_id: str
    actor_role: str
    soap_subjective: str
    soap_objective: str
    soap_assessment: str
    soap_plan: str
    protocol_citations: List[str] = field(default_factory=list)
    uncertainty_note: str = ""
    disclaimer: str = ""
    prompt_log_id: str = ""
    output_log_id: str = ""
    approval_gate_id: Optional[str] = None
    hitl_required: bool = False
    status: str = "drafted"
    created_at: str = ""
    ai_execution_authority: bool = False
