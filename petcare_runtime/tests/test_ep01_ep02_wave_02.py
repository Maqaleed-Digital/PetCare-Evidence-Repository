from pathlib import Path

from petcare.api.routes_ep01_ep02 import get_document
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_CONSULTATION,
    PURPOSE_OWNER_SELF_SERVICE,
    PURPOSE_PLATFORM_AUDIT,
    ROLE_OWNER,
    ROLE_PLATFORM_ADMIN,
    ROLE_VETERINARIAN,
    SCOPE_DOCUMENT_SHARING,
)
from petcare.uphr.repository import FileBackedRepository
from petcare.uphr.service import UPHRService


def build_service(tmp_path: Path) -> UPHRService:
    repo = FileBackedRepository(str(tmp_path / "uphr_store.json"))
    return UPHRService(repository=repo)


def test_create_vaccination_lab_note_and_document_records(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet = service.create_pet("tenant-1", "owner-1", "Bella", "dog")

    vaccination = service.create_vaccination_record(pet.pet_id, "Rabies", "2026-03-28T10:00:00Z")
    lab = service.create_lab_result(pet.pet_id, "Central Lab", "CBC")
    note = service.create_clinical_note(pet.pet_id, "soap", "Patient stable", "vet-1")
    document = service.create_document(
        pet.pet_id,
        "lab_report",
        "docs/report1.pdf",
        "application/pdf",
        1024,
        "vet-1",
        "shared_for_care",
        "abc123",
    )

    timeline = service.get_timeline(pet.pet_id)
    assert vaccination.vaccine_name == "Rabies"
    assert lab.test_name == "CBC"
    assert note.note_type == "soap"
    assert document.document_type == "lab_report"
    assert len(timeline["vaccinations"]) == 1
    assert len(timeline["labs"]) == 1
    assert len(timeline["clinical_notes"]) == 1
    assert len(timeline["documents"]) == 1


def test_repository_persists_records(tmp_path: Path) -> None:
    repo_path = tmp_path / "uphr_store.json"
    service_a = UPHRService(repository=FileBackedRepository(str(repo_path)))
    pet = service_a.create_pet("tenant-1", "owner-1", "Bella", "dog")
    service_a.create_vaccination_record(pet.pet_id, "Rabies", "2026-03-28T10:00:00Z")

    service_b = UPHRService(repository=FileBackedRepository(str(repo_path)))
    timeline = service_b.get_timeline(pet.pet_id)
    assert len(timeline["vaccinations"]) == 1


def test_owner_can_view_document() -> None:
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
        resource_type="uphr_document",
        resource_id="doc-1",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
        document_shared=False,
    )
    result = get_document(access, resource, correlation_id="corr-doc-owner")
    assert result["allowed"] is True


def test_vet_can_view_shared_document_with_scope() -> None:
    access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes={SCOPE_DOCUMENT_SHARING},
    )
    resource = ResourceContext(
        resource_type="uphr_document",
        resource_id="doc-2",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
        document_shared=True,
        consent_record_active=True,
        consent_granted_role="Veterinarian",
        consent_purpose_of_use="purpose_consultation",
    )
    result = get_document(access, resource, correlation_id="corr-doc-vet")
    assert result["allowed"] is True
    assert result["audit_event"].event_name == "uphr.document.viewed"


def test_vet_denied_document_without_scope() -> None:
    access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes=set(),
    )
    resource = ResourceContext(
        resource_type="uphr_document",
        resource_id="doc-3",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
        document_shared=True,
    )
    result = get_document(access, resource, correlation_id="corr-doc-vet-denied")
    assert result["allowed"] is False
    assert result["audit_event"].event_name == "uphr.document.access_denied"


def test_platform_admin_can_view_document_for_audit() -> None:
    access = AccessContext(
        actor_id="admin-1",
        actor_role=ROLE_PLATFORM_ADMIN,
        tenant_id="tenant-1",
        clinic_id=None,
        purpose_of_use=PURPOSE_PLATFORM_AUDIT,
        consent_scopes=set(),
    )
    resource = ResourceContext(
        resource_type="uphr_document",
        resource_id="doc-4",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
        document_shared=False,
    )
    result = get_document(access, resource, correlation_id="corr-doc-admin")
    assert result["allowed"] is True
