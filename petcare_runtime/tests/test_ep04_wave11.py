from petcare.pharmacy.fastapi_app import FASTAPI_ROUTE_SPECS, dispatch_read_only_request
from petcare.pharmacy.gateway_auth import GATEWAY_AUTH_POLICIES, build_gateway_auth_context
from petcare.pharmacy.gateway_observability import (
    GATEWAY_OBSERVABILITY_EVENTS,
    build_gateway_health_payload,
    build_gateway_readiness_payload,
)
from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN
from petcare.pharmacy.repository import PharmacyRepository
from petcare.pharmacy.review import start_pharmacy_review
from petcare.pharmacy.service import authorize_prescription, create_prescription


def _repo():
    repo = PharmacyRepository({}, {})

    draft = create_prescription(
        tenant_id="tenant_001",
        pet_id="pet_001",
        consultation_id="consult_001",
        signed_note_id="note_signed",
        medication_code="MED001",
        medication_name="DrugX",
        dosage_instructions="Standard",
        quantity="1",
        created_by_user_id="vet",
    )
    prescription = authorize_prescription(
        draft,
        actor_user_id="vet",
        actor_role=ROLE_VETERINARIAN,
        signed_note_present=True,
        allergy_records=[],
        active_medication_records=[],
    )
    repo.add_prescription(prescription)

    review = start_pharmacy_review(
        prescription,
        actor_user_id="pharmacy",
        actor_role=ROLE_PHARMACY,
    )
    repo.add_review(review)

    return repo, prescription, review


def test_gateway_auth_context_success():
    result = build_gateway_auth_context(
        {
            "authorization": "Bearer token",
            "x-petcare-actor-user-id": "pharmacy",
            "x-petcare-tenant-id": "tenant_001",
        },
        surface="/review/context",
    )
    assert result["ok"] is True
    assert result["actor_user_id"] == "pharmacy"
    assert result["tenant_id"] == "tenant_001"


def test_gateway_auth_context_missing_actor_header():
    result = build_gateway_auth_context(
        {
            "authorization": "Bearer token",
        },
        surface="/review/context",
    )
    assert result["ok"] is False
    assert result["error"]["status"] == "error"
    assert result["error"]["error"]["code"] == "ACTOR_HEADER_MISSING"


def test_dispatch_read_only_request_success():
    repo, _, review = _repo()
    payload = dispatch_read_only_request(
        repo,
        route_path="/review/context",
        method="GET",
        headers={
            "authorization": "Bearer token",
            "x-petcare-actor-user-id": "pharmacy",
            "x-petcare-tenant-id": "tenant_001",
        },
        params={"review_id": review.review_id},
    )
    assert payload["response"]["status"] == "success"
    assert payload["observation"]["event_name"] == "gateway.request.handled"
    assert payload["response"]["payload"]["payload"]["review"] == review.review_id


def test_dispatch_read_only_request_auth_failure():
    repo, _, review = _repo()
    payload = dispatch_read_only_request(
        repo,
        route_path="/review/context",
        method="GET",
        headers={
            "authorization": "Bearer token",
        },
        params={"review_id": review.review_id},
    )
    assert payload["response"]["status"] == "error"
    assert payload["observation"]["status"] == "error"


def test_health_and_readiness_payloads_are_deterministic():
    health = build_gateway_health_payload()
    ready = build_gateway_readiness_payload(route_count=11)
    assert health["event_name"] == "gateway.health.reported"
    assert ready["event_name"] == "gateway.readiness.reported"
    assert ready["route_count"] == 11


def test_wave11_contracts_are_locked():
    assert GATEWAY_AUTH_POLICIES == (
        "AUTHORIZATION_BEARER_REQUIRED",
        "ACTOR_HEADER_REQUIRED",
        "TENANT_HEADER_OPTIONAL",
    )
    assert GATEWAY_OBSERVABILITY_EVENTS == (
        "gateway.health.reported",
        "gateway.readiness.reported",
        "gateway.request.handled",
    )
    assert len(FASTAPI_ROUTE_SPECS) == 13
