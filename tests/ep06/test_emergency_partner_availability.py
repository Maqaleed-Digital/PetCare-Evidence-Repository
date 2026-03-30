from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.emergency_network.repository import FileEmergencyPartnerAvailabilityRepository
from petcare.emergency_network.service import EmergencyPartnerAvailabilityService


def build_service(tmp_path: Path) -> EmergencyPartnerAvailabilityService:
    repository = FileEmergencyPartnerAvailabilityRepository(tmp_path / "emergency_network")
    return EmergencyPartnerAvailabilityService(repository)


def test_upsert_partner_availability_creates_governed_record(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    record = service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_001",
        clinic_name="Jeddah Emergency Vet Center",
        city="Jeddah",
        open_status="open",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=18,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="Primary emergency coverage for north zone.",
    )

    assert record.tenant_id == "tenant_jeddah_001"
    assert record.partner_clinic_id == "clinic_001"
    assert record.emergency_ready is True
    assert record.estimated_eta_minutes == 18
    assert record.ai_execution_authority is False


def test_upsert_partner_availability_updates_existing_partner_record(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    original = service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_001",
        clinic_name="Jeddah Emergency Vet Center",
        city="Jeddah",
        open_status="open",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=18,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="Initial state.",
    )

    updated = service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_001",
        clinic_name="Jeddah Emergency Vet Center",
        city="Jeddah",
        open_status="limited",
        capacity_status="near_capacity",
        emergency_ready=True,
        estimated_eta_minutes=25,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="High load but still accepting cases.",
    )

    assert updated.id == original.id
    assert updated.open_status == "limited"
    assert updated.capacity_status == "near_capacity"
    assert updated.estimated_eta_minutes == 25


def test_list_emergency_ready_partners_filters_correctly(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_001",
        clinic_name="Clinic One",
        city="Jeddah",
        open_status="open",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=15,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes=None,
    )
    service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_002",
        clinic_name="Clinic Two",
        city="Jeddah",
        open_status="closed",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=20,
        failover_eligible=False,
        on_call_vet_available=False,
        accepts_walk_in_emergency=False,
        operational_notes=None,
    )
    service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_003",
        clinic_name="Clinic Three",
        city="Jeddah",
        open_status="open",
        capacity_status="full",
        emergency_ready=True,
        estimated_eta_minutes=30,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes=None,
    )

    records = service.list_emergency_ready_partners("tenant_jeddah_001")

    assert len(records) == 1
    assert records[0].partner_clinic_id == "clinic_001"


def test_api_round_trip_for_emergency_partner_availability(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "api_emergency_network"
    os.environ["PETCARE_EMERGENCY_NETWORK_DIR"] = str(runtime_dir)

    from petcare.api.routes_ep06_wave01 import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    create_response = client.post(
        "/api/ep06/emergency-network/availability",
        json={
            "tenant_id": "tenant_jeddah_001",
            "partner_clinic_id": "clinic_010",
            "clinic_name": "Emergency Vet South",
            "city": "Jeddah",
            "open_status": "open",
            "capacity_status": "available",
            "emergency_ready": True,
            "estimated_eta_minutes": 22,
            "failover_eligible": True,
            "on_call_vet_available": True,
            "accepts_walk_in_emergency": True,
            "operational_notes": "South district emergency coverage.",
        },
    )
    assert create_response.status_code == 200
    payload = create_response.json()
    assert payload["ai_execution_authority"] is False

    get_response = client.get(f"/api/ep06/emergency-network/availability/{payload['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["partner_clinic_id"] == "clinic_010"

    list_response = client.get("/api/ep06/emergency-network/availability/tenant/tenant_jeddah_001")
    assert list_response.status_code == 200
    assert len(list_response.json()["records"]) == 1

    ready_response = client.get("/api/ep06/emergency-network/availability/tenant/tenant_jeddah_001/ready")
    assert ready_response.status_code == 200
    assert len(ready_response.json()["records"]) == 1
