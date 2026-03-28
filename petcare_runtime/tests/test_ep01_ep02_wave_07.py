from pathlib import Path

from petcare.api.routes_ep01_ep02 import (
    create_consent,
    get_document,
    revoke_consent,
)
from petcare.audit.audit_service import (
    AuditEvent,
    REQUIRED_AUDIT_FIELDS,
    emit_audit_event,
    serialize_audit_event,
    validate_audit_event,
)
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_CONSULTATION,
    ROLE_OWNER,
    ROLE_VETERINARIAN,
    SCOPE_CARE_DELIVERY,
    SCOPE_DOCUMENT_SHARING,
)
from petcare.consent.consent_repository import ConsentRepository
from petcare.consent.consent_service import (
    STATUS_ACTIVE,
    STATUS_REVOKED,
    create_consent_record,
    revoke_consent_record,
)


def build_consent_repo(tmp_path: Path) -> ConsentRepository:
    return ConsentRepository(str(tmp_path / "consent_store.json"))


# --- audit serialization determinism ---

def test_validate_audit_event_no_errors_on_complete_event() -> None:
    event = emit_audit_event(
        event_name="uphr.document.viewed",
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        resource_type="document",
        resource_id="doc-1",
        action_result="allowed",
        reason_code="vet_document_shared",
        correlation_id="corr-validate-1",
    )
    missing = validate_audit_event(event)
    assert missing == [], f"Unexpected missing fields: {missing}"


def test_validate_audit_event_returns_missing_fields() -> None:
    event = AuditEvent(
        audit_event_id="",          # intentionally empty
        event_name="",              # intentionally empty
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id=None,
        resource_type="document",
        resource_id="doc-1",
        action_result="allowed",
        reason_code=None,
        correlation_id="corr-1",
        occurred_at="2026-03-28T00:00:00+00:00",
    )
    missing = validate_audit_event(event)
    assert "audit_event_id" in missing
    assert "event_name" in missing
    # Fields that are present and non-empty should not appear.
    assert "actor_id" not in missing
    assert "tenant_id" not in missing


def test_serialize_audit_event_keys_are_sorted() -> None:
    event = emit_audit_event(
        event_name="consent.created",
        actor_id="owner-1",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        resource_type="pet",
        resource_id="pet-1",
        action_result="allowed",
        reason_code="owner_manage_consent",
        correlation_id="corr-serial-1",
    )
    serialized = serialize_audit_event(event)
    keys = list(serialized.keys())
    assert keys == sorted(keys), "serialize_audit_event keys must be in sorted order"


def test_serialize_audit_event_is_deterministic_across_calls() -> None:
    event = emit_audit_event(
        event_name="consent.revoked",
        actor_id="owner-2",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        resource_type="pet",
        resource_id="pet-2",
        action_result="allowed",
        reason_code="owner_manage_consent",
        correlation_id="corr-serial-2",
    )
    first = serialize_audit_event(event)
    second = serialize_audit_event(event)
    assert list(first.keys()) == list(second.keys())
    assert first == second


def test_required_audit_fields_constant_is_non_empty() -> None:
    assert isinstance(REQUIRED_AUDIT_FIELDS, list)
    assert len(REQUIRED_AUDIT_FIELDS) >= 8
    for f in ["audit_event_id", "event_name", "actor_id", "actor_role", "occurred_at"]:
        assert f in REQUIRED_AUDIT_FIELDS


# --- consent history (all statuses) ---

def test_list_history_for_pet_includes_revoked_entries(tmp_path: Path) -> None:
    repo = build_consent_repo(tmp_path)
    record = create_consent_record(
        pet_id="pet-hist-1",
        owner_id="owner-1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role=ROLE_VETERINARIAN,
        captured_by_actor_id="owner-1",
        audit_reference_id="ref-hist-1",
    )
    repo.add_record(record)
    revoked = revoke_consent_record(record)
    repo.update_record(revoked)

    history = repo.list_history_for_pet("pet-hist-1")
    assert len(history) == 1
    assert history[0].status == STATUS_REVOKED


def test_list_history_for_pet_includes_active_and_revoked(tmp_path: Path) -> None:
    repo = build_consent_repo(tmp_path)
    r1 = create_consent_record(
        pet_id="pet-hist-2",
        owner_id="owner-1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role=ROLE_VETERINARIAN,
        captured_by_actor_id="owner-1",
        audit_reference_id="ref-hist-2a",
    )
    repo.add_record(r1)
    revoked = revoke_consent_record(r1)
    repo.update_record(revoked)

    r2 = create_consent_record(
        pet_id="pet-hist-2",
        owner_id="owner-1",
        consent_scope="SCOPE_DOCUMENT_SHARING",
        purpose_of_use=PURPOSE_CONSULTATION,
        granted_to_role=ROLE_VETERINARIAN,
        captured_by_actor_id="owner-1",
        audit_reference_id="ref-hist-2b",
    )
    repo.add_record(r2)

    history = repo.list_history_for_pet("pet-hist-2")
    assert len(history) == 2
    statuses = {h.status for h in history}
    assert STATUS_REVOKED in statuses
    assert STATUS_ACTIVE in statuses


# --- get_document vet consent auto-population ---

def test_get_document_vet_allowed_when_active_consent_exists(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.consent_repository = build_consent_repo(tmp_path)

    # Grant consent as owner
    owner_access = AccessContext(
        actor_id="owner-1",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        purpose_of_use="purpose_owner_self_service",
        consent_scopes=set(),
        owner_id="owner-1",
    )
    owner_resource = ResourceContext(
        resource_type="pet",
        resource_id="pet-doc-1",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    create_consent(owner_access, owner_resource, "SCOPE_DOCUMENT_SHARING", PURPOSE_CONSULTATION, "corr-grant-doc")

    # Vet requests document — consent fields auto-populated from store
    vet_access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes={SCOPE_DOCUMENT_SHARING},
    )
    vet_resource = ResourceContext(
        resource_type="document",
        resource_id="pet-doc-1",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
        document_shared=True,
        # consent fields intentionally NOT pre-populated — route must auto-fill
    )
    result = get_document(vet_access, vet_resource, "corr-view-doc")
    assert result["allowed"] is True
    assert result["reason_code"] == "vet_document_shared"


def test_get_document_vet_denied_when_consent_revoked(tmp_path: Path) -> None:
    from petcare.api import routes_ep01_ep02
    routes_ep01_ep02.consent_repository = build_consent_repo(tmp_path)

    owner_access = AccessContext(
        actor_id="owner-1",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        purpose_of_use="purpose_owner_self_service",
        consent_scopes=set(),
        owner_id="owner-1",
    )
    owner_resource = ResourceContext(
        resource_type="pet",
        resource_id="pet-doc-2",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    grant_result = create_consent(owner_access, owner_resource, "SCOPE_DOCUMENT_SHARING", PURPOSE_CONSULTATION, "corr-grant-doc2")
    revoke_consent(owner_access, owner_resource, grant_result["consent_record"], "corr-revoke-doc2")

    vet_access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes={SCOPE_DOCUMENT_SHARING},
    )
    vet_resource = ResourceContext(
        resource_type="document",
        resource_id="pet-doc-2",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
        document_shared=True,
    )
    result = get_document(vet_access, vet_resource, "corr-view-doc2")
    assert result["allowed"] is False
    assert result["reason_code"] == "document_missing_active_consent"
