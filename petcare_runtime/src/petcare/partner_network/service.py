from __future__ import annotations

from datetime import datetime
from typing import List

from petcare.partner_network.models import (
    Partner,
    validate_partner_type,
    validate_verification_state,
)
from petcare.partner_network.repository import PartnerRepository


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def create_partner(
    repo: PartnerRepository,
    partner_id: str,
    tenant_id: str,
    partner_type: str,
    name: str,
    capabilities: List[str],
) -> Partner:
    validate_partner_type(partner_type)

    partner = Partner(
        partner_id=partner_id,
        tenant_id=tenant_id,
        partner_type=partner_type,
        name=name,
        verification_state="draft",
        capabilities=list(capabilities),
        created_at=_now(),
        updated_at=_now(),
    )

    repo.add(partner)
    return partner


def transition_state(
    repo: PartnerRepository,
    partner_id: str,
    new_state: str,
) -> Partner:
    validate_verification_state(new_state)

    partner = repo.get(partner_id)

    updated = Partner(
        partner_id=partner.partner_id,
        tenant_id=partner.tenant_id,
        partner_type=partner.partner_type,
        name=partner.name,
        verification_state=new_state,
        capabilities=list(partner.capabilities),
        created_at=partner.created_at,
        updated_at=_now(),
        verified_at=_now() if new_state == "verified" else partner.verified_at,
    )

    repo.add(updated)
    return updated
