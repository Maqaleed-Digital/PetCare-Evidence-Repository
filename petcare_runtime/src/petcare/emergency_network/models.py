from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class EmergencyPartnerAvailabilityRecord:
    id: str
    tenant_id: str
    partner_clinic_id: str
    clinic_name: str
    city: str
    open_status: str
    capacity_status: str
    emergency_ready: bool
    estimated_eta_minutes: int
    failover_eligible: bool
    on_call_vet_available: bool
    accepts_walk_in_emergency: bool
    operational_notes: Optional[str]
    last_updated_at: str
    ai_execution_authority: bool = False
