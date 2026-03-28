from pathlib import Path

from petcare.api.routes_ep01_ep02 import (
    create_consent,
    latest_document_consent_allows,
    revoke_consent,
    upload_document,
)
from petcare.audit.audit_service import AuditEvent, emit_audit_event
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_CONSULTATION,
    PURPOSE_OWNER_SELF_SERVICE,
    ROLE_OWNER,
    ROLE_VETERINARIAN,
    SCOPE_CARE_DELIVERY,
    authorize_upload_document,
)
from petcare.consent.consent_repository import ConsentRepository
from petcare.consent.consent_service import (
    STATUS_ACTIVE,
    STATUS_REVOKED,
    create_consent_record,
    revoke_consent_record,
)
from petcare.uphr.repository import FileBackedRepository
from petcare.uphr.service import UPHRService


def build_uphr_service(tmp_path: Path) -> UPHRService:
    repo = FileBackedRepository(str(tmp_path / "uphr_store.json"))
    return UPHRService(repository=repo)


def build_consent_repo(tmp_path: Path) -> ConsentRepository:
    return ConsentRepository(str(tmp_path / "consent_store.json"))


# --- consent revocation-aware lookup ---

def test_latest_active_matching_record_returns_none_when_all_revoked(tmp_path: Path) -> None:
    repo = build_consent_repo(tmp_path)
    record = create_consent_record(
        pet_id="pet-1",
        owner_id="owner-1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role=ROLE_VETERINARIAN,
        captured_by_actor_id="owner-1",
        audit_reference_id="ref-1",
    )
    repo.add_record(record)
    revoked = revoke_consent_record(record)
    repo.update_record(revoked)  # update in place — replaces the active entry

    result = repo.latest_active_matching_record(
        pet_id="pet-1",
        required_scope="SCOPE_DOCUMENT_SHARING",
        required_purpose=PURPOSE_CONSULTATION,
        required_role=ROLE_VETERINARIAN,
    )
    assert result is None


def test_latest_active_matching_record_returns_record_when_active(tmp_path: Path) -> None:
    repo = build_consent_repo(tmp_path)
    record = create_consent_record(
        pet_id="pet-1",
        owner_id="owner-1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role=ROLE_VETERINARIAN,
        captured_by_actor_id="owner-1",
        audit_reference_id="ref-2",
    )
    repo.add_record(record)

    result = repo.latest_active_matching_record(
        pet_id="pet-1",
        required_scope="SCOPE_DOCUMENT_SHARING",
        required_purpose=PURPOSE_CONSULTATION,
        required_role=ROLE_VETERINARIAN,
    )
    assert result is not None
    assert result.status == STATUS_ACTIVE


def test_latest_document_consent_allows_false_after_revocation(tmp_path: Path) -> None:
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

    consent_result = create_consent(
        access, resource, "SCOPE_DOCUMENT_SHARING", PURPOSE_CONSULTATION, "corr-grant"
    )
    assert latest_document_consent_allows("pet-1") is True

    revoke_consent(access, resource, consent_result["consent_record"], "corr-revoke")
    assert latest_document_consent_allows("pet-1") is False


# --- upload route authorization before persistence ---

def test_authorize_upload_document_owner_allowed() -> None:
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
    decision = authorize_upload_document(access, resource)
    assert decision.allowed is True
    assert decision.reason_code == "owner_upload_document"


def test_authorize_upload_document_vet_allowed_with_care_scope() -> None:
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
        resource_id="pet-1",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
    )
    decision = authorize_upload_document(access, resource)
    assert decision.allowed is True
    assert decision.reason_code == "vet_upload_document"


def test_upload_document_denied_before_persistence_on_wrong_owner(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.uphr_service = build_uphr_service(tmp_path)
    pet_id = routes_ep01_ep02.uphr_service.create_pet("tenant-1", "owner-1", "Bella", "dog").pet_id

    try:
        upload_document(
            pet_id=pet_id,
            document_type="lab_report",
            object_storage_key="docs/file.pdf",
            mime_type="application/pdf",
            size_bytes=100,
            uploaded_by_actor_id="owner-99",
            visibility_scope="owner_only",
            checksum_sha256="abc123",
            correlation_id="corr-auth-denied",
            tenant_id="tenant-1",
            actor_role=ROLE_OWNER,
            clinic_id=None,
            owner_id="owner-1",      # resource owner
            purpose_of_use=PURPOSE_OWNER_SELF_SERVICE,
        )
    except ValueError as exc:
        payload = exc.args[0]
        assert payload["reason_code"] == "owner_not_authorized"
        assert payload["audit_event"].event_name == "access.denied"
        # No document created — authorization denied before persistence.
        timeline = routes_ep01_ep02.uphr_service.get_timeline(pet_id)
        assert len(timeline["documents"]) == 0
    else:
        raise AssertionError("Expected ValueError for unauthorized upload")


# --- audit event deterministic required fields ---

def test_audit_event_has_all_required_fields() -> None:
    event = emit_audit_event(
        event_name="uphr.document.uploaded",
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        resource_type="document",
        resource_id="doc-1",
        action_result="allowed",
        reason_code="document_uploaded",
        correlation_id="corr-audit-1",
    )
    assert isinstance(event, AuditEvent)
    required = [
        "audit_event_id", "event_name", "actor_id", "actor_role",
        "tenant_id", "resource_type", "resource_id",
        "action_result", "correlation_id", "occurred_at",
    ]
    for field in required:
        value = getattr(event, field)
        assert value is not None and value != "", f"Required field '{field}' is empty"


# --- timeline sort key within bucket ---

def test_timeline_vaccinations_sorted_most_recent_first(tmp_path: Path) -> None:
    service = build_uphr_service(tmp_path)
    pet = service.create_pet("tenant-1", "owner-1", "Max", "dog")
    service.create_vaccination_record(pet.pet_id, "Rabies", "2025-01-01T10:00:00Z")
    service.create_vaccination_record(pet.pet_id, "DHPP", "2026-03-28T10:00:00Z")
    service.create_vaccination_record(pet.pet_id, "Leptospira", "2024-06-15T10:00:00Z")

    timeline = service.get_timeline(pet.pet_id, category="vaccinations")
    vacc = timeline["vaccinations"]
    assert len(vacc) == 3
    # Most recent first: 2026 → 2025 → 2024
    dates = [v["administered_at"] for v in vacc]
    assert dates == sorted(dates, reverse=True)


def test_timeline_labs_sorted_most_recent_first(tmp_path: Path) -> None:
    service = build_uphr_service(tmp_path)
    pet = service.create_pet("tenant-1", "owner-1", "Luna", "cat")
    # Create labs at known fixed timestamps via direct cache injection
    import time
    service.create_lab_result(pet.pet_id, "Lab A", "CBC")
    time.sleep(0.01)
    service.create_lab_result(pet.pet_id, "Lab B", "T4")
    time.sleep(0.01)
    service.create_lab_result(pet.pet_id, "Lab C", "Urinalysis")

    timeline = service.get_timeline(pet.pet_id, category="labs")
    labs = timeline["labs"]
    assert len(labs) == 3
    recorded_ats = [lab["recorded_at"] for lab in labs]
    assert recorded_ats == sorted(recorded_ats, reverse=True)
