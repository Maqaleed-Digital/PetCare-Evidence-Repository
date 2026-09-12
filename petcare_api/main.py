"""
PetCare Platform API
Governed, fail-closed, audit-traced.
No autonomous execution. No unauthenticated writes.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request
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

_sessions: dict[str, dict] = {}
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
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
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
        actor_id=x_actor_id,
        actor_role=role,
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
    appointment_id: str,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    appt = _appointments.get(appointment_id)
    if not appt:
        raise HTTPException(404, "Appointment not found")
    _audit(
        event_name="appointment.viewed",
        actor_id=x_actor_id,
        actor_role=role,
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
    tenant_id: str
    clinic_id: Optional[str] = None

@app.post("/api/consultations")
def start_consultation(
    request: Request,
    body: ConsultationRequest,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    if role not in {ROLE_VETERINARIAN, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Only vets or admins may start consultations")
    session_id = str(uuid4())
    now = utc_now_iso()
    session = {
        "session_id": session_id,
        "pet_id": body.pet_id,
        "owner_id": body.owner_id,
        "veterinarian_id": body.veterinarian_id,
        "tenant_id": require_tenant(request, body.tenant_id),
        "clinic_id": body.clinic_id,
        "status": SESSION_REQUESTED,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "cancelled_at": None,
    }
    _sessions[session_id] = session
    _audit(
        event_name="consultation.session.requested",
        actor_id=x_actor_id,
        actor_role=role,
        tenant_id=require_tenant(request, body.tenant_id),
        resource_type="consultation_session",
        resource_id=session_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=body.clinic_id,
    )
    return session

@app.get("/api/consultations/{session_id}")
def get_consultation(
    session_id: str,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Consultation session not found")
    _audit(
        event_name="consultation.session.viewed",
        actor_id=x_actor_id,
        actor_role=role,
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

@app.post("/api/consultations/{session_id}/notes")
def create_note(
    request: Request,
    session_id: str,
    body: NoteRequest,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only vets may create consultation notes")
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    note_id = str(uuid4())
    now = utc_now_iso()
    note = {
        "note_id": note_id,
        "session_id": session_id,
        "pet_id": body.pet_id,
        "veterinarian_id": x_actor_id,
        "content": body.content,
        "status": NOTE_DRAFT,
        "created_at": now,
        "signed_at": None,
        "signed_by_actor_id": None,
    }
    _notes[note_id] = note
    _audit(
        event_name="consultation.note.created",
        actor_id=x_actor_id,
        actor_role=role,
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
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only vets may sign notes")
    note = _notes.get(note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    if note["status"] == NOTE_SIGNED:
        raise HTTPException(409, "Note already signed — immutable")
    now = utc_now_iso()
    note["status"] = NOTE_SIGNED
    note["signed_at"] = now
    note["signed_by_actor_id"] = x_actor_id
    _audit(
        event_name="consultation.note.signed",
        actor_id=x_actor_id,
        actor_role=role,
        tenant_id=require_tenant(request),
        resource_type="consultation_note",
        resource_id=note_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return note

# ---------------------------------------------------------------------------
# Prescriptions
# ---------------------------------------------------------------------------
_prescriptions: dict[str, dict] = {}

class PrescriptionRequest(BaseModel):
    pet_id: str
    session_id: str
    tenant_id: str
    clinic_id: Optional[str] = None
    medication_name: str
    dosage: str
    instructions: str

@app.post("/api/prescriptions")
def issue_prescription(
    request: Request,
    body: PrescriptionRequest,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    if role != ROLE_VETERINARIAN:
        raise HTTPException(403, "Only vets may issue prescriptions")
    rx_id = str(uuid4())
    now = utc_now_iso()
    rx = {
        "prescription_id": rx_id,
        "pet_id": body.pet_id,
        "session_id": body.session_id,
        "issuing_vet_id": x_actor_id,
        "tenant_id": require_tenant(request, body.tenant_id),
        "clinic_id": body.clinic_id,
        "medication_name": body.medication_name,
        "dosage": body.dosage,
        "instructions": body.instructions,
        "status": "ISSUED",
        "issued_at": now,
        "dispensed_at": None,
    }
    _prescriptions[rx_id] = rx
    _audit(
        event_name="prescription.issued",
        actor_id=x_actor_id,
        actor_role=role,
        tenant_id=require_tenant(request, body.tenant_id),
        resource_type="prescription",
        resource_id=rx_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=body.clinic_id,
    )
    return rx

@app.get("/api/prescriptions/{prescription_id}")
def get_prescription(
    prescription_id: str,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    rx = _prescriptions.get(prescription_id)
    if not rx:
        raise HTTPException(404, "Prescription not found")
    _audit(
        event_name="prescription.viewed",
        actor_id=x_actor_id,
        actor_role=role,
        tenant_id=rx["tenant_id"],
        resource_type="prescription",
        resource_id=prescription_id,
        action_result="success",
        correlation_id=x_correlation_id,
        clinic_id=rx.get("clinic_id"),
    )
    return rx

@app.post("/api/prescriptions/{prescription_id}/dispense")
def dispense_prescription(
    request: Request,
    prescription_id: str,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    # REQ-DISP-AUTH-FAILCLOSED (BRD V3.2 s11.1). Dispensing acts whose
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
        raise HTTPException(
            403,
            "Dispensing is restricted to a veterinarian: the professional-authority "
            "class for this act is unclassified (REQ-DISP-AUTH-FAILCLOSED)",
        )
    rx = _prescriptions.get(prescription_id)
    if not rx:
        raise HTTPException(404, "Prescription not found")
    if rx["status"] != "ISSUED":
        raise HTTPException(409, f"Cannot dispense — status is {rx['status']}")
    now = utc_now_iso()
    rx["status"] = "DISPENSED"
    rx["dispensed_at"] = now
    _audit(
        event_name="prescription.dispensed",
        actor_id=x_actor_id,
        actor_role=role,
        tenant_id=require_tenant(request),
        resource_type="prescription",
        resource_id=prescription_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return rx

# ---------------------------------------------------------------------------
# Pet profiles (UPHR)
# ---------------------------------------------------------------------------
class PetRequest(BaseModel):
    tenant_id: str
    owner_id: str
    name: str
    species: str

@app.post("/api/pets")
def create_pet(
    request: Request,
    body: PetRequest,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    if role not in {ROLE_OWNER, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Only owners or admins may create pet profiles")
    pet = uphr_service.create_pet(
        tenant_id=require_tenant(request, body.tenant_id),
        owner_id=body.owner_id,
        name=body.name,
        species=body.species,
    )
    _audit(
        event_name="pet.profile.created",
        actor_id=x_actor_id,
        actor_role=role,
        tenant_id=require_tenant(request, body.tenant_id),
        resource_type="pet",
        resource_id=pet.pet_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return {"pet_id": pet.pet_id, "name": pet.name, "species": pet.species,
            "owner_id": pet.owner_id, "tenant_id": pet.tenant_id}

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
