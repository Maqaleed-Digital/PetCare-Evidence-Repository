from pathlib import Path

import pytest

from petcare.api.routes_ep03 import (
    cancel_consultation_session,
    complete_consultation_session,
    create_consultation_note,
    request_consultation_escalation,
    request_consultation_session,
    sign_consultation_note,
    start_consultation_session,
    update_consultation_note,
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
    SESSION_ACTIVE,
    SESSION_CANCELLED,
    SESSION_COMPLETED,
    SESSION_REQUESTED,
    NOTE_DRAFT,
    NOTE_SIGNED,
    ALLOWED_SESSION_TRANSITIONS,
    cancel_consultation,
    complete_consultation,
    create_draft_note,
    request_consultation,
    request_escalation,
    sign_note,
    start_consultation,
    update_draft_note,
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


# --- state machine ---

def test_allowed_session_transitions_are_deterministic() -> None:
    assert ALLOWED_SESSION_TRANSITIONS[SESSION_REQUESTED] == {SESSION_ACTIVE, SESSION_CANCELLED}
    assert ALLOWED_SESSION_TRANSITIONS[SESSION_ACTIVE] == {SESSION_COMPLETED, SESSION_CANCELLED}
    assert ALLOWED_SESSION_TRANSITIONS[SESSION_COMPLETED] == set()
    assert ALLOWED_SESSION_TRANSITIONS[SESSION_CANCELLED] == set()


def test_request_consultation_creates_requested_state() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    assert session.status == SESSION_REQUESTED
    assert session.pet_id == "pet-1"
    assert session.owner_id == "owner-1"
    assert session.veterinarian_id == "vet-1"
    assert session.started_at is None
    assert session.escalation_requested is False


def test_start_consultation_transitions_to_active() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    started = start_consultation(session)
    assert started.status == SESSION_ACTIVE
    assert started.started_at is not None


def test_cancel_consultation_from_requested() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    cancelled = cancel_consultation(session)
    assert cancelled.status == SESSION_CANCELLED
    assert cancelled.cancelled_at is not None


def test_cancel_consultation_from_active() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    cancelled = cancel_consultation(session)
    assert cancelled.status == SESSION_CANCELLED


def test_invalid_transition_completed_to_active_raises() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    note = create_draft_note(session.session_id, "pet-1", "vet-1", "findings")
    sign_note(note, "vet-1")
    complete_consultation(session)
    with pytest.raises(ValueError, match="COMPLETED"):
        start_consultation(session)


# --- note draft / signed boundary ---

def test_create_draft_note_is_in_draft_state() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Initial findings.")
    assert note.status == NOTE_DRAFT
    assert note.signed_at is None
    assert note.signed_by_actor_id is None


def test_update_draft_note_mutates_content() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Initial.")
    updated = update_draft_note(note, "Revised findings.")
    assert updated.content == "Revised findings."
    assert updated.status == NOTE_DRAFT


def test_signed_note_mutation_raises() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Final.")
    sign_note(note, "vet-1")
    with pytest.raises(ValueError, match="signed_note_immutable"):
        update_draft_note(note, "Attempt to mutate.")


def test_sign_note_transitions_to_signed() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Diagnosis: healthy.")
    signed = sign_note(note, "vet-1")
    assert signed.status == NOTE_SIGNED
    assert signed.signed_by_actor_id == "vet-1"
    assert signed.signed_at is not None


def test_sign_note_twice_raises() -> None:
    note = create_draft_note("session-1", "pet-1", "vet-1", "Final.")
    sign_note(note, "vet-1")
    with pytest.raises(ValueError, match="note_already_signed"):
        sign_note(note, "vet-1")


# --- vet sign-off hard gate (route-level) ---

def test_sign_consultation_note_denied_for_non_vet(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    note = create_draft_note(session.session_id, "pet-1", "vet-1", "Observations.")
    routes_ep03.consultation_repository.add_session(session)
    routes_ep03.consultation_repository.add_note(note)

    owner_access = make_owner_access()
    resource = make_pet_resource()
    result = sign_consultation_note(owner_access, resource, note, "corr-sign-denied")
    assert result["allowed"] is False
    assert result["reason_code"] == "consultation_manage_denied"
    # Note must remain unsigned.
    assert note.status == NOTE_DRAFT


def test_sign_consultation_note_allowed_for_vet(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    note = create_draft_note(session.session_id, "pet-1", "vet-1", "Full assessment.")
    routes_ep03.consultation_repository.add_session(session)
    routes_ep03.consultation_repository.add_note(note)

    vet_access = make_vet_access()
    resource = make_pet_resource()
    result = sign_consultation_note(vet_access, resource, note, "corr-sign-ok")
    assert result["allowed"] is True
    assert result["note"].status == NOTE_SIGNED
    assert result["audit_event"].event_name == "consultation.note.signed"


# --- complete requires signed note ---

def test_complete_consultation_denied_without_signed_note(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    routes_ep03.consultation_repository.add_session(session)
    # No notes added.

    vet_access = make_vet_access()
    resource = make_pet_resource()
    result = complete_consultation_session(vet_access, resource, session, "corr-complete-denied")
    assert result["allowed"] is False
    assert result["reason_code"] == "no_signed_note"


def test_complete_consultation_allowed_after_signed_note(tmp_path: Path) -> None:
    from petcare.api import routes_ep03
    routes_ep03.consultation_repository = build_consultation_repo(tmp_path)

    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    note = create_draft_note(session.session_id, "pet-1", "vet-1", "Final assessment.")
    sign_note(note, "vet-1")
    routes_ep03.consultation_repository.add_session(session)
    routes_ep03.consultation_repository.add_note(note)

    vet_access = make_vet_access()
    resource = make_pet_resource()
    result = complete_consultation_session(vet_access, resource, session, "corr-complete-ok")
    assert result["allowed"] is True
    assert result["session"].status == SESSION_COMPLETED


# --- escalation boundary ---

def test_request_escalation_sets_flag_on_active_session() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    start_consultation(session)
    escalated = request_escalation(session)
    assert escalated.escalation_requested is True
    assert escalated.status == SESSION_ACTIVE  # status unchanged


def test_request_escalation_raises_when_not_active() -> None:
    session = request_consultation("pet-1", "owner-1", "vet-1", "tenant-1", None)
    # REQUESTED state — not ACTIVE
    with pytest.raises(ValueError, match="escalation_requires_active_session"):
        request_escalation(session)
