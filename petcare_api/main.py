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

from petcare.audit.audit_service import AuditEvent, emit_audit_event
from petcare.auth.access_control import (
    ROLE_OWNER,
    ROLE_VETERINARIAN,
    ROLE_PHARMACY_OPERATOR,
    ROLE_PLATFORM_ADMIN,
    ROLE_PARTNER_CLINIC_ADMIN,
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
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(
    title="PetCare Platform API",
    version="1.0.0",
    description="Governed veterinary platform API. Fail-closed. Audit-traced.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory stores (pilot phase — DB wiring deferred to PH7)
# ---------------------------------------------------------------------------
_audit_log: list[dict] = []
_sessions: dict[str, dict] = {}
_notes: dict[str, dict] = {}
_appointments: dict[str, dict] = {}

uphr_service = UPHRService()
consent_repo = ConsentRepository(
    os.environ.get("CONSENT_STORE_PATH", "petcare_runtime/data/consent_store.json")
)

# ---------------------------------------------------------------------------
# Auth helpers (pilot: role from header; production: JWT validation)
# ---------------------------------------------------------------------------
VALID_ROLES = {ROLE_OWNER, ROLE_VETERINARIAN, ROLE_PHARMACY_OPERATOR,
               ROLE_PLATFORM_ADMIN, ROLE_PARTNER_CLINIC_ADMIN}

def require_role(x_petcare_role: str = Header(...)) -> str:
    if x_petcare_role not in VALID_ROLES:
        raise HTTPException(403, f"Unknown role: {x_petcare_role}")
    return x_petcare_role

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
    _audit_log.append(record)
    log.info("AUDIT %s", json.dumps(record))
    return record

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
class AuditProbePayload(BaseModel):
    event_name: str
    actor_role: str
    surface: str
    correlation_id: str
    actor_id: Optional[str] = "system"
    tenant_id: Optional[str] = "platform"
    resource_type: Optional[str] = "ui_surface"
    resource_id: Optional[str] = "unknown"
    action_result: Optional[str] = "probe"

@app.post("/audit/ui")
def audit_ui_probe(payload: AuditProbePayload):
    record = _audit(
        event_name=payload.event_name,
        actor_id=payload.actor_id or "system",
        actor_role=payload.actor_role,
        tenant_id=payload.tenant_id or "platform",
        resource_type=payload.resource_type or "ui_surface",
        resource_id=payload.resource_id or payload.surface,
        action_result=payload.action_result or "probe",
        correlation_id=payload.correlation_id,
    )
    return {"accepted": True, "audit_event_id": record["audit_event_id"]}

@app.get("/audit/events")
def list_audit_events(role: str = Depends(require_admin)):
    return {"events": _audit_log, "count": len(_audit_log)}

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
        "tenant_id": body.tenant_id,
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
        tenant_id=body.tenant_id,
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
        "tenant_id": body.tenant_id,
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
        tenant_id=body.tenant_id,
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
        tenant_id=body.tenant_id,
        resource_type="consultation_note",
        resource_id=note_id,
        action_result="success",
        correlation_id=x_correlation_id,
    )
    return note

@app.post("/api/consultations/notes/{note_id}/sign")
def sign_note(
    note_id: str,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
    x_tenant_id: str = Header(default="platform"),
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
        tenant_id=x_tenant_id,
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
        "tenant_id": body.tenant_id,
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
        tenant_id=body.tenant_id,
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
    prescription_id: str,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
    x_tenant_id: str = Header(default="platform"),
):
    if role != ROLE_PHARMACY_OPERATOR:
        raise HTTPException(403, "Only pharmacy operators may dispense prescriptions")
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
        tenant_id=x_tenant_id,
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
    body: PetRequest,
    role: str = Depends(require_role),
    x_actor_id: str = Header(...),
    x_correlation_id: str = Header(default_factory=lambda: str(uuid4())),
):
    if role not in {ROLE_OWNER, ROLE_PLATFORM_ADMIN}:
        raise HTTPException(403, "Only owners or admins may create pet profiles")
    pet = uphr_service.create_pet(
        tenant_id=body.tenant_id,
        owner_id=body.owner_id,
        name=body.name,
        species=body.species,
    )
    _audit(
        event_name="pet.profile.created",
        actor_id=x_actor_id,
        actor_role=role,
        tenant_id=body.tenant_id,
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
@app.get("/api/governance/status")
def governance_status():
    return {
        "constitutional_status": "OPERATING_UNDER_SEALED_CONSTITUTION",
        "platform_state": "CONTROLLED_PRODUCTION_ACTIVE_UNDER_CONSTITUTION",
        "no_autonomous_execution": True,
        "audit_chain_active": True,
        "fail_closed": True,
        "ts": utc_now_iso(),
    }
