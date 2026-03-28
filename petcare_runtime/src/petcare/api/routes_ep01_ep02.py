from __future__ import annotations

from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    authorize_manage_consent,
    authorize_view_document,
    authorize_view_pet_profile,
    authorize_view_timeline,
)
from petcare.audit.audit_service import emit_audit_event
from petcare.consent.consent_service import create_consent_record, revoke_consent_record
from petcare.uphr.service import UPHRService


uphr_service = UPHRService()


def create_pet_profile(tenant_id: str, owner_id: str, name: str, species: str) -> dict:
    pet = uphr_service.create_pet(tenant_id=tenant_id, owner_id=owner_id, name=name, species=species)
    return {"pet_id": pet.pet_id, "status": "created"}


def get_pet_profile(access: AccessContext, resource: ResourceContext, correlation_id: str) -> dict:
    decision = authorize_view_pet_profile(access, resource)
    audit = emit_audit_event(
        event_name="pet.profile.viewed" if decision.allowed else "access.denied",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed" if decision.allowed else "denied",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    return {"allowed": decision.allowed, "reason_code": decision.reason_code, "audit_event": audit}


def get_document(access: AccessContext, resource: ResourceContext, correlation_id: str) -> dict:
    decision = authorize_view_document(access, resource)
    audit = emit_audit_event(
        event_name="uphr.document.viewed" if decision.allowed else "uphr.document.access_denied",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed" if decision.allowed else "denied",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    return {"allowed": decision.allowed, "reason_code": decision.reason_code, "audit_event": audit}


def get_timeline(
    access: AccessContext,
    resource: ResourceContext,
    correlation_id: str,
    category: str | None = None,
    search_term: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    decision = authorize_view_timeline(access, resource)
    audit = emit_audit_event(
        event_name="uphr.timeline.viewed" if decision.allowed else "access.denied",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed" if decision.allowed else "denied",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    if not decision.allowed:
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    timeline = uphr_service.get_timeline(
        resource.resource_id,
        category=category,
        search_term=search_term,
        page=page,
        page_size=page_size,
    )
    return {"allowed": True, "timeline": timeline, "audit_event": audit}


def get_prompt_safe_timeline_summary(access: AccessContext, resource: ResourceContext, correlation_id: str) -> dict:
    decision = authorize_view_timeline(access, resource)
    audit = emit_audit_event(
        event_name="uphr.ai_redaction.applied" if decision.allowed else "access.denied",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed" if decision.allowed else "denied",
        reason_code=decision.reason_code,
        correlation_id=correlation_id,
    )
    if not decision.allowed:
        return {"allowed": False, "reason_code": decision.reason_code, "audit_event": audit}

    summary = uphr_service.build_prompt_safe_timeline_summary(resource.resource_id)
    return {"allowed": True, "summary": summary, "audit_event": audit}


def upload_document(
    access: AccessContext,
    resource: ResourceContext,
    correlation_id: str,
    document_type: str,
    object_storage_key: str,
    mime_type: str,
    size_bytes: int,
    visibility_scope: str,
    checksum_sha256: str,
) -> dict:
    decision = authorize_view_pet_profile(access, resource)
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

    try:
        doc = uphr_service.create_document(
            pet_id=resource.resource_id,
            document_type=document_type,
            object_storage_key=object_storage_key,
            mime_type=mime_type,
            size_bytes=size_bytes,
            uploaded_by_actor_id=access.actor_id,
            visibility_scope=visibility_scope,
            checksum_sha256=checksum_sha256,
        )
    except ValueError as exc:
        audit = emit_audit_event(
            event_name="uphr.document.upload_rejected",
            actor_id=access.actor_id,
            actor_role=access.actor_role,
            tenant_id=access.tenant_id,
            clinic_id=access.clinic_id,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_result="rejected",
            reason_code=str(exc),
            correlation_id=correlation_id,
        )
        return {"allowed": True, "uploaded": False, "reason_code": str(exc), "audit_event": audit}

    audit = emit_audit_event(
        event_name="uphr.document.uploaded",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="document_uploaded",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "uploaded": True, "document_id": doc.uphr_document_id, "audit_event": audit}


def create_consent(
    access: AccessContext,
    resource: ResourceContext,
    consent_scope: str,
    purpose_of_use: str,
    correlation_id: str,
) -> dict:
    decision = authorize_manage_consent(access, resource)
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

    record = create_consent_record(
        pet_id=resource.resource_id,
        owner_id=resource.owner_id or "",
        consent_scope=consent_scope,
        purpose_of_use=purpose_of_use,
        granted_to_role="Veterinarian",
        captured_by_actor_id=access.actor_id,
        audit_reference_id=correlation_id,
    )
    audit = emit_audit_event(
        event_name="consent.created",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="owner_manage_consent",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "consent_record": record, "audit_event": audit}


def revoke_consent(
    access: AccessContext,
    resource: ResourceContext,
    consent_record,
    correlation_id: str,
) -> dict:
    decision = authorize_manage_consent(access, resource)
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

    revoked = revoke_consent_record(consent_record)
    audit = emit_audit_event(
        event_name="consent.revoked",
        actor_id=access.actor_id,
        actor_role=access.actor_role,
        tenant_id=access.tenant_id,
        clinic_id=access.clinic_id,
        resource_type=resource.resource_type,
        resource_id=resource.resource_id,
        action_result="allowed",
        reason_code="owner_manage_consent",
        correlation_id=correlation_id,
    )
    return {"allowed": True, "consent_record": revoked, "audit_event": audit}
