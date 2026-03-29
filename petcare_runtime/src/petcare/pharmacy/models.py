from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


ROLE_VETERINARIAN = "ROLE_VETERINARIAN"
ROLE_PHARMACY = "ROLE_PHARMACY"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PrescriptionStatus(str, Enum):
    DRAFT = "DRAFT"
    AUTHORIZED = "AUTHORIZED"
    SUBMITTED = "SUBMITTED"
    DISPENSED = "DISPENSED"
    CANCELLED = "CANCELLED"


PRESCRIPTION_AUDIT_EVENTS: tuple[str, ...] = (
    "prescription.created",
    "prescription.authorization_denied.invalid_role",
    "prescription.authorization_denied.missing_signed_note",
    "prescription.safety_warning_added",
    "prescription.override_reason_recorded",
    "prescription.authorized",
    "prescription.submitted",
    "prescription.dispensed",
    "prescription.cancelled",
    "prescription.queue_viewed",
)


@dataclass(frozen=True)
class PrescriptionSafetyWarning:
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict:
        return {"code": self.code, "severity": self.severity, "message": self.message}


@dataclass(frozen=True)
class Prescription:
    prescription_id: str
    tenant_id: str
    pet_id: str
    consultation_id: str
    signed_note_id: str
    medication_code: str
    medication_name: str
    dosage_instructions: str
    quantity: str
    status: PrescriptionStatus
    created_by_user_id: str
    created_at: str
    authorized_by_user_id: str | None = None
    authorized_at: str | None = None
    submitted_at: str | None = None
    dispensed_by_user_id: str | None = None
    dispensed_at: str | None = None
    cancelled_at: str | None = None
    ai_contribution: str | None = None
    safety_warnings: tuple[PrescriptionSafetyWarning, ...] = field(default_factory=tuple)
    override_reason: str | None = None
    audit_trail: tuple[dict, ...] = field(default_factory=tuple)

    def with_event(
        self,
        event_name: str,
        actor_user_id: str,
        details: dict | None = None,
    ) -> "Prescription":
        entry: dict[str, Any] = {
            "event_name": event_name,
            "actor_user_id": actor_user_id,
            "occurred_at": utc_now(),
        }
        if details:
            entry["details"] = details
        return replace(self, audit_trail=self.audit_trail + (entry,))

    def to_read_model(self) -> dict:
        return {
            "prescription_id": self.prescription_id,
            "tenant_id": self.tenant_id,
            "pet_id": self.pet_id,
            "consultation_id": self.consultation_id,
            "signed_note_id": self.signed_note_id,
            "medication_code": self.medication_code,
            "medication_name": self.medication_name,
            "dosage_instructions": self.dosage_instructions,
            "quantity": self.quantity,
            "status": self.status.value,
            "created_by_user_id": self.created_by_user_id,
            "created_at": self.created_at,
            "authorized_by_user_id": self.authorized_by_user_id,
            "authorized_at": self.authorized_at,
            "submitted_at": self.submitted_at,
            "dispensed_by_user_id": self.dispensed_by_user_id,
            "dispensed_at": self.dispensed_at,
            "cancelled_at": self.cancelled_at,
            "ai_contribution": self.ai_contribution,
            "safety_warnings": [w.to_dict() for w in self.safety_warnings],
            "override_reason": self.override_reason,
            "audit_trail": list(self.audit_trail),
        }


@dataclass(frozen=True)
class PrescriptionQueueEntry:
    prescription_id: str
    tenant_id: str
    pet_id: str
    consultation_id: str
    medication_name: str
    status: str
    authorized_at: str | None
    submitted_at: str | None
    warning_count: int


def new_prescription_id() -> str:
    return f"rx_{uuid4().hex}"
