"""
PetCare Platform API
Governed, fail-closed, audit-traced.
No autonomous execution. No unauthenticated writes.
"""
from __future__ import annotations

import dataclasses
import json
import logging
import os
from datetime import date, datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import (Depends, FastAPI, File, Header, HTTPException, Request,
                     Response, UploadFile)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Domain imports — all existing petcare_runtime modules
# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "petcare_runtime", "src"))
# W0-G: the governed audit-chain algorithm lives in the foundations tree, not in
# petcare_runtime. It is REUSED here, never reimplemented (CP-2 W0-G DISPOSITION).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from petcare.audit.audit_service import AuditEvent, emit_audit_event
# Authority tokens come from the serving layer's own canonical module
# (PRE2_RULING=2-C). They are NOT imported from petcare.auth.access_control any
# more: that package's ROLE_* values are its own domain vocabulary, and the
# domain authorizer they belong to is never called from here — `AccessContext`,
# `ResourceContext`, `authorize_view_pet_profile` and `authorize_view_timeline`
# were imported and never used. Comparing a session role against another
# package's tokens is what made every identity this system creates unauthorised
# (CONF-01).
from roles import (  # noqa: E402 — sys.path is set above
    ROLE_OWNER,
    ROLE_VETERINARIAN,
    ROLE_PLATFORM_ADMIN,
    ROLE_PARTNER_CLINIC_ADMIN,
    ALLOWED_ROLES,
)
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    authorize_view_pet_profile,
    authorize_view_timeline,
    PURPOSE_CONSULTATION,
    PURPOSE_OWNER_SELF_SERVICE,
    SCOPE_PROFILE,
    SCOPE_CARE_DELIVERY,
)
from petcare.consent.consent_repository import ConsentRepository
from petcare.consent.consent_service import (
    create_consent_record,
    revoke_consent_record,
)
from petcare.consultation.consultation_service import (
    ConsultationSession,
    ConsultationNote,
    SESSION_REQUESTED,
    SESSION_ACTIVE,
    SESSION_COMPLETED,
    NOTE_DRAFT,
    NOTE_SIGNED,
    ALLOWED_SESSION_TRANSITIONS,
    utc_now_iso,
)
from petcare.uphr.service import UPHRService

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("petcare.api")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]
if not ALLOWED_ORIGINS:
    ALLOWED_ORIGINS = [
        "https://myveticare.com",
        "https://www.myveticare.com",
        "http://localhost:3000",
        "http://localhost:3001",
    ]

app = FastAPI(
    title="PetCare Platform API",
    version="1.0.0",
    description="Governed veterinary platform API. Fail-closed. Audit-traced.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

# ---------------------------------------------------------------------------
# Auth router
# ---------------------------------------------------------------------------
from routers.auth import (router as auth_router, seed_user, seed_invite_code,
                          read_session, require_tenant, PERSISTENCE)
from audit_repository import AUDIT_CHAIN_GENESIS, AuditWriteFailed
# FR-14 · Option A. The prescription store, its governed transitions and the
# object side of its attachments. No SQL crosses into this module: these are the
# same repository protocols identity and audit already reach.
from prescriptions import (
    Prescription,
    PrescriptionDocument,
    PrescriptionNotFound,
    STATUS_DISPENSED,
    STATUS_ISSUED,
    STATUS_VET_VERIFIED,
    TransitionDenied,
)
from prescription_documents import (
    DocumentRejected,
    ObjectStoreUnavailable,
    SERVED_CONTENT_TYPE,
    build_document_store,
    new_storage_key,
    sha256_hex,
    validate_upload,
)
from repositories import RepositoryDenied
from pets import PetIdentification, PetMedicalRecord, PetProfile as Pet  # FR-02 (U2)
from preferences import DEFAULT_LANGUAGE  # FR-09 (U3)
from messages import (CHANNEL_IN_APP, DELIVERED, ConsultationMessage,  # FR-07 (U7)
                      DeliveryRecord, MessageAttachment)
from inventory import (ADJUSTMENT, RECEIPT, REASONS, SUPPLY, TRANSFER_IN, TRANSFER_OUT,  # FR-13 (U8)
                       VETERINARIAN_ONLY, InventoryLocation, StockMovement, prescription_required)
import sfda  # FR-14 AC-06 (U9): the SFDA prescription-validation port
import licences  # FR-05 (U10): veterinarian licence registration and verification
import consultations as consult  # FR-06 (U11): durable consultations and the REG-02 gate
import deliveries as dlv  # FR-16 (U12): cold-chain delivery tracking
from practitioners import (CLASS_VETERINARIAN, PractitionerAuthorityGrant,  # FR-01 (U5)
                           evaluate as practitioner_evaluate)
from tenant_membership import (
    TenantMembershipDenied,
    TenantMembershipService,
    TenantMembershipUnavailable,
)
app.include_router(auth_router)

# NO USER IS CREATED AT STARTUP.
#
# Sponsor ruling PRE1_RULING=1-B: the three seeded identities (`u-admin-001`,
# `u-vet-001`, `u-owner-001`) are development artefacts and are discarded. They
# are not migrated and they are not recreated here.
#
# The reason is not tidiness. Their password was a literal in this file, in a
# repository whose visibility is PUBLIC — so every start of a durable deployment
# would have written three accounts with a published credential into the
# identity store, one of them holding the highest role in the system. A startup
# path that creates a `platform_admin` from a source literal is a backdoor
# whether or not anyone intended one.
#
# Identity is created only through the governed invite-gated registration path,
# or by an operator calling `seed_user` deliberately. `SEED-01` asserts that
# importing this module creates zero identities.

# Seed pilot invite codes — invite-gated registration (MVC-UX-WO-001 WI-1).
# No expiry on the pilot seeds; rotated/extended via PO bookkeeping.
seed_invite_code("OWNER-PILOT-001", "owner")
seed_invite_code("VET-PILOT-001", "veterinarian")

# ---------------------------------------------------------------------------
# In-memory stores (pilot phase — DB wiring deferred to PH7)
# ---------------------------------------------------------------------------
#: W0-G. The authoritative audit store.
#:
#: This was `_audit_log`, a module-level list. A list is a store that dies with
#: the process and is not shared between instances, so the chain it carried made
#: tampering detectable and did nothing about loss — the two properties W0-G is
#: careful to report separately.
#:
#: It is now the repository selected by PETCARE_PERSISTENCE_MODE, which is the
#: same boundary identity, sessions and invite codes reach. There is deliberately
#: NO second list alongside it: a shadow copy would be a second source of truth,
#: and the one that disagreed would be the one nobody was reading.
AUDIT_REPO = PERSISTENCE.audit

#: The governed tenant-assignment control path (Sponsor ruling, 12 Sep 2026 §3).
#: Direct repository access is not an authorized operating path; this is.
TENANT_MEMBERSHIP = TenantMembershipService(PERSISTENCE)

_notes: dict[str, dict] = {}
_appointments: dict[str, dict] = {}

uphr_service = UPHRService()
consent_repo = ConsentRepository(
    os.environ.get("CONSENT_STORE_PATH", "petcare_runtime/data/consent_store.json")
)

# ---------------------------------------------------------------------------
# Auth helpers — authorization derives from the validated session (W0-B)
# ---------------------------------------------------------------------------
# W0-D. The retired role is deliberately ABSENT, and absent by OMISSION rather
# than by being named. BRD V3.2 s4 records that PRD-09/sS2.6 has not decided
# whether it is a staff permission, a counterparty class, or a held seam;
# admitting it is a Sponsor product act and "may never arrive as a role-catalogue
# migration". It was previously present AND was the sole dispensing authority.
#
# `pharmacy` is likewise not a role here (PHARMACY_ROLE=REMOVE).
#
# This is now an ALIAS of the canonical set rather than a second copy of it. Two
# sets that were meant to be equal and drifted is precisely how CONF-01 happened:
# a role became storable but not authorisable, and nothing compared the two.
VALID_ROLES = ALLOWED_ROLES


def require_role(request: Request) -> str:
    """Caller's role, derived from the signed session. Never from a header.

    W0-B. This previously read `X-Petcare-Role` and only checked that the
    string was a known role name - so any client could assert any role, and
    every `if role != ROLE_X` guard in this module rested on a value the caller
    chose. There was no authentication in the authorization path at all.

    The role now comes from the session payload written server-side at sign-in.
    `X-Petcare-Role` is accepted by FastAPI (clients still send it) but carries
    ZERO authority: it is never read here, and a header that disagrees with the
    session is simply ignored rather than honoured.
    """
    payload = read_session(request)
    role = payload.get("role")
    if role not in VALID_ROLES:
        raise HTTPException(403, f"Unknown role: {role}")
    return role

def require_admin(role: str = Depends(require_role)) -> str:
    if role != ROLE_PLATFORM_ADMIN:
        raise HTTPException(403, "Admin role required")
    return role

# ---------------------------------------------------------------------------
# Audit helper
# ---------------------------------------------------------------------------
def _audit(
    event_name: str,
    actor_id: str,
    actor_role: str,
    tenant_id: str,
    resource_type: str,
    resource_id: str,
    action_result: str,
    correlation_id: str,
    clinic_id: Optional[str] = None,
    reason_code: Optional[str] = None,
) -> dict:
    ev = emit_audit_event(
        event_name=event_name,
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        clinic_id=clinic_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action_result=action_result,
        reason_code=reason_code,
        correlation_id=correlation_id,
    )
    record = {
        "audit_event_id": ev.audit_event_id,
        "event_name": ev.event_name,
        "actor_id": ev.actor_id,
        "actor_role": ev.actor_role,
        "tenant_id": ev.tenant_id,
        "clinic_id": ev.clinic_id,
        "resource_type": ev.resource_type,
        "resource_id": ev.resource_id,
        "action_result": ev.action_result,
        "reason_code": ev.reason_code,
        "correlation_id": ev.correlation_id,
        "occurred_at": ev.occurred_at,
    }
    # W0-G: the event is linked into the tamper-evident chain AND stored by the
    # repository, in one transaction. Linkage is not done here on purpose —
    # `prev_hash` is a read-then-write, and two callers doing it concurrently
    # produce a fork that the verifier reports as tampering. A caller cannot get
    # that wrong because a caller no longer does it.
    #
    # AuditWriteFailed is NOT caught. An action that mutates state while its
    # audit write silently fails is an unaudited mutation, and afterwards it is
    # indistinguishable from an action that never happened. The request fails.
    stored = AUDIT_REPO.append_event(record)
    log.info("AUDIT %s", json.dumps(stored, default=str))
    return stored


def verify_audit_chain() -> dict:
    """Verify the whole chain, reusing the governed algorithm unmodified.

    The algorithm names the digest field `hash`; the governed schema (CP-2 W0-G
    SCHEMA_IMPACT) names the column `event_hash`. The record is adapted here at
    the boundary rather than editing the algorithm, because W0-G's disposition is
    REUSE — do not reinvent hashing.

    A break is REPORTED, never repaired. Silently rehashing a broken chain would
    destroy the only evidence that it broke.

    W0-G persistence: the adaptation between the algorithm's `hash` and the
    governed `event_hash` column now lives in the repository, so the write path
    and the verify path cannot disagree about which fields the digest covers.
    """
    return AUDIT_REPO.verify_chain()

# ---------------------------------------------------------------------------
# Health + readiness
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "petcare-api",
        "version": "1.0.0",
        "ts": utc_now_iso(),
    }

@app.get("/ready")
def ready():
    return {"status": "ready", "ts": utc_now_iso()}

# ---------------------------------------------------------------------------
# Audit ingestion (UI probe + governance events)
# ---------------------------------------------------------------------------
#: Tenant recorded for a probe that carries no verified identity. Deliberately
#: NOT a real scope: `platform` is one, and defaulting to it let an unauthenticated
#: caller file events under it.
UNATTRIBUTED_TENANT = "UNATTRIBUTED"

#: Prefix that makes a client-asserted role structurally unable to collide with a
#: real one. `VALID_ROLES` contains no prefixed member, so no authorization check
#: can ever match a value recorded from this endpoint.
CLIENT_ASSERTED_PREFIX = "client-asserted:"


class AuditProbePayload(BaseModel):
    event_name: str
    actor_role: str
    surface: str
    correlation_id: str
    actor_id: Optional[str] = "system"
    resource_type: Optional[str] = "ui_surface"
    resource_id: Optional[str] = "unknown"
    action_result: Optional[str] = "probe"

    # `tenant_id` is deliberately ABSENT. It was `Optional[str] = "platform"`,
    # which is the same defect W0-C removed from the tenant header: an omitted
    # value silently granted the platform scope. Tenant is never client-supplied.


@app.post("/audit/ui")
def audit_ui_probe(request: Request, payload: AuditProbePayload):
    """UI telemetry probe. Unauthenticated by design — and therefore unauthoritative.

    This endpoint accepts events from a surface that may have no session yet, so
    it cannot be gated. What it must not do is let the caller CHOOSE what the
    record says about identity.

    Three things were client-supplied and are now server-derived or neutralised:

    * **tenant** — was `payload.tenant_id or "platform"`, so any caller could file
      audit events under the platform scope, or any other tenant, by naming it.
      It now comes from the session when one exists, and is `UNATTRIBUTED`
      otherwise. There is no way to assert it.
    * **role** — is prefixed, so a claimed `platform_admin` is recorded as
      `client-asserted:platform_admin` and can never match `VALID_ROLES`.
    * **actor** — likewise prefixed, so a claimed actor id cannot be mistaken for
      an authenticated one.

    This matters more since W0-G. Every audit write is now chained, so an event
    forged through this endpoint would be correctly hashed and the chain would
    verify as VERIFIED — the integrity proof would lend the forgery its own
    credibility. A tamper-evident log is only as trustworthy as the authority of
    what enters it.
    """
    try:
        tenant_id = read_session(request).get("tenant_id") or UNATTRIBUTED_TENANT
    except HTTPException:
        tenant_id = UNATTRIBUTED_TENANT

    record = _audit(
        event_name=payload.event_name,
        actor_id=f"{CLIENT_ASSERTED_PREFIX}{payload.actor_id or 'system'}",
        actor_role=f"{CLIENT_ASSERTED_PREFIX}{payload.actor_role}",
        tenant_id=tenant_id,
        resource_type=payload.resource_type or "ui_surface",
        resource_id=payload.resource_id or payload.surface,
        action_result=payload.action_result or "probe",
        correlation_id=payload.correlation_id,
        reason_code="UNAUTHENTICATED_UI_PROBE",
    )
    return {"accepted": True, "audit_event_id": record["audit_event_id"]}

@app.get("/audit/events")
def list_audit_events(role: str = Depends(require_admin)):
    """The whole chain. PRIVILEGED and cross-tenant by necessity.

    The chain is one sequence over every tenant, so reading it whole is the only
    way to verify it — and that is why this route is admin-gated rather than
    tenant-scoped. A caller who holds a tenant and not the admin role reads
    /audit/events/tenant instead, which cannot return another tenant's rows.
    """
    events = AUDIT_REPO.all_events()
    return {"events": events, "count": len(events)}


@app.get("/audit/events/tenant")
def list_audit_events_for_tenant(request: Request, limit: int = 100):
    """A caller's own tenant's events, and no other tenant's.

    The tenant comes from `require_tenant`, which derives it from the validated
    session (W0-C). It is never read from a query parameter or a header: a
    client-supplied scope here would turn the audit log into a cross-tenant read
    for anyone who could name a tenant.
    """
    tenant_id = require_tenant(request)
    events = AUDIT_REPO.query_events_for_tenant(tenant_id, limit=limit)
    return {"events": events, "count": len(events), "tenant_id": tenant_id}


# ---------------------------------------------------------------------------
# Tenant membership — the governed assignment path
# ---------------------------------------------------------------------------
class TenantMembershipRequest(BaseModel):
    """The request body. There is deliberately NO role field.

    Sponsor ruling §3: the path "must not accept a role as an input and must not
    create, modify, elevate, downgrade, or otherwise change an identity's role".
    That is implemented as an absence — a field that does not exist cannot be
    supplied, and a schema that rejects unknown fields cannot be talked into one.
    """

    model_config = {"extra": "forbid"}

    #: `None` is a revocation. Absent is NOT the same as null and is rejected by
    #: the model, so a client cannot revoke membership by omitting a field.
    tenant_id: Optional[str]
    reason: str


@app.get("/api/admin/identities/{user_id}/tenant")
def read_tenant_membership(user_id: str, request: Request,
                           role: str = Depends(require_admin)):
    """Readback. The verification path the ruling requires."""
    identity = TENANT_MEMBERSHIP.read(user_id)
    if identity is None:
        raise HTTPException(404, detail={"error": "IDENTITY_NOT_FOUND"})
    return {
        "user_id": identity.user_id,
        "tenant_id": identity.tenant_id,
        # The role is REPORTED and is not writable through this surface.
        "role": identity.role,
    }


@app.post("/api/admin/identities/{user_id}/tenant")
def set_tenant_membership(user_id: str, body: TenantMembershipRequest,
                          request: Request,
                          role: str = Depends(require_admin),
                          x_correlation_id: str = Header(default="unset")):
    """Assign, reassign or revoke tenant membership.

    `platform_admin` only — `require_admin` compares the canonical machine id
    from the validated session, so the authority cannot be asserted by a header.

    The actor is taken from the session, never from the body: an actor a caller
    could name would make the audit record a statement about what the caller
    claimed rather than about what happened.
    """
    payload = read_session(request)
    try:
        change = TENANT_MEMBERSHIP.set_membership(
            target_user_id=user_id,
            tenant_id=body.tenant_id,
            actor_id=payload["user_id"],
            actor_role=payload["role"],
            reason=body.reason,
            correlation_id=x_correlation_id,
        )
    except TenantMembershipUnavailable as exc:
        # 503: the deployment cannot perform a durable governed act. Not a 4xx —
        # the request was well formed and the caller was authorised.
        raise HTTPException(503, detail={"error": "MEMBERSHIP_STORE_UNAVAILABLE",
                                         "reason": str(exc)})
    except TenantMembershipDenied as exc:
        raise HTTPException(400, detail={"error": "MEMBERSHIP_CHANGE_DENIED",
                                         "reason": str(exc)})
    except AuditWriteFailed as exc:
        # Fail closed. An unaudited membership change is indistinguishable
        # afterwards from one that never happened.
        raise HTTPException(500, detail={"error": "AUDIT_WRITE_FAILED",
                                         "reason": str(exc)})

    return {
        "user_id": change.target_user_id,
        "previous_tenant_id": change.previous_tenant_id,
        "tenant_id": change.resulting_tenant_id,
        "revoked": change.is_revocation,
        "removal_event_id": change.removal_event_id,
        "addition_event_id": change.addition_event_id,
    }


@app.get("/audit/chain/verify")
def verify_audit_chain_endpoint(role: str = Depends(require_admin)):
    """Surface chain verification. W0-G: detectable and reportable, never healed.

    Returns the failing index and the expected/actual digests on a break, so a
    tamper or a gap is localisable rather than merely announced.
    """
    return verify_audit_chain()

# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------
class AppointmentRequest(BaseModel):
    pet_id: str
    owner_id: str
    clinic_id: str
    tenant_id: str
    requested_at: Optional[str] = None
    notes: Optional[str] = None

@app.post("/api/appointments")
def book_appointment(
    request: Request,
    body: AppointmentRequest,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role = _actor(request)  # AC-FR-01-01: never a client-supplied actor
    if role not in {ROLE_OWNER, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Only owners or admins may book appointments")
    appt_id = str(uuid4())
    now = utc_now_iso()
    appt = {
        "appointment_id": appt_id,
        "pet_id": body.pet_id,
        "owner_id": body.owner_id,
        "clinic_id": body.clinic_id,
        "tenant_id": require_tenant(request, body.tenant_id),
        "status": "REQUESTED",
        "requested_at": body.requested_at or now,
        "created_at": now,
        "notes": body.notes,
    }
    _appointments[appt_id] = appt
    _audit(
        event_name="appointment.booked",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=require_tenant(request, body.tenant_id),
        resource_type="appointment",
        resource_id=appt_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=body.clinic_id,
    )
    return appt

@app.get("/api/appointments/{appointment_id}")
def get_appointment(
    request: Request,
    appointment_id: str,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role = _actor(request)  # AC-FR-01-01: never a client-supplied actor
    appt = _appointments.get(appointment_id)
    if not appt or appt["tenant_id"] != require_tenant(request):
        raise HTTPException(404, "Appointment not found")
    _audit(
        event_name="appointment.viewed",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=appt["tenant_id"],
        resource_type="appointment",
        resource_id=appointment_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=appt.get("clinic_id"),
    )
    return appt

# ---------------------------------------------------------------------------
# Consultations
# ---------------------------------------------------------------------------
class ConsultationRequest(BaseModel):
    pet_id: str
    owner_id: str
    veterinarian_id: str
    #: Optional (U11): the session decides; a disagreeing value is refused.
    tenant_id: Optional[str] = None
    clinic_id: Optional[str] = None
    #: FR-06: IN_PERSON, or REMOTE_VIDEO — fail-closed until REG-02 counsel is recorded (AC-FR-06-05).
    mode: str = consult.MODE_IN_PERSON


CONSULTATION_REPO = PERSISTENCE.consultations


def _consultation(session_id: str, tenant_id: str) -> Optional[dict]:
    """The consultation of the SESSION tenant as its read model, or None (AC-FR-06-04)."""
    c = CONSULTATION_REPO.get(session_id, tenant_id=tenant_id)
    return None if c is None else consult.read_model(c, CONSULTATION_REPO.outcome_of(session_id, tenant_id=tenant_id))


def _remote_consultation_gate() -> dict:
    d = consult.remote_consultation_lawful(CONSULTATION_REPO.determinations())
    if d is None:
        return {"offered": False, "dependency": "COUNSEL:REG-02_TELEMEDICINE",
                "reason": "Remote veterinary consultation is not offered until the KSA telemedicine counsel "
                          "determination (REG-02) is recorded."}
    return {"offered": True, "form": d.form, "reference": d.reference}

@app.post("/api/consultations")
def start_consultation(
    request: Request,
    body: ConsultationRequest,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role = _actor(request)  # AC-FR-01-01: never a client-supplied actor
    if role not in {ROLE_VETERINARIAN, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Only vets or admins may start consultations")
    tenant_id = require_tenant(request, body.tenant_id)
    if body.mode not in consult.MODES:
        raise HTTPException(400, f"mode must be one of {list(consult.MODES)}")
    if body.mode == consult.MODE_REMOTE_VIDEO and not _remote_consultation_gate()["offered"]:
        # AC-FR-06-05: fail closed until counsel; the refusal is audited.
        _audit(event_name="consultation.remote.refused", actor_id=actor_id, actor_role=actor_role,
               tenant_id=tenant_id, resource_type="consultation_session", resource_id=body.pet_id,
               action_result="denied", correlation_id=x_correlation_id, reason_code="COUNSEL:REG-02_TELEMEDICINE")
        raise HTTPException(403, detail={"error": "REMOTE_CONSULTATION_NOT_OFFERED", **_remote_consultation_gate()})
    # AC-FR-06-04: both participants are identities of THIS tenant in their roles.
    for uid, want in ((body.owner_id, ROLE_OWNER), (body.veterinarian_id, ROLE_VETERINARIAN)):
        ident = PERSISTENCE.identities.get_by_user_id(uid)
        if ident is None or ident.tenant_id != tenant_id or ident.role != want:
            raise HTTPException(400, f"{want} {uid!r} is not a {want} of this tenant")
    session_id = str(uuid4())
    c = consult.Consultation(session_id=session_id, tenant_id=tenant_id, pet_id=body.pet_id, owner_id=body.owner_id,
                             veterinarian_id=body.veterinarian_id, requested_by_actor_id=actor_id, mode=body.mode,
                             created_at=datetime.now(timezone.utc), clinic_id=body.clinic_id)
    try:
        CONSULTATION_REPO.create(c)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Consultation refused: {exc}") from None
    _audit(
        event_name="consultation.session.requested",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        resource_type="consultation_session",
        resource_id=session_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=body.clinic_id,
    )
    return consult.read_model(c, None)

@app.get("/api/consultations/{session_id}")
def get_consultation(
    request: Request,
    session_id: str,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role = _actor(request)  # AC-FR-01-01: never a client-supplied actor
    session = _consultation(session_id, require_tenant(request))
    if not session:
        raise HTTPException(404, "Consultation session not found")
    _audit(
        event_name="consultation.session.viewed",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=session["tenant_id"],
        resource_type="consultation_session",
        resource_id=session_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=session.get("clinic_id"),
    )
    return session

class NoteRequest(BaseModel):
    session_id: str
    pet_id: str
    content: str
    tenant_id: str

@app.get("/api/consultations")
def list_consultations(request: Request, role: str = Depends(require_role)):
    """The caller's consultations in the session tenant (an admin sees the tenant's), plus whether
    remote consultation is offered (AC-FR-06-05)."""
    actor_id, _r = _actor(request)
    tenant_id = require_tenant(request)
    rows = [c for c in CONSULTATION_REPO.for_tenant(tenant_id)
            if role in (ROLE_PLATFORM_ADMIN, ROLE_PARTNER_CLINIC_ADMIN) or actor_id in (c.owner_id, c.veterinarian_id)]
    return {"remote": _remote_consultation_gate(),
            "consultations": [consult.read_model(c, CONSULTATION_REPO.outcome_of(c.session_id, tenant_id=tenant_id))
                              for c in rows]}


@app.get("/api/consultations/remote/availability")
def remote_consultation_availability(request: Request, role: str = Depends(require_role)):
    return _remote_consultation_gate()


class OutcomeRequest(BaseModel):
    model_config = {"extra": "forbid"}

    outcome: str


@app.post("/api/consultations/{session_id}/outcome")
def record_consultation_outcome(
    session_id: str,
    body: OutcomeRequest,
    request: Request,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-06-04: the consultation's veterinarian records its outcome once; audited."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    session = _consultation(session_id, tenant_id)
    if not session:
        raise HTTPException(404, "Consultation session not found")
    if actor_id != session["veterinarian_id"]:
        raise HTTPException(403, "Only the consultation's veterinarian records its outcome")
    _require_practitioner_authority(actor_id, tenant_id)
    try:
        CONSULTATION_REPO.record_outcome(consult.ConsultationOutcome(
            session_id=session_id, tenant_id=tenant_id, outcome=body.outcome, recorded_by_actor_id=actor_id,
            recorded_at=datetime.now(timezone.utc)))
    except RepositoryDenied as exc:
        raise HTTPException(409 if "already" in str(exc) else 400, f"Outcome refused: {exc}") from None
    _audit(event_name="consultation.outcome.recorded", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="consultation_session", resource_id=session_id,
           action_result="success", correlation_id=x_correlation_id)
    return _consultation(session_id, tenant_id)


@app.post("/api/consultations/{session_id}/notes")
def create_note(
    request: Request,
    session_id: str,
    body: NoteRequest,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role = _actor(request)  # AC-FR-01-01: never a client-supplied actor
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only vets may create consultation notes")
    session = _consultation(session_id, require_tenant(request))
    if not session:
        raise HTTPException(404, "Session not found")
    _require_practitioner_authority(actor_id, session["tenant_id"])  # FR-05 (U10): verified licence at the act
    note_id = str(uuid4())
    now = utc_now_iso()
    note = {
        "note_id": note_id,
        "session_id": session_id,
        "pet_id": body.pet_id,
        "veterinarian_id": actor_id,
        "content": body.content,
        "status": NOTE_DRAFT,
        "created_at": now,
        "signed_at": None,
        "signed_by_actor_id": None,
    }
    _notes[note_id] = note
    _audit(
        event_name="consultation.note.created",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=require_tenant(request, body.tenant_id),
        resource_type="consultation_note",
        resource_id=note_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return note

@app.post("/api/consultations/notes/{note_id}/sign")
def sign_note(
    request: Request,
    note_id: str,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role = _actor(request)  # AC-FR-01-01: never a client-supplied actor
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only vets may sign notes")
    note = _notes.get(note_id)
    parent = _consultation(note["session_id"], require_tenant(request)) if note else None
    if not note or not parent:
        raise HTTPException(404, "Note not found")
    _require_practitioner_authority(actor_id, parent["tenant_id"])  # FR-05 (U10): verified licence at the act
    if note["status"] == NOTE_SIGNED:
        raise HTTPException(409, "Note already signed — immutable")
    now = utc_now_iso()
    note["status"] = NOTE_SIGNED
    note["signed_at"] = now
    note["signed_by_actor_id"] = actor_id
    _audit(
        event_name="consultation.note.signed",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=require_tenant(request),
        resource_type="consultation_note",
        resource_id=note_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return note

# ---------------------------------------------------------------------------
# Prescriptions  (FR-14 · Option A)
# ---------------------------------------------------------------------------
#
# The store was `_prescriptions`, a module-level dict. It is now the repository
# selected by PETCARE_PERSISTENCE_MODE — the same boundary identity, sessions,
# invite codes and the audit log already reach. There is deliberately no second
# dict alongside it: a shadow copy is a second source of truth, and the one that
# disagreed would be the one nobody was reading (W0-G's argument, unchanged).
#
# The lifecycle gained a middle state:
#
#     ISSUED  ->  VET_VERIFIED  ->  DISPENSED
#
# Before this, dispensing's only state guard was `status == "ISSUED"`, so a
# prescription was dispensable the instant it existed. The transitions are
# defined in `prescriptions.py`, enforced by both repositories, and enforced a
# second time by CHECK constraints in migration 0036.
PRESCRIPTION_REPO = PERSISTENCE.prescriptions


def _actor(request: Request) -> tuple[str, str]:
    """The caller's identity AND role, both from the validated session.

    W0-B, applied to the audit actor. Every route below previously took
    `x_actor_id: str = Header(...)` and wrote that value into the audit log as
    the actor — so the log recorded whoever the client said it was, on routes
    whose whole purpose is attributing a clinical act to a professional. The
    header is still accepted by FastAPI (clients send it) and carries ZERO
    authority: it is never read.
    """
    payload = read_session(request)
    return payload["user_id"], payload["role"]


#: FR-01 · U5 — the live practitioner authority attribute (AC-FR-01-02).
PRACTITIONER_REPO = PERSISTENCE.practitioners


def _require_practitioner_authority(actor_id: str, tenant_id: str):
    """The grant in force NOW for this actor in this tenant, or 403.

    Role is necessary and not sufficient: a regulated act additionally reads a
    live, time-bounded authority attribute at the moment of the act (REQ-MVC-8.32).
    The refusal names the attribute and why it is not in force (REQ-MVC-8.38).
    """
    grant, reason = practitioner_evaluate(
        PRACTITIONER_REPO.grants_for(actor_id, tenant_id=tenant_id),
        professional_class=CLASS_VETERINARIAN, when=datetime.now(timezone.utc))
    if grant is None:
        # FR-05 AC-FR-05-01 (U10): a clinical act refused for want of a verified, unexpired
        # licence is audited — a refusal that leaves no trace is indistinguishable from no attempt.
        _audit(event_name="practitioner.authority.refused", actor_id=actor_id, actor_role=ROLE_VETERINARIAN,
               tenant_id=tenant_id, resource_type="practitioner_authority", resource_id=actor_id,
               action_result="denied", correlation_id=str(uuid4()), reason_code=reason)
        raise HTTPException(403, detail={"error": "PRACTITIONER_AUTHORITY_REQUIRED",
                                         "attribute": CLASS_VETERINARIAN, "reason": reason})
    return grant


class PrescriptionRequest(BaseModel):
    pet_id: str
    session_id: str
    #: Optional (U9): the session decides. A value that disagrees with the session is refused.
    tenant_id: Optional[str] = None
    clinic_id: Optional[str] = None
    medication_name: str
    dosage: str
    instructions: str


def _rx_or_404(prescription_id: str, tenant_id: str) -> Prescription:
    """The prescription, scoped to the caller's tenant, or 404.

    404 and not 403. Answering "403 forbidden" for a record that exists in
    ANOTHER tenant confirms its existence to a caller who may not read it, and
    the difference between 403 and 404 is a working cross-tenant enumeration
    oracle. The repository applies the tenant predicate itself, so this cannot
    be bypassed by forgetting a filter at one call site.
    """
    rx = PRESCRIPTION_REPO.get(prescription_id, tenant_id=tenant_id)
    if rx is None:
        raise HTTPException(404, "Prescription not found")
    return rx


def _rx_read_audit(request: Request, event_name: str, resource_type: str, resource_id: str,
                   tenant_id: str) -> None:
    """AC-FR-14-05 (U9): every prescription read is audited with the session actor."""
    actor_id, actor_role = _actor(request)
    _audit(event_name=event_name, actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type=resource_type, resource_id=resource_id, action_result="success",
           correlation_id=request.headers.get("x-correlation-id") or str(uuid4()))


@app.post("/api/prescriptions")
def issue_prescription(
    request: Request,
    body: PrescriptionRequest,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only vets may issue prescriptions")
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request, body.tenant_id)
    authority = _require_practitioner_authority(actor_id, tenant_id)  # AC-FR-01-02: live attribute at the act
    rx_id = str(uuid4())
    rx = Prescription(
        prescription_id=rx_id,
        tenant_id=tenant_id,
        pet_id=body.pet_id,
        session_id=body.session_id,
        clinic_id=body.clinic_id,
        issuing_vet_id=actor_id,
        medication_name=body.medication_name,
        dosage=body.dosage,
        instructions=body.instructions,
        status=STATUS_ISSUED,
        issued_at=datetime.now(timezone.utc),
    )
    try:
        stored = PRESCRIPTION_REPO.create(rx, actor_id=actor_id, actor_role=actor_role)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Prescription refused: {exc}") from None
    _audit(
        event_name="prescription.issued",
        reason_code=f"authority:{authority.grant_id}",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        resource_type="prescription",
        resource_id=rx_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=body.clinic_id,
    )
    return stored.to_read_model()


@app.get("/api/prescriptions/{prescription_id}")
def get_prescription(
    request: Request,
    prescription_id: str,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    tenant_id = require_tenant(request)
    rx = _rx_or_404(prescription_id, tenant_id)
    actor_id, actor_role = _actor(request)
    _audit(
        event_name="prescription.viewed",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        resource_type="prescription",
        resource_id=prescription_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=rx.clinic_id,
    )
    return rx.to_read_model()


@app.post("/api/prescriptions/{prescription_id}/verify")
def verify_prescription(
    request: Request,
    prescription_id: str,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """The veterinarian verification step. ISSUED -> VET_VERIFIED.

    Authority is the veterinarian's, unchanged and deliberately not widened: the
    professional-authority class for the dispensing chain is unclassified
    pending a regulatory fact this estate does not hold (REQ-DISP-AUTH-FAILCLOSED,
    BRD V3.2 §11.1), and verification sits inside that same chain.

    RECORDED HONESTLY: the issuing veterinarian MAY verify their own
    prescription. This adds a deliberate second ACT but not a second ACTOR, so
    it is a workflow gate rather than a separation-of-duties control, and it is
    not presented as one. `verified_by_vet_id` is stored separately from
    `issuing_vet_id` precisely so a future ratified rule requiring a distinct
    verifier can be applied to existing records rather than needing a migration
    to tell the two apart.
    """
    if role != ROLE_VETERINARIAN:
        raise HTTPException(
            403,
            "Verification is restricted to a veterinarian: the "
            "professional-authority class for this act is unclassified "
            "(REQ-DISP-AUTH-FAILCLOSED)",
        )
    tenant_id = require_tenant(request)
    _rx_or_404(prescription_id, tenant_id)
    actor_id, actor_role = _actor(request)
    authority = _require_practitioner_authority(actor_id, tenant_id)  # AC-FR-01-02: live attribute at the act
    try:
        moved = PRESCRIPTION_REPO.transition(
            prescription_id,
            tenant_id=tenant_id,
            to_status=STATUS_VET_VERIFIED,
            actor_id=actor_id,
            actor_role=actor_role,
        )
    except TransitionDenied as exc:
        # The refusal is audited. A denied clinical transition that leaves no
        # trace is indistinguishable from one nobody attempted.
        _audit(
            event_name="prescription.verification_denied",
            actor_id=actor_id,
            actor_role=actor_role,
            tenant_id=tenant_id,
            resource_type="prescription",
            resource_id=prescription_id,
            action_result="denied",
            correlation_id=x_correlation_id,
            reason_code="TRANSITION_NOT_ALLOWED",
        )
        raise HTTPException(409, f"Cannot verify — {exc}") from None
    _audit(
        event_name="prescription.vet_verified",
        reason_code=f"authority:{authority.grant_id}",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        resource_type="prescription",
        resource_id=prescription_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=moved.clinic_id,
    )
    return moved.to_read_model()


class DispenseRequest(BaseModel):
    """FR-19 AC-FR-19-01 (U13): a dispense draws from stock and records the batch."""
    model_config = {"extra": "forbid"}

    location_id: str
    product_id: str
    batch: str
    quantity: int


@app.post("/api/prescriptions/{prescription_id}/dispense")
def dispense_prescription(
    request: Request,
    prescription_id: str,
    body: Optional[DispenseRequest] = None,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    # REQ-DISP-AUTH-FAILCLOSED (BRD V3.2 §11.1). Dispensing acts whose
    # professional-authority class is unclassified fail closed to VETERINARIAN.
    # This route previously required PHARMACY_OPERATOR and DENIED the
    # veterinarian - the exact inversion of the governed invariant, using a role
    # the specification says must not exist. Two acts remain deliberately
    # unclassified pending a regulatory fact this estate does not hold: whether
    # a non-veterinarian may lawfully dispense a veterinary medicine in KSA, and
    # witness qualification for wastage. Until a RATIFIED professional-authority
    # rule names another actor class, veterinarian only. This is a fail-closed
    # DEFAULT, not a determination, and must not be widened for convenience.
    if role != ROLE_VETERINARIAN:
        # AC-FR-14-02 (U9): the refusal is audited. The request carries no class and none
        # is read from it — nothing a client asserts can widen this rule.
        actor_id, actor_role = _actor(request)
        _audit(event_name="prescription.dispense_denied", actor_id=actor_id, actor_role=actor_role,
               tenant_id=require_tenant(request), resource_type="prescription", resource_id=prescription_id,
               action_result="denied", correlation_id=x_correlation_id, reason_code="NOT_VETERINARIAN")
        raise HTTPException(
            403,
            "Dispensing is restricted to a veterinarian: the professional-authority "
            "class for this act is unclassified (REQ-DISP-AUTH-FAILCLOSED)",
        )
    tenant_id = require_tenant(request)
    rx = _rx_or_404(prescription_id, tenant_id)
    actor_id, actor_role = _actor(request)
    authority = _require_practitioner_authority(actor_id, tenant_id)  # AC-FR-01-02: live attribute at the act
    # FR-19 AC-FR-19-01 (U13): every dispense records the batch — it draws from stock as a SUPPLY
    # movement citing the prescription. Checked after authority/tenancy/state so those refusals keep
    # their meaning; a verified prescription with no stock origin is refused, never dispensed blind.
    movement = None
    if rx.status == STATUS_VET_VERIFIED:
        if body is None or body.quantity <= 0:
            raise HTTPException(400, {"error": "STOCK_ORIGIN_REQUIRED",
                                      "detail": "a dispense names the location, product, batch and a positive quantity"})
        movement = StockMovement(movement_id=str(uuid4()), tenant_id=tenant_id, location_id=body.location_id,
                                 product_id=body.product_id, batch=body.batch, quantity_delta=-body.quantity,
                                 reason=SUPPLY, supply_class=INVENTORY_REPO.supply_class_of(body.product_id),
                                 actor_id=actor_id, actor_role=actor_role, created_at=datetime.now(timezone.utc),
                                 prescription_id=prescription_id)
        try:
            INVENTORY_REPO.record([movement])
        except RepositoryDenied as exc:
            raise HTTPException(400, f"Dispense refused: {exc}") from None
    try:
        moved = PRESCRIPTION_REPO.transition(
            prescription_id,
            tenant_id=tenant_id,
            to_status=STATUS_DISPENSED,
            actor_id=actor_id,
            actor_role=actor_role,
        )
    except TransitionDenied as exc:
        if movement is not None:  # lost a race: return the stock (compensating movement; the ledger is never rewritten)
            INVENTORY_REPO.record([dataclasses.replace(movement, movement_id=str(uuid4()), quantity_delta=body.quantity,
                                                       reason=ADJUSTMENT, created_at=datetime.now(timezone.utc))])
        _audit(
            event_name="prescription.dispense_denied",
            actor_id=actor_id,
            actor_role=actor_role,
            tenant_id=tenant_id,
            resource_type="prescription",
            resource_id=prescription_id,
            action_result="denied",
            correlation_id=x_correlation_id,
            reason_code="TRANSITION_NOT_ALLOWED",
        )
        # 409, and the message names the state. An unverified prescription and
        # an already-dispensed one are both refused here, by the same rule.
        raise HTTPException(409, f"Cannot dispense — {exc}") from None
    _audit(
        event_name="prescription.dispensed",
        reason_code=f"authority:{authority.grant_id}",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        resource_type="prescription",
        resource_id=prescription_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=moved.clinic_id,
    )
    _audit(event_name="inventory.movement.recorded", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="stock_movement", resource_id=movement.movement_id, action_result="success",
           correlation_id=x_correlation_id, reason_code=f"{SUPPLY}:{movement.supply_class}:batch:{movement.batch}")
    return {**moved.to_read_model(), "dispensed_batch": movement.batch, "movement_id": movement.movement_id}


# ---------------------------------------------------------------------------
# Prescription attachments  (Option A §5)
# ---------------------------------------------------------------------------
DOCUMENT_STORE = build_document_store()


@app.post("/api/prescriptions/{prescription_id}/documents")
async def upload_prescription_document(
    request: Request,
    prescription_id: str,
    file: UploadFile = File(...),
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """Attach a prescription document.

    ORDER IS LOAD-BEARING (§5, "upload failure does not create an inconsistent
    prescription state"):
      1. authorize, and resolve the prescription inside the caller's tenant;
      2. validate the payload — type and size — BEFORE anything is written;
      3. write the object;
      4. write the metadata row.
    Nothing about the prescription changes until the bytes are known storable,
    and the metadata row is written last so a row can never reference an object
    that was never stored.
    """
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only vets may attach prescription documents")
    tenant_id = require_tenant(request)
    _rx_or_404(prescription_id, tenant_id)
    actor_id, actor_role = _actor(request)

    payload = await file.read()
    try:
        validate_upload(content_type=file.content_type or "", payload=payload)
    except DocumentRejected as exc:
        _audit(
            event_name="prescription.document_rejected",
            actor_id=actor_id,
            actor_role=actor_role,
            tenant_id=tenant_id,
            resource_type="prescription",
            resource_id=prescription_id,
            action_result="denied",
            correlation_id=x_correlation_id,
            reason_code="DOCUMENT_REJECTED",
        )
        raise HTTPException(400, str(exc)) from None

    storage_key = new_storage_key(tenant_id=tenant_id, prescription_id=prescription_id)
    doc = PrescriptionDocument(
        document_id=str(uuid4()),
        prescription_id=prescription_id,
        tenant_id=tenant_id,
        uploaded_by_actor_id=actor_id,
        # The caller's filename is metadata. It is never joined to a path —
        # storage_key is server-generated, so a traversal sequence in a filename
        # reaches the same code and the same directory as any other name.
        filename=file.filename or "prescription",
        content_type=(file.content_type or "").split(";")[0].strip().lower(),
        byte_size=len(payload),
        content_sha256=sha256_hex(payload),
        storage_key=storage_key,
        uploaded_at=datetime.now(timezone.utc),
    )
    try:
        DOCUMENT_STORE.put(storage_key, payload)
    except (ObjectStoreUnavailable, DocumentRejected) as exc:
        raise HTTPException(503, f"Document store unavailable: {exc}") from None
    try:
        stored = PRESCRIPTION_REPO.attach_document(doc)
    except (RepositoryDenied, PrescriptionNotFound) as exc:
        raise HTTPException(400, f"Document refused: {exc}") from None

    _audit(
        event_name="prescription.document_uploaded",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        resource_type="prescription_document",
        resource_id=stored.document_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return stored.to_read_model()


@app.get("/api/prescriptions/{prescription_id}/documents")
def list_prescription_documents(
    request: Request,
    prescription_id: str,
    role: str = Depends(require_role),
):
    tenant_id = require_tenant(request)
    _rx_or_404(prescription_id, tenant_id)
    _rx_read_audit(request, "prescription.documents_listed", "prescription", prescription_id, tenant_id)
    return [
        d.to_read_model()
        for d in PRESCRIPTION_REPO.documents_for(prescription_id, tenant_id=tenant_id)
    ]


@app.get("/api/prescriptions/{prescription_id}/documents/{document_id}")
def download_prescription_document(
    request: Request,
    prescription_id: str,
    document_id: str,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """Serve the bytes — as a download, never as a rendered document.

    `application/octet-stream` plus `Content-Disposition: attachment` regardless
    of the stored content type. The stored type is attacker-influenced; serving
    a file inline under a type the uploader chose is how an attachment becomes
    stored XSS in the application's own origin.
    """
    tenant_id = require_tenant(request)
    _rx_or_404(prescription_id, tenant_id)
    doc = PRESCRIPTION_REPO.get_document(document_id, tenant_id=tenant_id)
    if doc is None or doc.prescription_id != prescription_id:
        raise HTTPException(404, "Document not found")
    try:
        payload = DOCUMENT_STORE.get(doc.storage_key)
    except ObjectStoreUnavailable as exc:
        raise HTTPException(503, f"Document store unavailable: {exc}") from None

    actor_id, actor_role = _actor(request)
    _audit(
        event_name="prescription.document_downloaded",
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        resource_type="prescription_document",
        resource_id=document_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return Response(
        content=payload,
        media_type=SERVED_CONTENT_TYPE,
        headers={"Content-Disposition": 'attachment; filename="prescription-document"'},
    )


# ---------------------------------------------------------------------------
# The dispensing queue  (Option A §7/§8)
# ---------------------------------------------------------------------------
@app.get("/api/prescriptions/queue/awaiting-dispense")
def awaiting_dispense_queue(
    request: Request,
    role: str = Depends(require_role),
):
    """Verified prescriptions in the caller's tenant, awaiting dispense.

    This is the surface the pilot's dispensing screen reads.

    WHO MAY READ IT. Veterinarian and partner clinic admin — both existing
    canonical roles. NO new role is introduced here. `pharmacy` is not an
    authorization principal in this estate (PHARMACY_ROLE=REMOVE, W0-D), and
    admitting one is a Sponsor product act, not an engineering convenience. The
    consequence is stated plainly rather than worked around: an external
    pharmacy operator CANNOT read this queue today, because there is no identity
    the platform can mint for them.

    The tenant scope comes from the session. There is no tenant parameter to
    supply, so there is nothing to tamper with.
    """
    if role not in (ROLE_VETERINARIAN, ROLE_PARTNER_CLINIC_ADMIN):
        raise HTTPException(403, "Not authorized to read the dispensing queue")
    tenant_id = require_tenant(request)
    _rx_read_audit(request, "prescription.queue_viewed", "prescription_queue", STATUS_VET_VERIFIED, tenant_id)
    return [
        rx.to_read_model()
        for rx in PRESCRIPTION_REPO.list_by_status(
            tenant_id=tenant_id, status=STATUS_VET_VERIFIED
        )
    ]


@app.get("/api/prescriptions/queue/awaiting-verification")
def awaiting_verification_queue(request: Request, role: str = Depends(require_role)):
    """AC-FR-14-01 (U9): issued prescriptions in the session tenant awaiting the vet's
    verification — the list /vet/prescriptions works from. Veterinarians only."""
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only a veterinarian verifies prescriptions")
    tenant_id = require_tenant(request)
    _rx_read_audit(request, "prescription.queue_viewed", "prescription_queue", STATUS_ISSUED, tenant_id)
    return [rx.to_read_model() for rx in PRESCRIPTION_REPO.list_by_status(tenant_id=tenant_id, status=STATUS_ISSUED)]


#: AC-FR-14-06 (U9). The served app has no live SFDA adapter; tests substitute a contract double.
SFDA_PORT = sfda.UnconfiguredSfdaAdapter()


@app.post("/api/prescriptions/{prescription_id}/sfda-validation")
def sfda_validate_prescription(
    request: Request,
    prescription_id: str,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """Ask the SFDA prescription-validation port. Only an explicit VALID is valid; the
    result is audited. Dependency EXTERNAL:SFDA_API: no live adapter is bound."""
    if role not in (ROLE_VETERINARIAN, ROLE_PARTNER_CLINIC_ADMIN):
        raise HTTPException(403, "Not authorized to validate prescriptions")
    tenant_id = require_tenant(request)
    rx = _rx_or_404(prescription_id, tenant_id)
    try:
        result = sfda.normalise(SFDA_PORT.validate(prescription_id=rx.prescription_id,
                                                   medication_name=rx.medication_name))
    except Exception:
        result = sfda.SfdaResult(sfda.UNAVAILABLE, "the SFDA interface did not answer")
    actor_id, actor_role = _actor(request)
    _audit(event_name="prescription.sfda_validated", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="prescription", resource_id=prescription_id,
           action_result="success" if result.valid else "denied", correlation_id=x_correlation_id,
           reason_code=f"SFDA_{result.status}")
    return {"prescription_id": prescription_id, "status": result.status, "valid": result.valid,
            "detail": result.detail}


#: AC-FR-14-07 (U9): BRD §13.1 target — 95% verified within 30 minutes (measured in production).
VERIFICATION_TARGET_MINUTES = 30


@app.get("/api/prescriptions/metrics/verification-time")
def prescription_verification_metric(request: Request, role: str = Depends(require_role)):
    """Share of the session tenant's verified prescriptions verified within 30 minutes of
    issue, and the p95 verification time. The instrument for AC-FR-14-07; the production
    reading itself is the PRODUCTION dependency."""
    if role not in (ROLE_VETERINARIAN, ROLE_PARTNER_CLINIC_ADMIN):
        raise HTTPException(403, "Not authorized to read prescription metrics")
    tenant_id = require_tenant(request)
    minutes = sorted((rx.verified_at - rx.issued_at).total_seconds() / 60.0
                     for status in (STATUS_VET_VERIFIED, STATUS_DISPENSED)
                     for rx in PRESCRIPTION_REPO.list_by_status(tenant_id=tenant_id, status=status)
                     if rx.verified_at is not None)
    _rx_read_audit(request, "prescription.metrics_viewed", "prescription_metric", "verification-time", tenant_id)
    n = len(minutes)
    within = sum(1 for m in minutes if m <= VERIFICATION_TARGET_MINUTES)
    p95 = minutes[max(0, int(round(0.95 * n)) - 1)] if n else None
    return {"verified": n, "within_target": within, "target_minutes": VERIFICATION_TARGET_MINUTES,
            "share_within_target": (within / n) if n else None, "p95_minutes": p95,
            "meets_target": (n > 0 and within / n >= 0.95)}


@app.get("/api/prescriptions/{prescription_id}/transitions")
def prescription_transitions(
    request: Request,
    prescription_id: str,
    role: str = Depends(require_role),
):
    """The record's own transition ledger, tenant-scoped."""
    tenant_id = require_tenant(request)
    _rx_or_404(prescription_id, tenant_id)
    _rx_read_audit(request, "prescription.transitions_viewed", "prescription", prescription_id, tenant_id)
    return [
        {
            "transition_id": t.transition_id,
            "from_status": t.from_status,
            "to_status": t.to_status,
            "actor_id": t.actor_id,
            "actor_role": t.actor_role,
            "occurred_at": t.occurred_at.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        for t in PRESCRIPTION_REPO.transitions_for(prescription_id, tenant_id=tenant_id)
    ]


# ---------------------------------------------------------------------------
# Pet profiles (UPHR)
# ---------------------------------------------------------------------------
class PetRequest(BaseModel):
    """BRD P373-P374 fields (AC-FR-02-01). `owner_id` is honoured only for an
    admin creating on an owner's behalf; an owner always creates for themself."""

    model_config = {"extra": "forbid"}

    #: Optional: the tenant comes from the session. If supplied it must match it
    #: (`require_tenant`), never widen it.
    tenant_id: Optional[str] = None
    owner_id: Optional[str] = None
    name: str
    species: str
    breed: Optional[str] = None
    birth_date: Optional[str] = None
    weight_kg: Optional[float] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    preferences: Optional[str] = None


class PetUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    birth_date: Optional[str] = None
    weight_kg: Optional[float] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    preferences: Optional[str] = None


class PetIdentificationRequest(BaseModel):
    model_config = {"extra": "forbid"}

    id_type: str
    id_value: str
    captured_at: str
    capture_method: str
    issuing_scheme: Optional[str] = None


class PetMedicalRecordRequest(BaseModel):
    model_config = {"extra": "forbid"}

    record_type: str
    title: str
    detail: Optional[str] = None


#: FR-02 · the durable pet store selected by PETCARE_PERSISTENCE_MODE (U2). The
#: profile no longer lives in the node-local UPHR JSON file.
PET_REPO = PERSISTENCE.pets

PET_READERS = {ROLE_OWNER, ROLE_VETERINARIAN, ROLE_PARTNER_CLINIC_ADMIN, ROLE_PLATFORM_ADMIN}


def _iso_date(value: Optional[str], field_name: str):
    if value is None:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        raise HTTPException(400, f"{field_name} must be an ISO date") from None


def _pet_or_404(request: Request, pet_id: str):
    """The pet, scoped to the session tenant — and, for an owner, to their own pets.

    404 rather than 403 for a pet in another tenant or of another owner: a 403
    would confirm the record exists (the enumeration oracle `_rx_or_404` refuses).
    """
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    pet = PET_REPO.get(pet_id, tenant_id=tenant_id)
    if pet is None or (actor_role == ROLE_OWNER and pet.owner_id != actor_id):
        raise HTTPException(404, "Pet not found")
    return pet, actor_id, actor_role, tenant_id


def _pet_audit(event: str, actor_id: str, actor_role: str, tenant_id: str, pet_id: str,
               correlation_id: str) -> None:
    _audit(event_name=event, actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="pet", resource_id=pet_id, action_result="success",
           correlation_id=correlation_id)


@app.post("/api/pets")
def create_pet(
    request: Request,
    body: PetRequest,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-02-01 create; AC-FR-02-04: attributed to the SESSION actor.

    Rule 21 — there is no client-supplied actor input (U1). The actor and role
    come from the signed session (`_actor`, as the prescription routes derive
    them) and the tenant from `require_tenant`.
    """
    if role not in {ROLE_OWNER, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Only owners or admins may create pet profiles")
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request, body.tenant_id)
    if actor_role == ROLE_OWNER:
        owner_id = actor_id
    elif body.owner_id and body.owner_id.strip():
        owner_id = body.owner_id
    else:
        raise HTTPException(400, "owner_id is required when an admin creates a pet profile")
    now = datetime.now(timezone.utc)
    pet = Pet(
        pet_id=str(uuid4()), tenant_id=tenant_id, owner_id=owner_id, name=body.name,
        species=body.species, breed=body.breed, birth_date=_iso_date(body.birth_date, "birth_date"),
        weight_kg=body.weight_kg, medical_conditions=body.medical_conditions,
        allergies=body.allergies, preferences=body.preferences,
        created_by_actor_id=actor_id, created_at=now, updated_at=now,
    )
    try:
        stored = PET_REPO.create(pet)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Pet profile refused: {exc}") from None
    _pet_audit("pet.profile.created", actor_id, actor_role, tenant_id, stored.pet_id, x_correlation_id)
    return stored.to_read_model()


@app.get("/api/pets")
def list_pets(request: Request, role: str = Depends(require_role)):
    """The session tenant's pets; an owner sees only their own."""
    if role not in PET_READERS:
        raise HTTPException(403, "Not authorized to read pet profiles")
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    owner = actor_id if actor_role == ROLE_OWNER else None
    return [p.to_read_model() for p in PET_REPO.list_for_tenant(tenant_id=tenant_id, owner_id=owner)]


@app.get("/api/pets/{pet_id}")
def get_pet_profile(request: Request, pet_id: str, role: str = Depends(require_role)):
    """AC-FR-02-01/02/03: profile, identifications and medical history.

    History = the profile's lab results and clinical records, plus every
    prescription for the pet read from the prescription store (not copied).
    """
    if role not in PET_READERS:
        raise HTTPException(403, "Not authorized to read pet profiles")
    pet, _actor_id, _role, tenant_id = _pet_or_404(request, pet_id)
    prescriptions = [
        rx.to_read_model()
        for status in (STATUS_ISSUED, STATUS_VET_VERIFIED, STATUS_DISPENSED)
        for rx in PRESCRIPTION_REPO.list_by_status(tenant_id=tenant_id, status=status)
        if rx.pet_id == pet_id
    ]
    return {
        "profile": pet.to_read_model(),
        "identifications": [i.to_read_model() for i in PET_REPO.identifications_for(pet_id, tenant_id=tenant_id)],
        "medical_history": {
            "records": [r.to_read_model() for r in PET_REPO.medical_records_for(pet_id, tenant_id=tenant_id)],
            "prescriptions": sorted(prescriptions, key=lambda r: (r["issued_at"], r["prescription_id"])),
        },
    }


@app.patch("/api/pets/{pet_id}")
def update_pet_profile(
    request: Request,
    pet_id: str,
    body: PetUpdate,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-02-01/02 change (incl. preferences); AC-FR-02-04 audited as the session actor."""
    if role not in {ROLE_OWNER, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Only owners or admins may change pet profiles")
    _pet, actor_id, actor_role, tenant_id = _pet_or_404(request, pet_id)
    changes = body.model_dump(exclude_unset=True)
    if "birth_date" in changes:
        changes["birth_date"] = _iso_date(changes["birth_date"], "birth_date")
    for required in ("name", "species"):
        if required in changes and not (changes[required] or "").strip():
            raise HTTPException(400, f"{required} cannot be empty")
    if not changes:
        raise HTTPException(400, "No changes supplied")
    try:
        pet = PET_REPO.update(pet_id, tenant_id=tenant_id, changes=changes,
                              updated_at=datetime.now(timezone.utc))
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Pet profile change refused: {exc}") from None
    _pet_audit("pet.profile.updated", actor_id, actor_role, tenant_id, pet_id, x_correlation_id)
    return pet.to_read_model()


@app.post("/api/pets/{pet_id}/identifications")
def add_pet_identification(
    request: Request,
    pet_id: str,
    body: PetIdentificationRequest,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-02-03: structured identification (type, value, capture date). Optional."""
    if role not in {ROLE_OWNER, ROLE_VETERINARIAN, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Not authorized to record identification")
    _pet, actor_id, actor_role, tenant_id = _pet_or_404(request, pet_id)
    ident = PetIdentification(
        identification_id=str(uuid4()), pet_id=pet_id, tenant_id=tenant_id, id_type=body.id_type,
        id_value=body.id_value, issuing_scheme=body.issuing_scheme,
        captured_at=_iso_date(body.captured_at, "captured_at"), capture_method=body.capture_method,
        recorded_by_actor_id=actor_id, recorded_at=datetime.now(timezone.utc),
    )
    try:
        stored = PET_REPO.add_identification(ident)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Identification refused: {exc}") from None
    _pet_audit("pet.identification.recorded", actor_id, actor_role, tenant_id, pet_id, x_correlation_id)
    return stored.to_read_model()


@app.post("/api/pets/{pet_id}/medical-records")
def add_pet_medical_record(
    request: Request,
    pet_id: str,
    body: PetMedicalRecordRequest,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-02-02: a lab result or clinical record on the pet's history. Veterinarian only."""
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only veterinarians may record medical history")
    _pet, actor_id, actor_role, tenant_id = _pet_or_404(request, pet_id)
    _require_practitioner_authority(actor_id, tenant_id)  # FR-05 (U10): verified licence at the act
    rec = PetMedicalRecord(
        record_id=str(uuid4()), pet_id=pet_id, tenant_id=tenant_id, record_type=body.record_type,
        title=body.title, detail=body.detail, recorded_by_actor_id=actor_id,
        recorded_at=datetime.now(timezone.utc),
    )
    try:
        stored = PET_REPO.add_medical_record(rec)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Medical record refused: {exc}") from None
    _pet_audit("pet.medical_record.recorded", actor_id, actor_role, tenant_id, pet_id, x_correlation_id)
    return stored.to_read_model()

# ---------------------------------------------------------------------------
# FR-07 · consultation messaging and file sharing (U7)
# ---------------------------------------------------------------------------
MESSAGE_REPO = PERSISTENCE.messages


class MessageRequest(BaseModel):
    model_config = {"extra": "forbid"}

    body: str


def _consultation_participant(request: Request, consultation_id: str):
    """The consultation, if the session actor is one of its two participants, else 404.

    AC-FR-07-01: nothing is visible outside the consultation. 404 (not 403) outside it
    or outside the tenant, so existence is not confirmed to a non-participant.
    """
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    session = _consultation(consultation_id, tenant_id)
    if not session or actor_id not in (session["owner_id"], session["veterinarian_id"]):
        raise HTTPException(404, "Consultation not found")
    return session, actor_id, actor_role, tenant_id


def _render_notification(sender_role: str, consultation_id: str, body: str) -> str:
    return f"New message from your {sender_role} in consultation {consultation_id}: {body[:200]}"


@app.post("/api/consultations/{consultation_id}/messages")
def send_consultation_message(
    consultation_id: str,
    body: MessageRequest,
    request: Request,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    session, actor_id, actor_role, tenant_id = _consultation_participant(request, consultation_id)
    now = datetime.now(timezone.utc)
    msg = ConsultationMessage(message_id=str(uuid4()), tenant_id=tenant_id, consultation_id=consultation_id,
                              sender_id=actor_id, sender_role=actor_role, body=body.body, created_at=now)
    try:
        MESSAGE_REPO.add_message(msg)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Message refused: {exc}") from None
    rendered = _render_notification(actor_role, consultation_id, body.body)
    for recipient in {session["owner_id"], session["veterinarian_id"]} - {actor_id}:
        MESSAGE_REPO.record_delivery(DeliveryRecord(
            record_id=str(uuid4()), tenant_id=tenant_id, message_id=msg.message_id, recipient_id=recipient,
            channel=CHANNEL_IN_APP, attempt_no=1, status=DELIVERED, rendered_body=rendered,
            occurred_at=datetime.now(timezone.utc)))
    _audit(event_name="consultation.message.sent", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="consultation_message", resource_id=msg.message_id,
           action_result="success", correlation_id=x_correlation_id)
    return msg.to_read_model()


@app.get("/api/consultations/{consultation_id}/messages")
def list_consultation_messages(consultation_id: str, request: Request, role: str = Depends(require_role)):
    _session, _a, _r, tenant_id = _consultation_participant(request, consultation_id)
    return [{**m.to_read_model(),
             "attachments": [a.to_read_model() for a in MESSAGE_REPO.attachments_for(m.message_id, tenant_id=tenant_id)]}
            for m in MESSAGE_REPO.messages_for(consultation_id, tenant_id=tenant_id)]


@app.post("/api/consultations/{consultation_id}/messages/{message_id}/attachments")
async def attach_to_consultation_message(
    consultation_id: str,
    message_id: str,
    request: Request,
    file: UploadFile = File(...),
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-07-01/03: an image or lab report, validated for type and size, stored in the
    document store (object store in production), never served inline."""
    _session, actor_id, actor_role, tenant_id = _consultation_participant(request, consultation_id)
    msg = MESSAGE_REPO.get_message(message_id, tenant_id=tenant_id)
    if msg is None or msg.consultation_id != consultation_id or msg.sender_id != actor_id:
        raise HTTPException(404, "Message not found")
    payload = await file.read()
    content_type = file.content_type or ""
    try:
        validate_upload(content_type=content_type, payload=payload)
    except DocumentRejected as exc:
        raise HTTPException(400, f"Attachment refused: {exc}") from None
    key = new_storage_key(tenant_id=tenant_id, prescription_id=f"consultation-{consultation_id}")
    try:
        DOCUMENT_STORE.put(key, payload)
    except ObjectStoreUnavailable as exc:
        raise HTTPException(503, f"Document store unavailable: {exc}") from None
    att = MessageAttachment(attachment_id=str(uuid4()), message_id=message_id, tenant_id=tenant_id,
                            filename=(file.filename or "attachment")[:200], content_type=content_type,
                            byte_size=len(payload), sha256=sha256_hex(payload), storage_key=key,
                            created_at=datetime.now(timezone.utc))
    MESSAGE_REPO.add_attachment(att)
    _audit(event_name="consultation.message.attachment_added", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="consultation_message_attachment", resource_id=att.attachment_id,
           action_result="success", correlation_id=x_correlation_id)
    return att.to_read_model()


@app.get("/api/consultations/{consultation_id}/messages/{message_id}/attachments/{attachment_id}")
def download_consultation_attachment(consultation_id: str, message_id: str, attachment_id: str,
                                     request: Request, role: str = Depends(require_role)):
    _session, _a, _r, tenant_id = _consultation_participant(request, consultation_id)
    msg = MESSAGE_REPO.get_message(message_id, tenant_id=tenant_id)
    att = next((a for a in MESSAGE_REPO.attachments_for(message_id, tenant_id=tenant_id)
                if a.attachment_id == attachment_id), None)
    if msg is None or msg.consultation_id != consultation_id or att is None:
        raise HTTPException(404, "Attachment not found")
    return Response(content=DOCUMENT_STORE.get(att.storage_key), media_type=SERVED_CONTENT_TYPE,
                    headers={"Content-Disposition": f'attachment; filename="{att.attachment_id}"',
                             "X-Content-Type-Options": "nosniff"})


# ---------------------------------------------------------------------------
# FR-13 · real-time multi-location inventory (U8)
# ---------------------------------------------------------------------------
INVENTORY_REPO = PERSISTENCE.inventory
#: Tenant staff who see and handle stock. Owners do not (FR-13 is not customer-facing).
INVENTORY_ROLES = frozenset({ROLE_VETERINARIAN, ROLE_PARTNER_CLINIC_ADMIN})


def _inventory_actor(request: Request):
    actor_id, actor_role = _actor(request)
    if actor_role not in INVENTORY_ROLES:
        raise HTTPException(403, "Inventory is available to tenant staff only")
    return actor_id, actor_role, require_tenant(request)


class LocationRequest(BaseModel):
    model_config = {"extra": "forbid"}

    name: str


class MovementRequest(BaseModel):
    """No actor, role, tenant or supply class: the session and the product registration decide."""
    model_config = {"extra": "forbid"}

    location_id: str
    product_id: str
    batch: str
    quantity_delta: int
    reason: str
    to_location_id: Optional[str] = None
    #: FR-19 (U13): BRD P392 — a RECEIPT records the batch's expiry date (YYYY-MM-DD).
    batch_expiry: Optional[str] = None


@app.post("/api/inventory/locations")
def create_inventory_location(
    body: LocationRequest,
    request: Request,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role, tenant_id = _inventory_actor(request)
    if actor_role != ROLE_PARTNER_CLINIC_ADMIN:
        raise HTTPException(403, "Only a clinic administrator adds a pharmacy location")
    loc = InventoryLocation(location_id=str(uuid4()), tenant_id=tenant_id, name=body.name.strip(),
                            created_at=datetime.now(timezone.utc))
    try:
        INVENTORY_REPO.add_location(loc)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Location refused: {exc}") from None
    _audit(event_name="inventory.location.created", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="inventory_location", resource_id=loc.location_id,
           action_result="success", correlation_id=x_correlation_id)
    return loc.to_read_model()


@app.get("/api/inventory/locations")
def list_inventory_locations(request: Request, role: str = Depends(require_role)):
    _a, _r, tenant_id = _inventory_actor(request)
    return [x.to_read_model() for x in INVENTORY_REPO.locations(tenant_id=tenant_id)]


@app.get("/api/inventory/stock")
def inventory_stock(request: Request, product_id: Optional[str] = None, role: str = Depends(require_role)):
    """AC-FR-13-01: stock per location for every location of the SESSION tenant, derived
    from the ledger at read time (AC-FR-13-02). Polled by /pharmacy/inventory. With
    `product_id`, the inventory check for one product across locations (AC-FR-13-03)."""
    _a, _r, tenant_id = _inventory_actor(request)
    locations = INVENTORY_REPO.locations(tenant_id=tenant_id)
    balances = INVENTORY_REPO.balances(tenant_id=tenant_id, product_id=product_id)
    return {"as_of": datetime.now(timezone.utc).isoformat(),
            "locations": [{**x.to_read_model(),
                           "stock": [b for b in balances if b["location_id"] == x.location_id]}
                          for x in locations]}


@app.post("/api/inventory/movements")
def record_stock_movement(
    body: MovementRequest,
    request: Request,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """Append movements to the ledger. AC-FR-13-04 (MVC-PHARM-001 §5, until counsel L-2):
    POM/RESTRICTED/CONTROLLED stock is handled by a veterinarian with a LIVE practitioner
    authority only; the class is read from product registration, never from the request."""
    actor_id, actor_role, tenant_id = _inventory_actor(request)
    supply_class = INVENTORY_REPO.supply_class_of(body.product_id)
    if supply_class in VETERINARIAN_ONLY:
        try:
            if actor_role != ROLE_VETERINARIAN:
                raise HTTPException(403, detail={"error": "VETERINARIAN_ONLY_SUPPLY_CLASS",
                                                 "supply_class": supply_class})
            _require_practitioner_authority(actor_id, tenant_id)
        except HTTPException:
            _audit(event_name="inventory.movement.refused", actor_id=actor_id, actor_role=actor_role,
                   tenant_id=tenant_id, resource_type="stock_movement", resource_id=body.product_id,
                   action_result="denied", correlation_id=x_correlation_id,
                   reason_code=f"SUPPLY_CLASS_{supply_class}")
            raise
    if body.reason not in REASONS or body.reason in (TRANSFER_IN, SUPPLY):
        raise HTTPException(400, f"reason must be one of {RECEIPT}, {ADJUSTMENT}, {TRANSFER_OUT}")
    expiry = None
    if body.reason == RECEIPT:
        try:
            expiry = datetime.strptime(body.batch_expiry or "", "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(400, {"error": "BATCH_EXPIRY_REQUIRED",
                                      "detail": "a receipt records the batch expiry (YYYY-MM-DD)"}) from None
    now = datetime.now(timezone.utc)

    def mv(location_id, delta, reason, transfer_id=None):
        return StockMovement(movement_id=str(uuid4()), tenant_id=tenant_id, location_id=location_id,
                             product_id=body.product_id, batch=body.batch, quantity_delta=delta, reason=reason,
                             supply_class=supply_class, actor_id=actor_id, actor_role=actor_role,
                             created_at=now, transfer_id=transfer_id,
                             batch_expiry=expiry if reason == RECEIPT else None)

    if body.reason == TRANSFER_OUT:
        if not body.to_location_id or body.to_location_id == body.location_id or body.quantity_delta <= 0:
            raise HTTPException(400, "a transfer names another location and a positive quantity")
        tid = str(uuid4())
        movements = [mv(body.location_id, -body.quantity_delta, TRANSFER_OUT, tid),
                     mv(body.to_location_id, body.quantity_delta, TRANSFER_IN, tid)]
    else:
        if body.reason == RECEIPT and body.quantity_delta <= 0:
            raise HTTPException(400, "a receipt adds a positive quantity")
        movements = [mv(body.location_id, body.quantity_delta, body.reason)]
    try:
        INVENTORY_REPO.record(movements)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Movement refused: {exc}") from None
    for m in movements:
        _audit(event_name="inventory.movement.recorded", actor_id=actor_id, actor_role=actor_role,
               tenant_id=tenant_id, resource_type="stock_movement", resource_id=m.movement_id,
               action_result="success", correlation_id=x_correlation_id,
               reason_code=f"{m.reason}:{m.supply_class}")
    return [m.to_read_model() for m in movements]


class SupplyRequest(BaseModel):
    """No actor, tenant or supply class — the session and the product registration decide."""
    model_config = {"extra": "forbid"}

    location_id: str
    product_id: str
    batch: str
    quantity: int
    prescription_id: Optional[str] = None


@app.post("/api/inventory/supplies")
def supply_stock(
    body: SupplyRequest,
    request: Request,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """FR-14 AC-FR-14-03 (U9): the prescription gate applies by supply class.

    GENERAL / OTC: supplied by tenant staff with NO prescription — being sold in a pharmacy
    is not a reason to demand one. POM / RESTRICTED / CONTROLLED (and any unregistered
    product, AC-FR-04-03): a VET_VERIFIED prescription of the session tenant is required,
    and the act is a dispense by a veterinarian with a live authority (AC-FR-14-02, until
    counsel). The supply is a SUPPLY movement on the FR-13 ledger; the database refuses a
    veterinarian-only SUPPLY that cites no prescription (migration 0042).
    """
    actor_id, actor_role, tenant_id = _inventory_actor(request)
    if body.quantity <= 0:
        raise HTTPException(400, "a supply is a positive quantity")
    supply_class = INVENTORY_REPO.supply_class_of(body.product_id)
    gated = prescription_required(supply_class)

    def refuse(status_code, detail, reason_code):
        _audit(event_name="inventory.supply.refused", actor_id=actor_id, actor_role=actor_role,
               tenant_id=tenant_id, resource_type="stock_movement", resource_id=body.product_id,
               action_result="denied", correlation_id=x_correlation_id, reason_code=reason_code)
        raise HTTPException(status_code, detail)

    rx = None
    if gated:
        if not body.prescription_id:
            refuse(403, {"error": "PRESCRIPTION_REQUIRED", "supply_class": supply_class}, "PRESCRIPTION_REQUIRED")
        if actor_role != ROLE_VETERINARIAN:
            refuse(403, {"error": "VETERINARIAN_ONLY_SUPPLY_CLASS", "supply_class": supply_class},
                   f"SUPPLY_CLASS_{supply_class}")
        try:
            _require_practitioner_authority(actor_id, tenant_id)
        except HTTPException as exc:
            refuse(403, exc.detail, "PRACTITIONER_AUTHORITY_REQUIRED")
        rx = PRESCRIPTION_REPO.get(body.prescription_id, tenant_id=tenant_id)
        if rx is None:
            refuse(404, "Prescription not found", "PRESCRIPTION_NOT_FOUND")
        if rx.status != STATUS_VET_VERIFIED:
            refuse(409, f"Prescription is {rx.status}; only a VET_VERIFIED prescription can be supplied",
                   "PRESCRIPTION_NOT_VERIFIED")
    movement = StockMovement(movement_id=str(uuid4()), tenant_id=tenant_id, location_id=body.location_id,
                             product_id=body.product_id, batch=body.batch, quantity_delta=-body.quantity,
                             reason=SUPPLY, supply_class=supply_class, actor_id=actor_id, actor_role=actor_role,
                             created_at=datetime.now(timezone.utc),
                             prescription_id=rx.prescription_id if rx is not None else None)
    try:
        INVENTORY_REPO.record([movement])
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Supply refused: {exc}") from None
    if rx is not None:
        try:
            PRESCRIPTION_REPO.transition(rx.prescription_id, tenant_id=tenant_id, to_status=STATUS_DISPENSED,
                                         actor_id=actor_id, actor_role=actor_role)
        except TransitionDenied as exc:
            # Lost a race with another dispense: return the stock with a compensating movement
            # (the ledger is never rewritten) and refuse.
            INVENTORY_REPO.record([StockMovement(
                movement_id=str(uuid4()), tenant_id=tenant_id, location_id=body.location_id,
                product_id=body.product_id, batch=body.batch, quantity_delta=body.quantity, reason=ADJUSTMENT,
                supply_class=supply_class, actor_id=actor_id, actor_role=actor_role,
                created_at=datetime.now(timezone.utc), prescription_id=rx.prescription_id)])
            refuse(409, f"Cannot dispense — {exc}", "TRANSITION_NOT_ALLOWED")
        _audit(event_name="prescription.dispensed", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
               resource_type="prescription", resource_id=rx.prescription_id, action_result="success",
               correlation_id=x_correlation_id, reason_code=f"supply:{movement.movement_id}")
    _audit(event_name="inventory.movement.recorded", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="stock_movement", resource_id=movement.movement_id,
           action_result="success", correlation_id=x_correlation_id, reason_code=f"{SUPPLY}:{supply_class}")
    return {**movement.to_read_model(), "prescription_required": gated}


# ---------------------------------------------------------------------------
# FR-16 · temperature-controlled delivery tracking (U12)
# ---------------------------------------------------------------------------
DELIVERY_REPO = PERSISTENCE.deliveries


def _delivery_view(d, tenant_id: str) -> dict:
    readings = DELIVERY_REPO.readings(d.delivery_id, tenant_id=tenant_id)
    done = DELIVERY_REPO.completion_of(d.delivery_id, tenant_id=tenant_id)
    return {"delivery_id": d.delivery_id, "owner_id": d.owner_id, "product_id": d.product_id,
            "cold_chain": d.cold_chain, "temp_min_c": d.temp_min_c, "temp_max_c": d.temp_max_c,
            "status": dlv.DELIVERED if done else dlv.IN_TRANSIT, "created_at": d.created_at.isoformat(),
            "completed_at": done.completed_at.isoformat() if done else None,
            "temperature_log": [{"recorded_at": r.recorded_at.isoformat(), "celsius": r.celsius, "source": r.source,
                                 "out_of_range": r.out_of_range} for r in readings]}


def _delivery_for(request: Request, delivery_id: str):
    """(delivery, actor_id, actor_role, tenant_id): staff of the tenant, or the delivery's owner; else 404."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    d = DELIVERY_REPO.get(delivery_id, tenant_id=tenant_id)
    if d is None or (actor_role not in INVENTORY_ROLES and actor_id != d.owner_id):
        raise HTTPException(404, "Delivery not found")
    return d, actor_id, actor_role, tenant_id


class DeliveryRequest(BaseModel):
    model_config = {"extra": "forbid"}

    owner_id: str
    product_id: str


@app.post("/api/deliveries")
def create_delivery(body: DeliveryRequest, request: Request, role: str = Depends(require_role),
                    x_correlation_id: str = Header(default_factory=lambda: str(uuid4()))):
    """Tenant staff open a delivery to an owner of the tenant. The temperature range comes from the
    product's registration (BRD P393), never from the request."""
    actor_id, actor_role, tenant_id = _inventory_actor(request)
    ident = PERSISTENCE.identities.get_by_user_id(body.owner_id)
    if ident is None or ident.tenant_id != tenant_id or ident.role != ROLE_OWNER:
        raise HTTPException(400, "The recipient is not an owner of this tenant")
    rng = INVENTORY_REPO.storage_range_of(body.product_id)
    d = dlv.Delivery(delivery_id=str(uuid4()), tenant_id=tenant_id, owner_id=body.owner_id, product_id=body.product_id,
                     created_by_actor_id=actor_id, created_at=datetime.now(timezone.utc),
                     temp_min_c=rng[0] if rng else None, temp_max_c=rng[1] if rng else None)
    DELIVERY_REPO.create(d)
    _audit(event_name="delivery.created", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="delivery", resource_id=d.delivery_id, action_result="success",
           correlation_id=x_correlation_id, reason_code="COLD_CHAIN" if d.cold_chain else "AMBIENT")
    return _delivery_view(d, tenant_id)


class ReadingRequest(BaseModel):
    model_config = {"extra": "forbid"}

    recorded_at: Optional[str] = None
    celsius: Optional[float] = None


@app.post("/api/deliveries/{delivery_id}/readings")
def record_temperature_reading(delivery_id: str, body: ReadingRequest, request: Request,
                               role: str = Depends(require_role),
                               x_correlation_id: str = Header(default_factory=lambda: str(uuid4()))):
    """AC-FR-16-01/04: append a reading to the delivery's log. An out-of-range reading is kept,
    raises a pharmacy alert (same transaction) and is audited."""
    d, actor_id, actor_role, tenant_id = _delivery_for(request, delivery_id)
    if actor_role not in INVENTORY_ROLES:
        raise HTTPException(403, "Readings are recorded by tenant staff or the logistics partner")
    try:
        when, celsius = dlv.normalise_partner_reading(body.model_dump())
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Reading refused: {exc}") from None
    reading = dlv.TemperatureReading(reading_id=str(uuid4()), delivery_id=delivery_id, tenant_id=tenant_id,
                                     recorded_at=when, celsius=celsius, source=dlv.SOURCE_STAFF, recorded_by=actor_id,
                                     out_of_range=dlv.out_of_range(d, celsius))
    alert = None if not reading.out_of_range else dlv.DeliveryAlert(
        alert_id=str(uuid4()), delivery_id=delivery_id, tenant_id=tenant_id, reading_id=reading.reading_id,
        kind=dlv.ALERT_OUT_OF_RANGE, raised_at=datetime.now(timezone.utc))
    try:
        DELIVERY_REPO.add_reading(reading, alert)
    except RepositoryDenied as exc:
        raise HTTPException(409, f"Reading refused: {exc}") from None
    _audit(event_name="delivery.temperature.recorded", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="delivery", resource_id=delivery_id, action_result="success", correlation_id=x_correlation_id,
           reason_code=f"{celsius}C")
    if alert is not None:
        _audit(event_name="delivery.temperature.alert", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
               resource_type="delivery_alert", resource_id=alert.alert_id, action_result="success",
               correlation_id=x_correlation_id,
               reason_code=f"{dlv.ALERT_OUT_OF_RANGE}:{celsius}C:[{d.temp_min_c},{d.temp_max_c}]")
    return {**_delivery_view(d, tenant_id), "alert_raised": alert is not None}


@app.post("/api/deliveries/{delivery_id}/complete")
def complete_delivery(delivery_id: str, request: Request, role: str = Depends(require_role),
                      x_correlation_id: str = Header(default_factory=lambda: str(uuid4()))):
    """A temperature-controlled delivery never completes without a temperature log (AC-FR-16-01)."""
    d, actor_id, actor_role, tenant_id = _delivery_for(request, delivery_id)
    if actor_role not in INVENTORY_ROLES:
        raise HTTPException(403, "Deliveries are completed by tenant staff")
    if d.cold_chain and not DELIVERY_REPO.readings(delivery_id, tenant_id=tenant_id):
        raise HTTPException(409, "A temperature-controlled delivery cannot complete without a temperature log")
    try:
        DELIVERY_REPO.complete(dlv.DeliveryCompletion(delivery_id=delivery_id, tenant_id=tenant_id,
                                                      completed_by_actor_id=actor_id,
                                                      completed_at=datetime.now(timezone.utc)))
    except RepositoryDenied as exc:
        raise HTTPException(409, f"Completion refused: {exc}") from None
    _audit(event_name="delivery.completed", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="delivery", resource_id=delivery_id, action_result="success", correlation_id=x_correlation_id)
    return _delivery_view(d, tenant_id)


@app.get("/api/deliveries")
def list_deliveries(request: Request, role: str = Depends(require_role)):
    """An owner sees their own deliveries with the temperature log; tenant staff see the tenant's."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    return [_delivery_view(d, tenant_id) for d in DELIVERY_REPO.for_tenant(tenant_id)
            if actor_role in INVENTORY_ROLES or d.owner_id == actor_id]


@app.get("/api/deliveries/alerts")
def delivery_alerts(request: Request, role: str = Depends(require_role)):
    """The pharmacy's alert list: out-of-range readings in the session tenant."""
    _a, _r, tenant_id = _inventory_actor(request)
    return [{"alert_id": a.alert_id, "delivery_id": a.delivery_id, "reading_id": a.reading_id, "kind": a.kind,
             "raised_at": a.raised_at.isoformat()} for a in DELIVERY_REPO.alerts(tenant_id=tenant_id)]


@app.get("/api/deliveries/{delivery_id}")
def get_delivery(delivery_id: str, request: Request, role: str = Depends(require_role)):
    d, _a, _r, tenant_id = _delivery_for(request, delivery_id)
    return _delivery_view(d, tenant_id)


# ---------------------------------------------------------------------------
# FR-19 · batch recall resolution and owner notification (U13)
# ---------------------------------------------------------------------------
import recalls as rcl  # noqa: E402

RECALL_REPO = PERSISTENCE.recalls


def _recall_resolution(r) -> dict:
    """AC-FR-19-02: resolve through stored relationships of the recall's tenant only."""
    return rcl.resolve(
        r, INVENTORY_REPO.supplies_of_batch(tenant_id=r.tenant_id, product_id=r.product_id, batch=r.batch),
        prescription_of=lambda pid: PRESCRIPTION_REPO.get(pid, tenant_id=r.tenant_id),
        pet_of=lambda pet_id: PET_REPO.get(pet_id, tenant_id=r.tenant_id))


class RecallRequest(BaseModel):
    model_config = {"extra": "forbid"}

    product_id: str
    batch: str
    reason: str


@app.post("/api/recalls")
def create_recall(body: RecallRequest, request: Request, role: str = Depends(require_role),
                  x_correlation_id: str = Header(default_factory=lambda: str(uuid4()))):
    """Tenant staff record a recall of (product, batch). It resolves to every affected dispense and owner
    through stored relationships, notifies each resolved owner (one notice per affected dispense, in the
    same transaction as the recall), and returns both partitions with the completeness statement."""
    actor_id, actor_role, tenant_id = _inventory_actor(request)
    try:
        product, batch, _ = rcl.normalise_sfda_recall(body.model_dump())
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Recall refused: {exc}") from None
    if not body.reason.strip():
        raise HTTPException(400, "Recall refused: a recall states its reason")
    now = datetime.now(timezone.utc)
    r = rcl.Recall(recall_id=str(uuid4()), tenant_id=tenant_id, product_id=product, batch=batch,
                   reason=body.reason.strip(), source=rcl.SOURCE_STAFF, initiated_by_actor_id=actor_id, created_at=now)
    res = _recall_resolution(r)
    notices = [rcl.RecallNotification(
        notification_id=str(uuid4()), recall_id=r.recall_id, tenant_id=tenant_id, owner_id=x["owner_id"],
        movement_id=x["movement_id"], created_at=now,
        rendered_body=(f"Recall: {product} batch {batch} dispensed for your pet ({x['pet_id']}) under prescription "
                       f"{x['prescription_id']} has been recalled. Reason: {r.reason}. Please contact your clinic."))
        for x in res["resolved"]]
    RECALL_REPO.create(r, notices)
    _audit(event_name="recall.created", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="recall", resource_id=r.recall_id, action_result="success", correlation_id=x_correlation_id,
           reason_code=f"{product}:{batch}:resolved={len(res['resolved'])}:indeterminate={len(res['indeterminate'])}")
    for n in notices:
        _audit(event_name="recall.owner_notified", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
               resource_type="recall_notification", resource_id=n.notification_id, action_result="success",
               correlation_id=x_correlation_id, reason_code=f"owner:{n.owner_id}")
    return {**res, "notified_owners": sorted({n.owner_id for n in notices})}


@app.get("/api/recalls/{recall_id}")
def get_recall(recall_id: str, request: Request, role: str = Depends(require_role)):
    _a, _r, tenant_id = _inventory_actor(request)
    r = RECALL_REPO.get(recall_id, tenant_id=tenant_id)
    if r is None:
        raise HTTPException(404, "Recall not found")
    return {**_recall_resolution(r),
            "notified_owners": sorted({n.owner_id for n in RECALL_REPO.notifications(recall_id, tenant_id=tenant_id)})}


@app.get("/api/me/recall-notices")
def my_recall_notices(request: Request, role: str = Depends(require_role)):
    """The owner's recall notices (AC-FR-19-02: each affected owner is notified)."""
    actor_id, _r = _actor(request)
    tenant_id = require_tenant(request)
    return [{"notification_id": n.notification_id, "recall_id": n.recall_id, "body": n.rendered_body,
             "created_at": n.created_at.isoformat()} for n in RECALL_REPO.notices_for_owner(actor_id, tenant_id=tenant_id)]


# ---------------------------------------------------------------------------
# FR-20 · cash on delivery with digital receipting (U14)
# ---------------------------------------------------------------------------
import orders as ordr  # noqa: E402

ORDER_REPO = PERSISTENCE.orders


class PriceRequest(BaseModel):
    model_config = {"extra": "forbid"}

    product_id: str
    unit_price_halalas: int


@app.post("/api/catalog/prices")
def set_price(body: PriceRequest, request: Request, role: str = Depends(require_role),
              x_correlation_id: str = Header(default_factory=lambda: str(uuid4()))):
    """A clinic administrator sets the tenant's price for a product (append-only history, latest wins)."""
    actor_id, actor_role, tenant_id = _inventory_actor(request)
    if actor_role != ROLE_PARTNER_CLINIC_ADMIN:
        raise HTTPException(403, "Only a clinic administrator sets prices")
    try:
        ORDER_REPO.set_price(ordr.PriceEntry(tenant_id=tenant_id, product_id=body.product_id,
                                             unit_price_halalas=body.unit_price_halalas, set_by_actor_id=actor_id,
                                             set_at=datetime.now(timezone.utc)))
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Price refused: {exc}") from None
    _audit(event_name="catalog.price.set", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="tenant_price", resource_id=body.product_id, action_result="success",
           correlation_id=x_correlation_id, reason_code=f"{body.unit_price_halalas}")
    return {"product_id": body.product_id, "unit_price_halalas": body.unit_price_halalas}


@app.get("/api/catalog/prices")
def list_prices(request: Request, role: str = Depends(require_role)):
    """The session tenant's orderable products: priced and GENERAL/OTC (eligible for an order)."""
    tenant_id = require_tenant(request)
    return [{"product_id": pid, "unit_price_halalas": price, "supply_class": INVENTORY_REPO.supply_class_of(pid)}
            for pid, price in sorted(ORDER_REPO.prices(tenant_id=tenant_id).items())
            if not prescription_required(INVENTORY_REPO.supply_class_of(pid))]


class OrderLineRequest(BaseModel):
    model_config = {"extra": "forbid"}

    product_id: str
    quantity: int


class OrderRequest(BaseModel):
    """No price, owner or tenant: the tenant's price list and the session decide."""
    model_config = {"extra": "forbid"}

    lines: list[OrderLineRequest]
    payment_method: str


def _order_view(o, tenant_id: str) -> dict:
    col = ORDER_REPO.collection_of(o.order_id, tenant_id=tenant_id)
    rec = ORDER_REPO.receipt_of(o.order_id, tenant_id=tenant_id)
    return {"order_id": o.order_id, "owner_id": o.owner_id, "payment_method": o.payment_method,
            "status": ordr.DELIVERED if col else ordr.PLACED, "paid": col is not None,
            "total_halalas": o.total_halalas, "created_at": o.created_at.isoformat(),
            "lines": [{"product_id": l.product_id, "quantity": l.quantity, "unit_price_halalas": l.unit_price_halalas}
                      for l in o.lines],
            "receipt": None if rec is None else {"receipt_id": rec.receipt_id, "language": rec.language,
                                                 "rendered": rec.rendered, "issued_at": rec.issued_at.isoformat()}}


@app.post("/api/orders")
def place_order(body: OrderRequest, request: Request, role: str = Depends(require_role),
                x_correlation_id: str = Header(default_factory=lambda: str(uuid4()))):
    """AC-FR-20-01: an owner places an order and chooses cash on delivery; the order records COD."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    if actor_role != ROLE_OWNER:
        raise HTTPException(403, "Orders are placed by owners")
    if body.payment_method not in ordr.PAYMENT_METHODS:
        raise HTTPException(400, f"payment_method must be one of {list(ordr.PAYMENT_METHODS)}")
    if not body.lines or len(body.lines) > ordr.MAX_LINES:
        raise HTTPException(400, f"an order has 1..{ordr.MAX_LINES} lines")
    lines = []
    for l in body.lines:
        if not 0 < l.quantity <= ordr.MAX_QTY:
            raise HTTPException(400, f"quantity must be 1..{ordr.MAX_QTY}")
        if prescription_required(INVENTORY_REPO.supply_class_of(l.product_id)):
            raise HTTPException(409, {"error": "PRESCRIPTION_PRODUCT_NOT_ORDERABLE", "product_id": l.product_id,
                                      "detail": "POM/RESTRICTED/CONTROLLED products are dispensed against a prescription"})
        price = ORDER_REPO.price_of(l.product_id, tenant_id=tenant_id)
        if price is None:
            raise HTTPException(400, {"error": "PRODUCT_NOT_PRICED", "product_id": l.product_id})
        lines.append(ordr.OrderLine(product_id=l.product_id, quantity=l.quantity, unit_price_halalas=price))
    o = ordr.Order(order_id=str(uuid4()), tenant_id=tenant_id, owner_id=actor_id, payment_method=body.payment_method,
                   lines=tuple(lines), created_at=datetime.now(timezone.utc))
    ORDER_REPO.create(o)
    _audit(event_name="order.placed", actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
           resource_type="customer_order", resource_id=o.order_id, action_result="success",
           correlation_id=x_correlation_id, reason_code=f"{o.payment_method}:{o.total_halalas}")
    return _order_view(o, tenant_id)


class DeliverOrderRequest(BaseModel):
    """The collection confirmation (AC-FR-20-03) and the stock the order leaves from (FR-13 ledger)."""
    model_config = {"extra": "forbid"}

    location_id: str
    batches: dict[str, str]
    collected_amount_halalas: int
    collection_reference: str


@app.post("/api/orders/{order_id}/deliver")
def deliver_order(order_id: str, body: DeliverOrderRequest, request: Request, role: str = Depends(require_role),
                  x_correlation_id: str = Header(default_factory=lambda: str(uuid4()))):
    """Tenant staff record delivery: the stock leaves as SUPPLY movements, the cash collection is confirmed
    for the exact total, and the digital receipt is issued in the owner's language — collection and
    receipt in one transaction. An order is never marked paid without the confirmation."""
    actor_id, actor_role, tenant_id = _inventory_actor(request)
    o = ORDER_REPO.get(order_id, tenant_id=tenant_id)
    if o is None:
        raise HTTPException(404, "Order not found")
    if ORDER_REPO.collection_of(order_id, tenant_id=tenant_id) is not None:
        raise HTTPException(409, "The order is already delivered")
    if body.collected_amount_halalas != o.total_halalas or not body.collection_reference.strip():
        raise HTTPException(409, {"error": "COLLECTION_NOT_CONFIRMED", "total_halalas": o.total_halalas,
                                  "detail": "delivery needs a collection confirmation of the exact total, with a reference"})
    if set(body.batches) != {l.product_id for l in o.lines}:
        raise HTTPException(400, "name the batch supplied for every product of the order")
    now = datetime.now(timezone.utc)
    moves = [StockMovement(movement_id=str(uuid4()), tenant_id=tenant_id, location_id=body.location_id,
                           product_id=l.product_id, batch=body.batches[l.product_id], quantity_delta=-l.quantity,
                           reason=SUPPLY, supply_class=INVENTORY_REPO.supply_class_of(l.product_id), actor_id=actor_id,
                           actor_role=actor_role, created_at=now) for l in o.lines]
    try:
        INVENTORY_REPO.record(moves)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Delivery refused: {exc}") from None
    language = PREFERENCE_REPO.get_language(o.owner_id) or DEFAULT_LANGUAGE
    collection = ordr.Collection(order_id=order_id, tenant_id=tenant_id, amount_halalas=body.collected_amount_halalas,
                                 reference=body.collection_reference.strip(), source=ordr.SOURCE_STAFF,
                                 confirmed_by=actor_id, confirmed_at=now)
    receipt = ordr.Receipt(receipt_id=str(uuid4()), order_id=order_id, tenant_id=tenant_id, owner_id=o.owner_id,
                           language=language, rendered=ordr.render_receipt(o, collection, language, now),
                           total_halalas=o.total_halalas, issued_at=now)
    try:
        ORDER_REPO.deliver(collection, receipt)
    except RepositoryDenied as exc:
        INVENTORY_REPO.record([dataclasses.replace(m, movement_id=str(uuid4()), quantity_delta=-m.quantity_delta,
                                                   reason=ADJUSTMENT) for m in moves])  # return the stock
        raise HTTPException(409, f"Delivery refused: {exc}") from None
    for event, rid in (("order.cash_collected", order_id), ("order.delivered", order_id),
                       ("order.receipt_issued", receipt.receipt_id)):
        _audit(event_name=event, actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,
               resource_type="order_receipt" if event == "order.receipt_issued" else "customer_order", resource_id=rid,
               action_result="success", correlation_id=x_correlation_id,
               reason_code=f"{collection.source}:{collection.reference}" if event == "order.cash_collected" else None)
    return _order_view(o, tenant_id)


@app.get("/api/orders")
def list_orders(request: Request, role: str = Depends(require_role)):
    """An owner sees their own orders with receipts; tenant staff see the tenant's."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    return [_order_view(o, tenant_id) for o in ORDER_REPO.for_tenant(tenant_id)
            if actor_role in INVENTORY_ROLES or o.owner_id == actor_id]


@app.get("/api/orders/{order_id}/receipt")
def get_order_receipt(order_id: str, request: Request, role: str = Depends(require_role)):
    """AC-FR-20-02: the receipt is retrievable later, by the order's owner or tenant staff."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    o = ORDER_REPO.get(order_id, tenant_id=tenant_id)
    if o is None or (actor_role not in INVENTORY_ROLES and o.owner_id != actor_id):
        raise HTTPException(404, "Order not found")
    rec = ORDER_REPO.receipt_of(order_id, tenant_id=tenant_id)
    if rec is None:
        raise HTTPException(404, "No receipt: the order is not delivered")
    return {"receipt_id": rec.receipt_id, "order_id": order_id, "language": rec.language, "rendered": rec.rendered,
            "total_halalas": rec.total_halalas, "issued_at": rec.issued_at.isoformat()}


# ---------------------------------------------------------------------------
# FR-01 · practitioner authority administration (U5). Never self-service.
# ---------------------------------------------------------------------------
class AuthorityGrantRequest(BaseModel):
    model_config = {"extra": "forbid"}

    professional_class: str = CLASS_VETERINARIAN
    licence_ref: str
    effective_from: Optional[str] = None
    expires_at: Optional[str] = None


def _iso_datetime(value: Optional[str], field_name: str):
    if value is None:
        return None
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(400, f"{field_name} must be an ISO datetime") from None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


@app.post("/api/admin/practitioners/{user_id}/authority")
def grant_practitioner_authority(
    user_id: str,
    body: AuthorityGrantRequest,
    request: Request,
    role: str = Depends(require_admin),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """platform_admin records an authority attribute against another natural person."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    if user_id == actor_id:
        raise HTTPException(403, "Authority attributes are never self-granted")
    target = PERSISTENCE.identities.get_by_user_id(user_id)
    if target is None or target.tenant_id != tenant_id or target.role != ROLE_VETERINARIAN:
        raise HTTPException(404, "No veterinarian with that id in this tenant")
    now = datetime.now(timezone.utc)
    grant = PractitionerAuthorityGrant(
        grant_id=str(uuid4()), tenant_id=tenant_id, actor_id=user_id,
        professional_class=body.professional_class, licence_ref=body.licence_ref,
        effective_from=_iso_datetime(body.effective_from, "effective_from") or now,
        expires_at=_iso_datetime(body.expires_at, "expires_at"),
        granted_by_actor_id=actor_id, granted_at=now)
    try:
        stored = PRACTITIONER_REPO.grant(grant)
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Authority grant refused: {exc}") from None
    _audit(event_name="practitioner.authority.granted", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="practitioner_authority", resource_id=stored.grant_id,
           action_result="success", correlation_id=x_correlation_id, reason_code=f"subject:{user_id}")
    return stored.to_read_model()


@app.post("/api/admin/practitioners/authority/{grant_id}/revoke")
def revoke_practitioner_authority(
    grant_id: str,
    request: Request,
    role: str = Depends(require_admin),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    try:
        g = PRACTITIONER_REPO.revoke(grant_id, tenant_id=tenant_id, at=datetime.now(timezone.utc), by=actor_id)
    except RepositoryDenied:
        raise HTTPException(404, "No unrevoked grant with that id in this tenant") from None
    _audit(event_name="practitioner.authority.revoked", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="practitioner_authority", resource_id=grant_id,
           action_result="success", correlation_id=x_correlation_id, reason_code=f"subject:{g.actor_id}")
    return g.to_read_model()


# ---------------------------------------------------------------------------
# FR-05 · veterinarian licence verification (U10)
# ---------------------------------------------------------------------------
LICENCE_REPO = PERSISTENCE.licences
#: The served app has no live licensing-authority adapter (EXTERNAL:VET_LICENSING_AUTHORITY).
LICENSING_PORT = licences.UnconfiguredLicensingAdapter()


def _licence_view(lic) -> dict:
    v = LICENCE_REPO.verification_of(lic.licence_id)
    return {"licence_id": lic.licence_id, "actor_id": lic.actor_id, "licence_number": lic.licence_number,
            "issuing_authority": lic.issuing_authority, "expires_on": lic.expires_on.isoformat(),
            "submitted_at": lic.submitted_at.isoformat(),
            "status": licences.VERIFIED if v else licences.SUBMITTED,
            "verification": None if v is None else {
                "verified_by_actor_id": v.verified_by_actor_id, "verified_at": v.verified_at.isoformat(),
                "method": v.method, "basis": v.basis, "grant_id": v.grant_id}}


def _tenant_vet(user_id: str, tenant_id: str):
    target = PERSISTENCE.identities.get_by_user_id(user_id)
    if target is None or target.tenant_id != tenant_id or target.role != ROLE_VETERINARIAN:
        return None
    return target


@app.get("/api/admin/practitioners/licences")
def list_vet_licences(request: Request, role: str = Depends(require_admin)):
    """Licences of the veterinarians of the SESSION tenant, with their verification state."""
    tenant_id = require_tenant(request)
    return [_licence_view(lic) for lic in LICENCE_REPO.all() if _tenant_vet(lic.actor_id, tenant_id) is not None]


class LicenceVerificationRequest(BaseModel):
    model_config = {"extra": "forbid"}

    method: str
    basis: str = ""


@app.post("/api/admin/practitioners/licences/{licence_id}/verify")
def verify_vet_licence(
    licence_id: str,
    body: LicenceVerificationRequest,
    request: Request,
    role: str = Depends(require_admin),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-05-01/02: verify a submitted licence. MANUAL_STAFF names what the session admin
    checked it against; AUTHORITY_LOOKUP asks the licensing-authority port and accepts only an
    explicit VALID. Verification mints the practitioner authority grant that expires with the
    licence (re-checked at every clinical act) and is audited with the session actor."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    lic = LICENCE_REPO.get(licence_id)
    if lic is None or _tenant_vet(lic.actor_id, tenant_id) is None:
        raise HTTPException(404, "No licence with that id for a veterinarian of this tenant")
    if lic.actor_id == actor_id:
        raise HTTPException(403, "A licence is never self-verified")
    if LICENCE_REPO.verification_of(licence_id) is not None:
        raise HTTPException(409, "The licence is already verified")
    now = datetime.now(timezone.utc)
    if lic.expires_at() <= now:
        raise HTTPException(409, f"The licence expired on {lic.expires_on.isoformat()}")
    if body.method == licences.MANUAL_STAFF:
        if not body.basis.strip():
            raise HTTPException(400, "A manual verification states what the licence was checked against")
        basis = body.basis.strip()[:500]
    elif body.method == licences.AUTHORITY_LOOKUP:
        try:
            result = licences.normalise_lookup(LICENSING_PORT.lookup(
                licence_number=lic.licence_number, issuing_authority=lic.issuing_authority))
        except Exception:
            result = licences.LookupResult(licences.LOOKUP_UNAVAILABLE, "the licensing authority did not answer")
        if not result.verified:
            _audit(event_name="practitioner.licence.verification_refused", actor_id=actor_id, actor_role=actor_role,
                   tenant_id=tenant_id, resource_type="vet_licence", resource_id=licence_id, action_result="denied",
                   correlation_id=x_correlation_id, reason_code=f"LOOKUP_{result.status}")
            raise HTTPException(409, detail={"error": "LICENCE_NOT_VERIFIED", "lookup": result.status,
                                             "detail": result.detail})
        basis = f"{lic.issuing_authority} lookup: {result.status} {result.detail}".strip()
    else:
        raise HTTPException(400, f"method must be {licences.MANUAL_STAFF} or {licences.AUTHORITY_LOOKUP}")
    grant = PRACTITIONER_REPO.grant(PractitionerAuthorityGrant(
        grant_id=str(uuid4()), tenant_id=tenant_id, actor_id=lic.actor_id, professional_class=CLASS_VETERINARIAN,
        licence_ref=f"{lic.issuing_authority}:{lic.licence_number}", effective_from=now,
        expires_at=lic.expires_at(), granted_by_actor_id=actor_id, granted_at=now))
    LICENCE_REPO.record_verification(licences.LicenceVerification(
        verification_id=str(uuid4()), licence_id=licence_id, tenant_id=tenant_id, verified_by_actor_id=actor_id,
        verified_at=now, method=body.method, basis=basis, grant_id=grant.grant_id))
    _audit(event_name="practitioner.licence.verified", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="vet_licence", resource_id=licence_id, action_result="success",
           correlation_id=x_correlation_id, reason_code=f"{body.method}:grant:{grant.grant_id}")
    return _licence_view(lic)


@app.get("/api/practitioners/me/licence")
def my_vet_licence(request: Request, role: str = Depends(require_role)):
    actor_id, _r = _actor(request)
    return [_licence_view(lic) for lic in LICENCE_REPO.for_actor(actor_id)]


@app.get("/api/practitioners/me/authority")
def my_practitioner_authority(request: Request, role: str = Depends(require_role)):
    """The caller's own grants and whether one is in force now."""
    actor_id, _r = _actor(request)
    tenant_id = require_tenant(request)
    grants = PRACTITIONER_REPO.grants_for(actor_id, tenant_id=tenant_id)
    live, reason = practitioner_evaluate(grants, professional_class=CLASS_VETERINARIAN,
                                         when=datetime.now(timezone.utc))
    return {"in_force": live is not None, "reason": reason,
            "grants": [g.to_read_model() for g in grants]}


# ---------------------------------------------------------------------------
# FR-09 · language preference that survives a new session (U3)
# ---------------------------------------------------------------------------
PREFERENCE_REPO = PERSISTENCE.preferences


class LanguagePreference(BaseModel):
    model_config = {"extra": "forbid"}

    language: str


@app.get("/api/me/preferences/language")
def get_language_preference(request: Request, role: str = Depends(require_role)):
    """AC-FR-09-02: the caller's stored language, or Arabic (FR-09 primary) by default."""
    actor_id, _actor_role = _actor(request)
    stored = PREFERENCE_REPO.get_language(actor_id)
    return {"language": stored or DEFAULT_LANGUAGE, "source": "stored" if stored else "default"}


@app.put("/api/me/preferences/language")
def set_language_preference(
    request: Request,
    body: LanguagePreference,
    role: str = Depends(require_role),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    """AC-FR-09-02: persist the caller's own language choice; audited as the session actor."""
    actor_id, actor_role = _actor(request)
    tenant_id = require_tenant(request)
    try:
        language = PREFERENCE_REPO.set_language(actor_id, tenant_id=tenant_id, language=body.language,
                                                at=datetime.now(timezone.utc))
    except RepositoryDenied as exc:
        raise HTTPException(400, f"Language preference refused: {exc}") from None
    _audit(event_name="user.preference.language.set", actor_id=actor_id, actor_role=actor_role,
           tenant_id=tenant_id, resource_type="user_preference", resource_id=actor_id,
           action_result="success", correlation_id=x_correlation_id)
    return {"language": language, "source": "stored"}


# ---------------------------------------------------------------------------
# Governance status
# ---------------------------------------------------------------------------
def _audit_chain_active() -> bool:
    """Whether a governed, verifiable audit chain is wired into THIS serving path.

    Computed, never asserted. The chain algorithm exists at
    petcare_execution/FND/security/audit_chain.py (canonical-JSON SHA-256,
    compute_event_hash + verify_hash_chain) but is not imported here, no
    prev_hash/event_hash is persisted, and the audit log in this process is an
    in-memory list. Until W0-G wires it, the honest answer is False.

    W0-G replaces this with a real verification against persisted chain state.
    """
    events = AUDIT_REPO.all_events()
    for ev in events:
        if not (ev.get("prev_hash") and ev.get("event_hash")):
            return False
    return bool(events)


def _audit_chain_persisted() -> bool:
    """Whether the chain SURVIVES this process.

    COMPUTED from the configured store, never asserted. W0-G closed this by
    moving the log behind a repository, so the answer is now true when the
    process is configured for a durable store and false when it is not — and it
    changes with configuration rather than with a code edit.

    Still reported as its own field, separately from `audit_chain_active`.
    Computing a chain over a volatile store is a real control against tampering
    and a real non-control against loss, and W0-E's discipline is that the
    service must not blur the two. Persistence has not made them the same
    property; it has made one of them true.
    """
    return bool(getattr(AUDIT_REPO, "durable", False))


@app.get("/api/governance/status")
def governance_status():
    """Governance posture, COMPUTED from live state.

    MVC-INC-ATTEST-001 (W0-E): this endpoint previously returned hard-coded
    literals asserting audit_chain_active=true and fail_closed=true while
    nothing evaluated either claim. An absent control is a gap; an absent
    control that reports itself present is a misrepresentation, and would have
    satisfied a reviewer who queried it.

    Every field below is either computed or reported as not-established. No
    field may be reintroduced as a constant.
    """
    chain_active = _audit_chain_active()
    return {
        # Computed from the serving path, not asserted.
        "audit_chain_active": chain_active,
        "audit_chain_verification": (
            ("VERIFIED" if verify_audit_chain()["ok"] else "BROKEN")
            if chain_active
            else "NOT_WIRED_INTO_SERVING_PATH"
        ),
        # W0-G computes the chain; it does not persist it. Separate fields, so
        # neither can be mistaken for the other.
        "audit_chain_persisted": _audit_chain_persisted(),
        # COMPUTED, not asserted. This was the fixed string "IN_PROCESS_ONLY …
        # persistence is W0-F", which was true when written and becomes a FALSE
        # claim the moment the service is configured for a durable store — the
        # MVC-INC-ATTEST-001 defect inverted: a service misreporting a control it
        # now has. A literal that is only correct in one configuration is a
        # literal, and W0-E's rule is that no field here may be a constant.
        "audit_chain_durability": (
            f"DURABLE_SHARED_STORE — the audit store survives this process "
            f"({PERSISTENCE.mode})"
            if _audit_chain_persisted()
            else "IN_PROCESS_ONLY — the audit store is not durable and is not "
                 "shared between instances"
        ),
        # fail_closed cannot be evaluated from inside this process while
        # authorization derives from a client-supplied header (W0-B). Reporting
        # it as a boolean at all would repeat the original defect.
        "fail_closed": "NOT_ESTABLISHED",
        "fail_closed_reason": "authorization not bound to verified identity (W0-B pending)",
        # Previously fixed strings claiming a sealed constitution and active
        # production governance. Neither is computable here.
        "constitutional_status": "NOT_ESTABLISHED_BY_THIS_SERVICE",
        "platform_state": "NOT_ESTABLISHED_BY_THIS_SERVICE",
        "no_autonomous_execution": "NOT_ESTABLISHED",
        "attestation_note": (
            "This service makes no governance attestation it cannot compute. "
            "See MVC-INC-ATTEST-001."
        ),
        "ts": utc_now_iso(),
    }
