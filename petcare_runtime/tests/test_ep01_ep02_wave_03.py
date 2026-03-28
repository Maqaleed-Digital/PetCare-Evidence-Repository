from pathlib import Path

from petcare.api.routes_ep01_ep02 import get_prompt_safe_timeline_summary, get_timeline
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_CONSULTATION,
    PURPOSE_OWNER_SELF_SERVICE,
    ROLE_OWNER,
    ROLE_VETERINARIAN,
    SCOPE_CARE_DELIVERY,
)
from petcare.uphr.document_validation import validate_document_metadata
from petcare.uphr.repository import FileBackedRepository
from petcare.uphr.service import UPHRService


def build_service(tmp_path: Path) -> UPHRService:
    repo = FileBackedRepository(str(tmp_path / "uphr_store.json"))
    return UPHRService(repository=repo)


def seed_pet_records(service: UPHRService) -> str:
    pet = service.create_pet("tenant-1", "owner-1", "Bella", "dog")
    service.create_vaccination_record(pet.pet_id, "Rabies", "2026-03-28T10:00:00Z")
    service.create_lab_result(pet.pet_id, "Central Lab", "CBC")
    service.create_clinical_note(
        pet.pet_id,
        "soap",
        "Owner email bella@example.com phone +966500000000 microchip 123456789012",
        "vet-1",
    )
    return pet.pet_id


def test_timeline_can_filter_by_category(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet_records(service)

    timeline = service.get_timeline(pet_id, category="vaccinations")
    assert list(timeline.keys()) == ["vaccinations", "pet_id"]
    assert len(timeline["vaccinations"]) == 1


def test_timeline_can_search(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet_records(service)

    timeline = service.get_timeline(pet_id, search_term="cbc")
    assert len(timeline["labs"]) == 1
    assert len(timeline["vaccinations"]) == 0


def test_document_validation_rejects_bad_mime_type() -> None:
    result = validate_document_metadata("application/exe", 100, "abc123")
    assert result.valid is False
    assert result.reason_code == "unsupported_mime_type"


def test_document_validation_rejects_large_document() -> None:
    result = validate_document_metadata("application/pdf", 20 * 1024 * 1024, "abc123")
    assert result.valid is False
    assert result.reason_code == "document_too_large"


def test_prompt_safe_timeline_summary_redacts_sensitive_values(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet_records(service)

    summary = service.build_prompt_safe_timeline_summary(pet_id)
    assert "[REDACTED_EMAIL]" in summary
    assert "[REDACTED_PHONE]" in summary
    assert "[REDACTED_ID]" in summary
    assert "bella@example.com" not in summary


def test_owner_can_view_timeline_route(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet_records(service)

    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.uphr_service = service

    access = AccessContext(
        actor_id="owner-1",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        purpose_of_use=PURPOSE_OWNER_SELF_SERVICE,
        consent_scopes=set(),
        owner_id="owner-1",
    )
    resource = ResourceContext(
        resource_type="pet",
        resource_id=pet_id,
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    result = get_timeline(access, resource, correlation_id="corr-wave03-owner", category="vaccinations")
    assert result["allowed"] is True
    assert result["audit_event"].event_name == "uphr.timeline.viewed"


def test_vet_can_get_prompt_safe_summary_with_care_scope(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet_records(service)

    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.uphr_service = service

    access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes={SCOPE_CARE_DELIVERY},
    )
    resource = ResourceContext(
        resource_type="pet",
        resource_id=pet_id,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
    )
    result = get_prompt_safe_timeline_summary(access, resource, correlation_id="corr-wave03-vet")
    assert result["allowed"] is True
    assert result["audit_event"].event_name == "uphr.ai_redaction.applied"
    assert "[REDACTED_EMAIL]" in result["summary"]
