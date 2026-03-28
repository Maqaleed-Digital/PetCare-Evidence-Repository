from __future__ import annotations

from petcare.audit.audit_service import emit_audit_event
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    authorize_manage_consultation,
    authorize_request_consultation,
    authorize_view_consultation,
    ROLE_VETERINARIAN,
)
from petcare.consultation.consultation_repository import ConsultationRepository
from petcare.consultation.consultation_service import (
    ConsultationNote,
    ConsultationSession,
    NOTE_SIGNED,
    cancel_consultation,
    complete_consultation,
    create_draft_note,
    get_note_read_model,
    request_consultation,
    request_escalation,
    sign_note,
    start_consultation,
    update_draft_note,
)


consultation_repository = ConsultationRepository("petcare_runtime/data/consultation_store.json")


def request_consultation_session(
    access: AccessContext,
    resource: ResourceContext,
    veterinarian_id: str,
    correlation_id: str,
) -> dict:
    decision = authorize_request_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    session = request_consultation(
        pet_id=resource.resource_id,
        owner_id=resource.owner_id or "",
        veterinarian_id=veterinarian_id,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
    )
    consultation_repository.add_session(session)
    audit = emit_audit_event(
        event_name="consultation.session.requested",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="owner_request_consultation",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "session": session, "audit_event": audit}


def start_consultation_session(
    access: AccessContext,
    resource: ResourceContext,
    session: ConsultationSession,
    correlation_id: str,
) -> dict:
    decision = authorize_manage_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    started = start_consultation(session)
    consultation_repository.update_session(started)
    audit = emit_audit_event(
        event_name="consultation.session.started",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="vet_manage_consultation",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "session": started, "audit_event": audit}


def cancel_consultation_session(
    access: AccessContext,
    resource: ResourceContext,
    session: ConsultationSession,
    correlation_id: str,
) -> dict:
    # Both owner and vet may cancel; owner uses authorize_request_consultation,
    # vet uses authorize_manage_consultation.
    if access.actor_role == ROLE_VETERINARIAN:
        decision = authorize_manage_consultation(access, resource)
    else:
        decision = authorize_request_consultation(access, resource)

    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    cancelled = cancel_consultation(session)
    consultation_repository.update_session(cancelled)
    audit = emit_audit_event(
        event_name="consultation.session.cancelled",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    return {"allowed": True, "session": cancelled, "audit_event": audit}


def complete_consultation_session(
    access: AccessContext,
    resource: ResourceContext,
    session: ConsultationSession,
    correlation_id: str,
) -> dict:
    decision = authorize_manage_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    # Require at least one signed note before completing.
    notes = consultation_repository.list_notes_for_session(session.session_id)
    signed_notes = [n for n in notes if n.status == NOTE_SIGNED]
    if not signed_notes:
        audit = emit_audit_event(
            event_name="consultation.session.complete_denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code="no_signed_note",
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": "no_signed_note", "audit_event": audit}

    completed = complete_consultation(session)
    consultation_repository.update_session(completed)
    audit = emit_audit_event(
        event_name="consultation.session.completed",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="vet_manage_consultation",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "session": completed, "audit_event": audit}


def create_consultation_note(
    access: AccessContext,
    resource: ResourceContext,
    session_id: str,
    content: str,
    correlation_id: str,
) -> dict:
    decision = authorize_manage_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    note = create_draft_note(
        session_id=session_id,
        pet_id=resource.resource_id,
        veterinarian_id=access.actor_id,
        content=content,
    )
    consultation_repository.add_note(note)
    audit = emit_audit_event(
        event_name="consultation.note.created",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="vet_manage_consultation",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "note": note, "audit_event": audit}


def update_consultation_note(
    access: AccessContext,
    resource: ResourceContext,
    note: ConsultationNote,
    new_content: str,
    correlation_id: str,
) -> dict:
    decision = authorize_manage_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    if note.status == NOTE_SIGNED:
        audit = emit_audit_event(
            event_name="consultation.note.update_denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code="signed_note_immutable",
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": "signed_note_immutable", "audit_event": audit}

    updated = update_draft_note(note, new_content)
    consultation_repository.update_note(updated)
    audit = emit_audit_event(
        event_name="consultation.note.updated",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="vet_manage_consultation",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "note": updated, "audit_event": audit}


def sign_consultation_note(
    access: AccessContext,
    resource: ResourceContext,
    note: ConsultationNote,
    correlation_id: str,
) -> dict:
    """Hard gate: only ROLE_VETERINARIAN may sign a consultation note."""
    decision = authorize_manage_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    signed = sign_note(note, signing_actor_id=access.actor_id)
    consultation_repository.update_note(signed)
    audit = emit_audit_event(
        event_name="consultation.note.signed",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="vet_manage_consultation",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "note": signed, "audit_event": audit}


def request_consultation_escalation(
    access: AccessContext,
    resource: ResourceContext,
    session: ConsultationSession,
    correlation_id: str,
) -> dict:
    """Boundary only: sets escalation_requested flag on session.
    No Emergency domain logic is executed.
    """
    decision = authorize_manage_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    escalated = request_escalation(session)
    consultation_repository.update_session(escalated)
    audit = emit_audit_event(
        event_name="consultation.session.escalation_requested",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="vet_manage_consultation",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "session": escalated, "audit_event": audit}


# --- retrieval and listing (Wave 02) ---

def get_consultation_session_route(
    access: AccessContext,
    resource: ResourceContext,
    session_id: str,
    correlation_id: str,
) -> dict:
    decision = authorize_view_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    session = consultation_repository.get_session(session_id)
    audit = emit_audit_event(
        event_name="consultation.session.viewed",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    return {"allowed": True, "session": session, "audit_event": audit}


def list_consultation_sessions(
    access: AccessContext,
    resource: ResourceContext,
    correlation_id: str,
) -> dict:
    decision = authorize_view_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    sessions = consultation_repository.list_sessions_for_pet(resource.resource_id)
    audit = emit_audit_event(
        event_name="consultation.session.listed",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    return {"allowed": True, "sessions": sessions, "audit_event": audit}


def get_consultation_note_route(
    access: AccessContext,
    resource: ResourceContext,
    session_id: str,
    note_id: str,
    correlation_id: str,
) -> dict:
    decision = authorize_view_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    notes = consultation_repository.list_notes_for_session(session_id)
    note = next((n for n in notes if n.note_id == note_id), None)
    audit = emit_audit_event(
        event_name="consultation.note.viewed",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    read_model = get_note_read_model(note) if note is not None else None
    return {"allowed": True, "note": read_model, "audit_event": audit}


def list_consultation_notes_route(
    access: AccessContext,
    resource: ResourceContext,
    session_id: str,
    correlation_id: str,
) -> dict:
    decision = authorize_view_consultation(access, resource)
    if not decision.allowed:
        audit = emit_audit_event(
            event_name="access.denied",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="denied",
            reason_code=decision.reason_code,
            correlation_id=correlation_id,
        )
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    notes = consultation_repository.list_notes_for_session(session_id)
    read_models = [get_note_read_model(n) for n in notes]
    audit = emit_audit_event(
        event_name="consultation.note.listed",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    return {"allowed": True, "notes": read_models, "audit_event": audit}
