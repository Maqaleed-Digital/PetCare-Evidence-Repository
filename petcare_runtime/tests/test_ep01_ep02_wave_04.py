from pathlib import Path

from petcare.api.routes_ep01_ep02 import get_timeline, upload_document
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_CONSULTATION,
    PURPOSE_OWNER_SELF_SERVICE,
    ROLE_OWNER,
    ROLE_VETERINARIAN,
    SCOPE_CARE_DELIVERY,
    SCOPE_DOCUMENT_SHARING,
)
from petcare.consent.consent_service import (
    STATUS_ACTIVE,
    STATUS_REVOKED,
    create_consent_record,
    consent_allows_document_access,
    revoke_consent_record,
)
from petcare.uphr.repository import FileBackedRepository
from petcare.uphr.service import UPHRService


def build_service(tmp_path: Path) -> UPHRService:
    repo = FileBackedRepository(str(tmp_path / "uphr_store.json"))
    return UPHRService(repository=repo)


def seed_pet(service: UPHRService) -> str:
    pet = service.create_pet("tenant-1", "owner-1", "Max", "cat")
    service.create_vaccination_record(pet.pet_id, "FVRCP", "2026-03-28T10:00:00Z")
    service.create_vaccination_record(pet.pet_id, "Rabies", "2026-03-28T11:00:00Z")
    service.create_lab_result(pet.pet_id, "City Lab", "T4")
    service.create_lab_result(pet.pet_id, "City Lab", "CBC")
    service.create_lab_result(pet.pet_id, "City Lab", "Urinalysis")
    return pet.pet_id


# --- consent_allows_document_access ---

def test_consent_allows_document_access_active_match() -> None:
    record = create_consent_record(
        pet_id="p1",
        owner_id="o1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role=ROLE_VETERINARIAN,
        captured_by_actor_id="o1",
        audit_reference_id="ref-1",
    )
    assert consent_allows_document_access(
        record,
        required_scope="SCOPE_DOCUMENT_SHARING",
        required_purpose=PURPOSE_CONSULTATION,
        required_role=ROLE_VETERINARIAN,
    ) is True


def test_consent_allows_document_access_revoked_denied() -> None:
    record = create_consent_record(
        pet_id="p1",
        owner_id="o1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role=ROLE_VETERINARIAN,
        captured_by_actor_id="o1",
        audit_reference_id="ref-2",
    )
    revoked = revoke_consent_record(record)
    assert consent_allows_document_access(
        revoked,
        required_scope="SCOPE_DOCUMENT_SHARING",
        required_purpose=PURPOSE_CONSULTATION,
        required_role=ROLE_VETERINARIAN,
    ) is False


def test_consent_allows_document_access_wrong_role_denied() -> None:
    record = create_consent_record(
        pet_id="p1",
        owner_id="o1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role="Pharmacy Operator",
        captured_by_actor_id="o1",
        audit_reference_id="ref-3",
    )
    assert consent_allows_document_access(
        record,
        required_scope="SCOPE_DOCUMENT_SHARING",
        required_purpose=PURPOSE_CONSULTATION,
        required_role=ROLE_VETERINARIAN,
    ) is False


# --- authorize_view_document with consent linkage ---

def test_vet_document_access_denied_without_active_consent(tmp_path: Path) -> None:
    from petcare.auth.access_control import authorize_view_document, SCOPE_DOCUMENT_SHARING
    access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes={SCOPE_DOCUMENT_SHARING},
    )
    resource = ResourceContext(
        resource_type="document",
        resource_id="doc-1",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
        document_shared=True,
        consent_record_active=False,  # no active consent
        consent_granted_role=ROLE_VETERINARIAN,
        consent_purpose_of_use=PURPOSE_CONSULTATION,
    )
    decision = authorize_view_document(access, resource)
    assert decision.allowed is False
    assert decision.reason_code == "document_missing_active_consent"


def test_vet_document_access_allowed_with_active_consent(tmp_path: Path) -> None:
    from petcare.auth.access_control import authorize_view_document, SCOPE_DOCUMENT_SHARING
    access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes={SCOPE_DOCUMENT_SHARING},
    )
    resource = ResourceContext(
        resource_type="document",
        resource_id="doc-1",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
        document_shared=True,
        consent_record_active=True,
        consent_granted_role=ROLE_VETERINARIAN,
        consent_purpose_of_use=PURPOSE_CONSULTATION,
    )
    decision = authorize_view_document(access, resource)
    assert decision.allowed is True
    assert decision.reason_code == "vet_document_shared"


# --- timeline pagination ---

def test_timeline_pagination_page_1(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet(service)

    timeline = service.get_timeline(pet_id, page=1, page_size=2)
    assert len(timeline["vaccinations"]) == 2
    assert len(timeline["labs"]) == 2


def test_timeline_pagination_page_2(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet(service)

    timeline = service.get_timeline(pet_id, page=2, page_size=2)
    assert len(timeline["vaccinations"]) == 0  # only 2 vaccinations total
    assert len(timeline["labs"]) == 1           # 3 labs, page 2 has 1


def test_timeline_pagination_route_passes_params(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet_id = seed_pet(service)

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
    result = get_timeline(access, resource, correlation_id="corr-wave04-page", page=1, page_size=1)
    assert result["allowed"] is True
    assert len(result["timeline"]["vaccinations"]) == 1
    assert len(result["timeline"]["labs"]) == 1


# --- upload_document route ---

def test_upload_document_owner_valid(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet = service.create_pet("tenant-1", "owner-1", "Luna", "dog")

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
        resource_id=pet.pet_id,
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    result = upload_document(
        access=access,
        resource=resource,
        correlation_id="corr-wave04-upload",
        document_type="lab_report",
        object_storage_key="pets/luna/lab_report.pdf",
        mime_type="application/pdf",
        size_bytes=500_000,
        visibility_scope="owner_and_vet",
        checksum_sha256="abc123def456",
    )
    assert result["allowed"] is True
    assert result["uploaded"] is True
    assert "document_id" in result
    assert result["audit_event"].event_name == "uphr.document.uploaded"


def test_upload_document_rejected_bad_mime(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    pet = service.create_pet("tenant-1", "owner-1", "Luna", "dog")

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
        resource_id=pet.pet_id,
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    result = upload_document(
        access=access,
        resource=resource,
        correlation_id="corr-wave04-reject",
        document_type="lab_report",
        object_storage_key="pets/luna/malware.exe",
        mime_type="application/exe",
        size_bytes=100,
        visibility_scope="owner_only",
        checksum_sha256="abc123def456",
    )
    assert result["allowed"] is True
    assert result["uploaded"] is False
    assert result["reason_code"] == "unsupported_mime_type"
    assert result["audit_event"].event_name == "uphr.document.upload_rejected"
