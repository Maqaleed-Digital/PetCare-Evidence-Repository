from pathlib import Path

from petcare.api.routes_ep01_ep02 import (
    create_consent,
    latest_document_consent_allows,
    upload_document,
)
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_OWNER_SELF_SERVICE,
    ROLE_OWNER,
)
from petcare.consent.consent_repository import ConsentRepository
from petcare.uphr.repository import FileBackedRepository
from petcare.uphr.service import UPHRService


def build_uphr_service(tmp_path: Path) -> UPHRService:
    repo = FileBackedRepository(str(tmp_path / "uphr_store.json"))
    return UPHRService(repository=repo)


def build_consent_repo(tmp_path: Path) -> ConsentRepository:
    return ConsentRepository(str(tmp_path / "consent_store.json"))


def test_consent_repository_persists_and_lists_records(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.consent_repository = build_consent_repo(tmp_path)

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
        resource_id="pet-1",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    result = create_consent(access, resource, "SCOPE_DOCUMENT_SHARING", "purpose_consultation", "corr-1")
    records = routes_ep01_ep02.consent_repository.list_records_for_pet("pet-1")
    assert result["allowed"] is True
    assert len(records) == 1
    assert records[0].consent_scope == "SCOPE_DOCUMENT_SHARING"


def test_latest_document_consent_allows_true(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.consent_repository = build_consent_repo(tmp_path)

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
        resource_id="pet-1",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    create_consent(access, resource, "SCOPE_DOCUMENT_SHARING", "purpose_consultation", "corr-2")
    assert latest_document_consent_allows("pet-1") is True


def test_latest_document_consent_allows_false_without_match(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.consent_repository = build_consent_repo(tmp_path)
    assert latest_document_consent_allows("missing-pet") is False


def test_upload_document_route_success_emits_audit(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.uphr_service = build_uphr_service(tmp_path)
    pet_id = routes_ep01_ep02.uphr_service.create_pet("tenant-1", "owner-1", "Bella", "dog").pet_id

    result = upload_document(
        pet_id=pet_id,
        document_type="lab_report",
        object_storage_key="docs/file.pdf",
        mime_type="application/pdf",
        size_bytes=100,
        uploaded_by_actor_id="vet-1",
        visibility_scope="shared_for_care",
        checksum_sha256="abc123",
        correlation_id="corr-upload-success",
        tenant_id="tenant-1",
        actor_role="Veterinarian",
        clinic_id="clinic-1",
    )
    assert result["status"] == "created"
    assert result["audit_event"].event_name == "uphr.document.uploaded"


def test_upload_document_route_failure_emits_audit_payload(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.uphr_service = build_uphr_service(tmp_path)
    pet_id = routes_ep01_ep02.uphr_service.create_pet("tenant-1", "owner-1", "Bella", "dog").pet_id

    try:
        upload_document(
            pet_id=pet_id,
            document_type="lab_report",
            object_storage_key="docs/file.bad",
            mime_type="application/exe",
            size_bytes=100,
            uploaded_by_actor_id="vet-1",
            visibility_scope="shared_for_care",
            checksum_sha256="abc123",
            correlation_id="corr-upload-fail",
            tenant_id="tenant-1",
            actor_role="Veterinarian",
            clinic_id="clinic-1",
        )
    except ValueError as exc:
        payload = exc.args[0]
        assert payload["reason_code"] == "unsupported_mime_type"
        assert payload["audit_event"].event_name == "uphr.document.upload_failed"
    else:
        raise AssertionError("Expected ValueError for invalid route upload")


def test_timeline_page_count_and_order(tmp_path: Path) -> None:
    service = build_uphr_service(tmp_path)
    pet = service.create_pet("tenant-1", "owner-1", "Bella", "dog")
    service.create_clinical_note(pet.pet_id, "soap", "note", "vet-1")
    service.create_lab_result(pet.pet_id, "Lab", "CBC")
    service.create_vaccination_record(pet.pet_id, "Rabies", "2026-03-28T10:00:00Z")
    service.create_document(
        pet.pet_id,
        "lab_report",
        "docs/file.pdf",
        "application/pdf",
        100,
        "vet-1",
        "shared_for_care",
        "abc123",
    )

    timeline = service.get_timeline(pet.pet_id, page=1, page_size=2)
    assert timeline["page_count"] >= 2
    assert timeline["timeline_order"] == ["clinical_notes", "labs", "medications", "allergies", "vaccinations", "documents"]
