from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from petcare.emergency_network.service import build_default_emergency_partner_availability_service


router = APIRouter(prefix="/api/ep06/emergency-network", tags=["ep06-emergency-network"])


class UpsertEmergencyPartnerAvailabilityRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    partner_clinic_id: str = Field(min_length=1)
    clinic_name: str = Field(min_length=1)
    city: str = Field(min_length=1)
    open_status: str = Field(min_length=1)
    capacity_status: str = Field(min_length=1)
    emergency_ready: bool
    estimated_eta_minutes: int = Field(ge=0)
    failover_eligible: bool
    on_call_vet_available: bool
    accepts_walk_in_emergency: bool
    operational_notes: Optional[str] = None


@router.post("/availability")
def upsert_partner_availability(payload: UpsertEmergencyPartnerAvailabilityRequest) -> dict:
    service = build_default_emergency_partner_availability_service()
    try:
        record = service.upsert_partner_availability(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(record)


@router.get("/availability/{record_id}")
def get_partner_availability(record_id: str) -> dict:
    service = build_default_emergency_partner_availability_service()
    record = service.get_partner_availability(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="emergency_partner_availability_not_found")
    return asdict(record)


@router.get("/availability/tenant/{tenant_id}")
def list_partner_availability(tenant_id: str) -> dict:
    service = build_default_emergency_partner_availability_service()
    return {
        "tenant_id": tenant_id,
        "records": [asdict(record) for record in service.list_partner_availability(tenant_id)],
    }


@router.get("/availability/tenant/{tenant_id}/ready")
def list_emergency_ready_partners(tenant_id: str) -> dict:
    service = build_default_emergency_partner_availability_service()
    return {
        "tenant_id": tenant_id,
        "records": [asdict(record) for record in service.list_emergency_ready_partners(tenant_id)],
    }
