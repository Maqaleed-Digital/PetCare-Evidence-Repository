from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Set
from uuid import uuid4


CONSULTATION_AUDIT_EVENTS = [
    "consultation.session.requested",
    "consultation.session.started",
    "consultation.session.cancelled",
    "consultation.session.completed",
    "consultation.session.complete_denied",
    "consultation.session.escalation_requested",
    "consultation.session.viewed",
    "consultation.session.listed",
    "consultation.note.created",
    "consultation.note.updated",
    "consultation.note.update_denied",
    "consultation.note.signed",
    "consultation.note.viewed",
    "consultation.note.listed",
]

SESSION_REQUESTED = "REQUESTED"
SESSION_ACTIVE = "ACTIVE"
SESSION_COMPLETED = "COMPLETED"
SESSION_CANCELLED = "CANCELLED"

NOTE_DRAFT = "DRAFT"
NOTE_SIGNED = "SIGNED"

# Deterministic allowed state transitions — terminal states have empty sets.
ALLOWED_SESSION_TRANSITIONS: dict[str, Set[str]] = {
    SESSION_REQUESTED: {SESSION_ACTIVE, SESSION_CANCELLED},
    SESSION_ACTIVE: {SESSION_COMPLETED, SESSION_CANCELLED},
    SESSION_COMPLETED: set(),
    SESSION_CANCELLED: set(),
}


@dataclass
class ConsultationSession:
    session_id: str
    pet_id: str
    owner_id: str
    veterinarian_id: str
    tenant_id: str
    clinic_id: Optional[str]
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    cancelled_at: Optional[str]
    escalation_requested: bool = False


@dataclass
class ConsultationNote:
    note_id: str
    session_id: str
    pet_id: str
    veterinarian_id: str
    content: str
    status: str  # NOTE_DRAFT or NOTE_SIGNED
    created_at: str
    signed_at: Optional[str]
    signed_by_actor_id: Optional[str]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _assert_session_transition(session: ConsultationSession, target: str) -> None:
    allowed = ALLOWED_SESSION_TRANSITIONS.get(session.status, set())
    if target not in allowed:
        raise ValueError(f"invalid_transition:{session.status}:{target}")


def request_consultation(
    pet_id: str,
    owner_id: str,
    veterinarian_id: str,
    tenant_id: str,
    clinic_id: Optional[str],
) -> ConsultationSession:
    return ConsultationSession(
        session_id=str(uuid4()),
        pet_id=pet_id,
        owner_id=owner_id,
        veterinarian_id=veterinarian_id,
        tenant_id=tenant_id,
        clinic_id=clinic_id,
        status=SESSION_REQUESTED,
        created_at=utc_now_iso(),
        started_at=None,
        completed_at=None,
        cancelled_at=None,
        escalation_requested=False,
    )


def start_consultation(session: ConsultationSession) -> ConsultationSession:
    _assert_session_transition(session, SESSION_ACTIVE)
    session.status = SESSION_ACTIVE
    session.started_at = utc_now_iso()
    return session


def cancel_consultation(session: ConsultationSession) -> ConsultationSession:
    _assert_session_transition(session, SESSION_CANCELLED)
    session.status = SESSION_CANCELLED
    session.cancelled_at = utc_now_iso()
    return session


def complete_consultation(session: ConsultationSession) -> ConsultationSession:
    _assert_session_transition(session, SESSION_COMPLETED)
    session.status = SESSION_COMPLETED
    session.completed_at = utc_now_iso()
    return session


def create_draft_note(
    session_id: str,
    pet_id: str,
    veterinarian_id: str,
    content: str,
) -> ConsultationNote:
    return ConsultationNote(
        note_id=str(uuid4()),
        session_id=session_id,
        pet_id=pet_id,
        veterinarian_id=veterinarian_id,
        content=content,
        status=NOTE_DRAFT,
        created_at=utc_now_iso(),
        signed_at=None,
        signed_by_actor_id=None,
    )


def update_draft_note(note: ConsultationNote, new_content: str) -> ConsultationNote:
    """Update draft note content. Raises ValueError if note is already signed."""
    if note.status == NOTE_SIGNED:
        raise ValueError("signed_note_immutable")
    note.content = new_content
    return note


def sign_note(note: ConsultationNote, signing_actor_id: str) -> ConsultationNote:
    """Sign a draft note. Raises ValueError if already signed."""
    if note.status == NOTE_SIGNED:
        raise ValueError("note_already_signed")
    note.status = NOTE_SIGNED
    note.signed_at = utc_now_iso()
    note.signed_by_actor_id = signing_actor_id
    return note


def get_note_read_model(note: ConsultationNote) -> dict:
    """Return a deterministic read model dict for a ConsultationNote.
    Includes read_only flag: True for SIGNED notes, False for DRAFT.
    Keys returned in sorted order for determinism.
    """
    return dict(sorted({
        "note_id": note.note_id,
        "session_id": note.session_id,
        "pet_id": note.pet_id,
        "veterinarian_id": note.veterinarian_id,
        "content": note.content,
        "status": note.status,
        "read_only": note.status == NOTE_SIGNED,
        "created_at": note.created_at,
        "signed_at": note.signed_at,
        "signed_by_actor_id": note.signed_by_actor_id,
    }.items()))


def request_escalation(session: ConsultationSession) -> ConsultationSession:
    """Set escalation_requested flag. Boundary only — no Emergency domain logic.
    Requires session to be ACTIVE.
    """
    if session.status != SESSION_ACTIVE:
        raise ValueError("escalation_requires_active_session")
    session.escalation_requested = True
    return session
