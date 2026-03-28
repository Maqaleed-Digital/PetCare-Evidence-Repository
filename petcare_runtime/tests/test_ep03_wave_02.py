from pathlib import Path

import pytest

from petcare.api.routes_ep03 import (
    get_consultation_note_route,
    get_consultation_session_route,
    list_consultation_notes_route,
    list_consultation_sessions,
    sign_consultation_note,
    update_consultation_note,
)
from petcare.audit.audit_service import (
    emit_audit_event,
    serialize_audit_event,
    validate_audit_event,
)
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_CONSULTATION,
    PURPOSE_OWNER_SELF_SERVICE,
    ROLE_OWNER,
    ROLE_VETERINARIAN,
)
from petcare.consultation.consultation_repository import ConsultationRepository
from petcare.consultation.consultation_service import (
    CONSULTATION_AUDIT_EVENTS,
    NOTE_DRAFT,
    NOTE_SIGNED,
    SESSION_ACTIVE,
    SESSION_CANCELLED,
    SESSION_COMPLETED,
    SESSION_REQUESTED,
    cancel_consultation,
    complete_consultation,
    create_draft_note,
    get_note_read_model,
    request_consultation,
    request_escalation,
    sign_note,
    start_consultation,
)


def build_consultation_repo(tmp_path: Path) -> ConsultationRepository:
    return ConsultationRepository(str(tmp_path / "consultation_store.json"))


def make_owner_access(owner_id: str = "owner-1", tenant_id: str = "tenant-1") -> AccessContext:
    return AccessContext(
        actor_id=owner_id,
        actor_role=ROLE_OWNER,
        tenant_id=tenant_id,
        clinic_id=None,
        purpose_of_use=PURPOSE_OWNER_SELF_SERVICE,
        consent_scopes=set(),
        owner_id=owner_id,
    )


def make_vet_access(vet_id: str = "vet-1", tenant_id: str = "tenant-1") -> AccessContext:
    return AccessContext(
        actor_id=vet_id,
        actor_role=ROLE_VETERINARIAN,
        tenant_id=tenant_id,
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes=set(),
    )


def make_pet_resource(pet_id: str = "pet-1", owner_id: str = "owner-1", tenant_id: str = "tenant-1") -> ResourceContext:
    return ResourceContext(
        resource_type="pet",
        resource_id=pet_id,
        tenant_id=tenant_id,
        clinic_id="clinic-1",
        owner_id=owner_id,
    )


# --- consultation audit contract ---

def test_consultation_audit_events_constant_is_complete() -> None:
    assert isinstance(CONSULTATION_AUDIT_EVENTS, list)
    assert len(CONSULTATION_AUDIT_EVENTS) >= 8
    required = [
        "consultation.session.requested",
        "consultation.session.started",
        "consultation.session.cancelled",
        "consultation.session.completed",
        "consultation.note.created",
        "consultation.note.signed",
        "consultation.session.viewed",
        "consultation.note.viewed",
    ]
    for event_name in required:
        assert event_name in CONSULTATION_AUDIT_EVENTS, f"Missing: {event_name}"


def test_ep03_audit_event_passes_required_fields_validation() -> None:
    event = emit_audit_event(
        event_name="consultation.session.requested",
        actor_id="owner-1",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        resource_type="pet",
        resource_id="pet-1",
        action_result="allowed",
        reason_code="owner_request_consultation",
        correlation_id="corr-audit-ep03",
    )
    missing = validate_audit_event(event)
    assert missing == [], f"Unexpected missing fields: {missing}"


def test_ep03_audit_serialization_keys_sorted() -> None:
    event = emit_audit_event(
        event_name="consultation.note.signed",
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        resource_type="pet",
        resource_id="pet-1",
        action_result="allowed",
        reason_code="vet_manage_consultation",
        correlation_id="corr-serial-ep03",
    )
    serialized = serialize_audit_event(event)
    keys = list(serialized.keys())
    assert keys == sorted(keys), "EP-03 audit event keys must be sorted"


# --- retrieval and listing ---

def test_list_sessions_for_pet_returns_sessions_for_correct_pet(tmp_path: Path) -> None:
    repo = build_consultation_repo(tmp_path)
    s1 = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    s2 = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    s3 = request_consultation("pet-2", "owner-1", "vet-1", "tenant-1", None)
    repo.add_session(s1)
    repo.add_session(s2)
    repo.add_session(s3)

    result = repo.list_sessions_for_pet("pet-1")
    assert len(result) == 2
    ids = {s.session_id for s in result}
    assert s1.session_id in ids
    assert s2.session_id in ids
    assert s3.session_id not in ids


def test_get_consultation_session_route_allowed_for_vet(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    routes_ep03.consultation_repository.add_session(session)

    result = get_consultation_session_route(
        make_vet_access(), make_pet_resource(), session.session_id, "corr-view-session"
    )
    assert result["allowed"] is True
    assert result["session"].session_id == session.session_id
    assert result["audit_event"].event_name == "consultation.session.viewed"


def test_get_consultation_session_route_denied_wrong_tenant(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    routes_ep03.consultation_repository.add_session(session)

    wrong_tenant_access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-OTHER",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes=set(),
    )
    result = get_consultation_session_route(
        wrong_tenant_access, make_pet_resource(), session.session_id, "corr-denied-tenant"
    )
    assert result["allowed"] is False
    assert result["reason_code"] == "tenant_mismatch"


def test_list_consultation_sessions_allowed_for_owner(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    s1 = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    s2 = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    routes_ep03.consultation_repository.add_session(s1)
    routes_ep03.consultation_repository.add_session(s2)

    result = list_consultation_sessions(
        make_owner_access(), make_pet_resource(), "corr-list-sessions"
    )
    assert result["allowed"] is True
    assert len(result["sessions"]) == 2


def test_list_consultation_notes_route_returns_read_models(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    note = create_draft_note(session.session_id, "pet-1", "vet-1", "Observations.")
    routes_ep03.consultation_repository.add_session(session)
    routes_ep03.consultation_repository.add_note(note)

    result = list_consultation_notes_route(
        make_vet_access(), make_pet_resource(), session.session_id, "corr-list-notes"
    )
    assert result["allowed"] is True
    assert len(result["notes"]) == 1
    assert result["notes"][0]["read_only"] is False
    assert result["notes"][0]["status"] == NOTE_DRAFT


# --- signed read model ---

def test_signed_note_read_model_has_read_only_true() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Final findings.")
    sign_note(note, "vet-1")
    model = get_note_read_model(note)
    assert model["read_only"] is True
    assert model["status"] == NOTE_SIGNED
    assert model["signed_by_actor_id"] == "vet-1"
    assert model["signed_at"] is not None


def test_draft_note_read_model_has_read_only_false() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Initial findings.")
    model = get_note_read_model(note)
    assert model["read_only"] is False
    assert model["status"] == NOTE_DRAFT


def test_signed_note_read_model_keys_are_sorted() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Final findings.")
    sign_note(note, "vet-1")
    model = get_note_read_model(note)
    keys = list(model.keys())
    assert keys == sorted(keys)


# --- negative state transitions ---

def test_invalid_transition_cancelled_to_active_raises() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    cancel_consultation(session)
    with pytest.raises(ValueError, match="CANCELLED"):
        start_consultation(session)


def test_invalid_transition_completed_to_cancelled_raises() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    complete_consultation(session)
    with pytest.raises(ValueError, match="COMPLETED"):
        cancel_consultation(session)


def test_update_note_via_route_denied_when_signed(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    note = create_draft_note(session.session_id, "pet-1", "vet-1", "Final note.")
    sign_note(note, "vet-1")
    routes_ep03.consultation_repository.add_session(session)
    routes_ep03.consultation_repository.add_note(note)

    result = update_consultation_note(
        make_vet_access(), make_pet_resource(), note, "Attempt to mutate.", "corr-immutable-route"
    )
    assert result["allowed"] is False
    assert result["reason_code"] == "signed_note_immutable"
    # Note content must remain unchanged.
    assert note.content == "Final note."


# --- escalation boundary ---

def test_request_escalation_does_not_change_session_status() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    request_escalation(session)
    assert session.status == SESSION_ACTIVE  # unchanged
    assert session.escalation_requested is True
