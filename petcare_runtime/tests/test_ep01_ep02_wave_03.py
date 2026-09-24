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
    assert "vaccinations" in timeline
    assert "pet_id" in timeline
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


# ---------------------------------------------------------------------------
# MVC-HYG-UPHR-001 — identifiers match whole; text matches by substring.
# ---------------------------------------------------------------------------
_CBC_UUID = "0cbc0000-1111-4222-8333-444455556666"


def _record(**overrides):
    base = {"lab_result_id": "11111111-2222-4333-8444-555555555555", "pet_id": "pet-1",
            "lab_name": "Central Lab", "test_name": "Chemistry", "result_value_nullable": None}
    base.update(overrides)
    return base


def test_uuid_containing_term_does_not_match_text_search(tmp_path: Path, monkeypatch) -> None:
    """Deterministic regression for the flake: a record whose uuid4 id contains the
    term, and whose text does not, must not be returned by timeline search."""
    import uuid
    import petcare.uphr.service as svc
    service = build_service(tmp_path)
    pet = service.create_pet("tenant-a", "owner-a", "Luna", "cat")
    monkeypatch.setattr(svc, "uuid4", lambda: uuid.UUID(_CBC_UUID))
    service.create_vaccination_record(pet.pet_id, "Rabies", "2026-03-28T10:00:00Z")
    monkeypatch.undo()
    service.create_lab_result(pet.pet_id, "Central Lab", "CBC")
    timeline = service.get_timeline(pet.pet_id, search_term="cbc")
    assert len(timeline["labs"]) == 1
    assert timeline["vaccinations"] == [], timeline["vaccinations"]


def test_term_in_text_field_matches() -> None:
    from petcare.uphr.service import _record_matches
    assert _record_matches(_record(test_name="CBC panel"), "cbc") is True


def test_identifier_matches_only_whole() -> None:
    from petcare.uphr.service import _record_matches
    rec = _record(lab_result_id=_CBC_UUID)
    assert _record_matches(rec, _CBC_UUID.lower()) is True
    assert _record_matches(rec, _CBC_UUID[:8]) is False


def test_timeline_can_search_is_stable_over_200_runs(tmp_path: Path) -> None:
    for i in range(200):
        run_dir = tmp_path / f"run{i}"
        run_dir.mkdir()
        test_timeline_can_search(run_dir)
