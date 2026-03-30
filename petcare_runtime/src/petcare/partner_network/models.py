from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


PARTNER_TYPES = {
    "clinic",
    "pharmacy",
    "diagnostics",
    "logistics",
    "emergency_provider",
    "marketplace_service",
}

VERIFICATION_STATES = {
    "draft",
    "submitted",
    "under_review",
    "verified",
    "rejected",
    "suspended",
}


@dataclass(frozen=True)
class Partner:
    partner_id: str
    tenant_id: str
    partner_type: str
    name: str
    verification_state: str
    capabilities: List[str]
    created_at: str
    updated_at: str
    verified_at: Optional[str] = None


def validate_partner_type(partner_type: str) -> None:
    if partner_type not in PARTNER_TYPES:
        raise ValueError("invalid partner_type")


def validate_verification_state(state: str) -> None:
    if state not in VERIFICATION_STATES:
        raise ValueError("invalid verification_state")
