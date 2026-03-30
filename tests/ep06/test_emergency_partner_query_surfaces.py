from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.emergency_network.query import EmergencyPartnerAvailabilityQueryService
from petcare.emergency_network.repository import FileEmergencyPartnerAvailabilityRepository
from petcare.emergency_network.service import EmergencyPartnerAvailabilityService


def build_services(tmp_path: Path) -> tuple[EmergencyPartnerAvailabilityService, EmergencyPartnerAvailabilityQueryService]:
    repository = FileEmergencyPartnerAvailabilityRepository(tmp_path / "emergency_network")
    write_service = EmergencyPartnerAvailabilityService(repository)
    query_service = EmergencyPartnerAvailabilityQueryService(repository)
    return write_service, query_service


def seed_records(tmp_path: Path) -> EmergencyPartnerAvailabilityQueryService:
    write_service, query_service = build_services(tmp_path)

    write_service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_001",
        clinic_name="North Emergency Vet",
        city="Jeddah",
        open_status="open",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=14,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="North zone primary.",
    )

    write_service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_002",
        clinic_name="South Emergency Vet",
        city="Jeddah",
        open_status="limited",
        capacity_status="near_capacity",
        emergency_ready=True,
        estimated_eta_minutes=25,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="High load.",
    )

    write_service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_003",
        clinic_name="Closed Partner",
        city="Jeddah",
        open_status="closed",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=18,
        failover_eligible=False,
        on_call_vet_available=False,
        accepts_walk_in_emergency=False,
        operational_notes="Closed overnight.",
    )

    write_service.upsert_partner_availability(
        tenant_id="tenant_riyadh_001",
        partner_clinic_id="clinic_101",
        clinic_name="Riyadh Emergency Vet",
        city="Riyadh",
        open_status="open",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=12,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="Separate tenant.",
    )

    return query_service


def test_filter_partners_returns_deterministic_filtered_results(tmp_path: Path) -> None:
    query_service = seed_records(tmp_path)

    records = query_service.filter_partners(
        tenant_id="tenant_jeddah_001",
        city="Jeddah",
        emergency_ready=True,
        max_eta_minutes=20,
    )

    assert len(records) == 2
    assert records[0].partner_clinic_id == "clinic_001"
    assert records[1].partner_clinic_id == "clinic_003"


def test_list_failover_candidates_filters_to_operationally_usable_partners(tmp_path: Path) -> None:
    query_service = seed_records(tmp_path)

    records = query_service.list_failover_candidates(
        tenant_id="tenant_jeddah_001",
        city="Jeddah",
        max_eta_minutes=30,
    )

    assert len(records) == 2
    assert [item.partner_clinic_id for item in records] == ["clinic_001", "clinic_002"]


def test_operational_readiness_summary_counts_partner_states(tmp_path: Path) -> None:
    query_service = seed_records(tmp_path)

    summary = query_service.summarize_operational_readiness("tenant_jeddah_001")

    assert summary["total_partners"] == 3
    assert summary["open_count"] == 1
    assert summary["limited_count"] == 1
    assert summary["closed_count"] == 1
    assert summary["emergency_ready_count"] == 3
    assert summary["failover_eligible_count"] == 2


def test_api_round_trip_for_query_surfaces(tmp_path: Path) -> None:
    base_path = tmp_path / "api_emergency_network"
    os.environ["PETCARE_EMERGENCY_NETWORK_DIR"] = str(base_path)

    repository = FileEmergencyPartnerAvailabilityRepository(base_path)
    write_service = EmergencyPartnerAvailabilityService(repository)

    write_service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_010",
        clinic_name="Emergency Vet South",
        city="Jeddah",
        open_status="open",
        capacity_status="available",
        emergency_ready=True,
        estimated_eta_minutes=22,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="South district emergency coverage.",
    )

    write_service.upsert_partner_availability(
        tenant_id="tenant_jeddah_001",
        partner_clinic_id="clinic_011",
        clinic_name="Overflow Emergency Vet",
        city="Jeddah",
        open_status="limited",
        capacity_status="near_capacity",
        emergency_ready=True,
        estimated_eta_minutes=27,
        failover_eligible=True,
        on_call_vet_available=True,
        accepts_walk_in_emergency=True,
        operational_notes="Overflow support.",
    )

    from petcare.api.routes_ep06_wave02 import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    list_response = client.get("/api/ep06/emergency-network/query/tenant/tenant_jeddah_001")
    assert list_response.status_code == 200
    assert len(list_response.json()["records"]) == 2

    filter_response = client.get(
        "/api/ep06/emergency-network/query/tenant/tenant_jeddah_001/filter",
        params={"city": "Jeddah", "emergency_ready": "true", "max_eta_minutes": 25},
    )
    assert filter_response.status_code == 200
    assert len(filter_response.json()["records"]) == 1

    failover_response = client.get(
        "/api/ep06/emergency-network/query/tenant/tenant_jeddah_001/failover-candidates",
        params={"city": "Jeddah", "max_eta_minutes": 30},
    )
    assert failover_response.status_code == 200
    assert len(failover_response.json()["records"]) == 2

    readiness_response = client.get(
        "/api/ep06/emergency-network/query/tenant/tenant_jeddah_001/operational-readiness"
    )
    assert readiness_response.status_code == 200
    assert readiness_response.json()["total_partners"] == 2
