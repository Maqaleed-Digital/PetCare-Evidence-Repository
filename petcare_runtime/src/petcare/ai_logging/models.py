from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class PromptLogRecord:
    id: str
    timestamp: str
    actor_id: str
    actor_role: str
    tenant_id: str
    case_id: str
    pet_id: Optional[str]
    prompt_text: str
    prompt_hash: str
    model_name: str
    model_version: str
    provider: str
    context_type: str
    created_by_service: str = "petcare.ai_logging"
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class OutputLogRecord:
    id: str
    prompt_id: str
    timestamp: str
    output_text: str
    output_hash: str
    confidence: Optional[float]
    risk_flags: List[str] = field(default_factory=list)
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    created_by_service: str = "petcare.ai_logging"
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class ModelRegistryRecord:
    model_name: str
    model_version: str
    provider: str
    status: str
    safety_level: str
    registered_at: str
