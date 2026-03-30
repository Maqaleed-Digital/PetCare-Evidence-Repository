from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from petcare.partner_network.repository import PartnerRepository
from petcare.partner_network.service import create_partner, transition_state
from petcare.partner_network.query import get_verified_partners

router = APIRouter(tags=["ep07-wave01"])

repo = PartnerRepository()


class PartnerCreateRequest(BaseModel):
    partner_id: str
    tenant_id: str
    partner_type: str
    name: str
    capabilities: List[str]


class PartnerStateRequest(BaseModel):
    partner_id: str
    new_state: str


@router.post("/ep07/partners/create")
def create_partner_api(payload: PartnerCreateRequest):
    partner = create_partner(
        repo=repo,
        partner_id=payload.partner_id,
        tenant_id=payload.tenant_id,
        partner_type=payload.partner_type,
        name=payload.name,
        capabilities=payload.capabilities,
    )
    return partner.__dict__


@router.post("/ep07/partners/state")
def update_partner_state(payload: PartnerStateRequest):
    partner = transition_state(
        repo=repo,
        partner_id=payload.partner_id,
        new_state=payload.new_state,
    )
    return partner.__dict__


@router.get("/ep07/partners/verified")
def list_verified():
    return [p.__dict__ for p in get_verified_partners(repo)]
