from __future__ import annotations

import os
from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Query

from petcare.emergency_network.query import EmergencyPartnerAvailabilityQueryService
from petcare.emergency_network.repository import FileEmergencyPartnerAvailabilityRepository


router = APIRouter(prefix="/api/ep06/emergency-network/query", tags=["ep06-emergency-network-query"])


def build_query_service() -> EmergencyPartnerAvailabilityQueryService:
    base_path = os.environ.get(
        "PETCARE_EMERGENCY_NETWORK_DIR",
        "petcare_runtime/runtime_data/emergency_network",
    )
    repository = FileEmergencyPartnerAvailabilityRepository(base_path)
    return EmergencyPartnerAvailabilityQueryService(repository)


@router.get("/tenant/{tenant_id}")
def list_all_for_tenant(tenant_id: str) -> dict:
    service = build_query_service()
    records = service.list_all_for_tenant(tenant_id)
    return {
        "tenant_id": tenant_id,
        "records": [asdict(item) for item in records],
    }


@router.get("/tenant/{tenant_id}/filter")
def filter_partners(
    tenant_id: str,
    city: Optional[str] = None,
    open_status: Optional[str] = None,
    capacity_status: Optional[str] = None,
    emergency_ready: Optional[bool] = None,
    failover_eligible: Optional[bool] = None,
    on_call_vet_available: Optional[bool] = None,
    accepts_walk_in_emergency: Optional[bool] = None,
    max_eta_minutes: Optional[int] = Query(default=None, ge=0),
) -> dict:
    service = build_query_service()
    records = service.filter_partners(
        tenant_id=tenant_id,
        city=city,
        open_status=open_status,
        capacity_status=capacity_status,
        emergency_ready=emergency_ready,
        failover_eligible=failover_eligible,
        on_call_vet_available=on_call_vet_available,
        accepts_walk_in_emergency=accepts_walk_in_emergency,
        max_eta_minutes=max_eta_minutes,
    )
    return {
        "tenant_id": tenant_id,
        "records": [asdict(item) for item in records],
    }


@router.get("/tenant/{tenant_id}/failover-candidates")
def list_failover_candidates(
    tenant_id: str,
    city: Optional[str] = None,
    max_eta_minutes: Optional[int] = Query(default=None, ge=0),
) -> dict:
    service = build_query_service()
    records = service.list_failover_candidates(
        tenant_id=tenant_id,
        city=city,
        max_eta_minutes=max_eta_minutes,
    )
    return {
        "tenant_id": tenant_id,
        "records": [asdict(item) for item in records],
    }


@router.get("/tenant/{tenant_id}/operational-readiness")
def summarize_operational_readiness(tenant_id: str) -> dict:
    service = build_query_service()
    return service.summarize_operational_readiness(tenant_id)
