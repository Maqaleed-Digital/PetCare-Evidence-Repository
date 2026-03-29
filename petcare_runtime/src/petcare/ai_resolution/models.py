from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ApprovalResolutionRecord:
    id: str
    tenant_id: str
    case_id: str
    artifact_type: str
    artifact_id: str
    output_id: str
    gate_status: str
    resolved_by: str
    resolved_role: str
    resolution_action: str
    resolution_notes: Optional[str]
    created_at: str
    ai_execution_authority: bool = False


@dataclass(frozen=True)
class ClinicalSignoffBindingRecord:
    id: str
    tenant_id: str
    case_id: str
    artifact_type: str
    artifact_id: str
    veterinarian_id: str
    veterinarian_role: str
    final_note_hash: str
    signoff_status: str
    signed_at: str
    immutable_after_signoff: bool = True
    ai_execution_authority: bool = False
