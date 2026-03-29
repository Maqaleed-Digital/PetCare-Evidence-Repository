from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
from uuid import uuid4

from .models import ROLE_PHARMACY, Prescription, PrescriptionStatus


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class PharmacyReviewStatus(str, Enum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    READY_FOR_DISPENSE_QUEUE = "READY_FOR_DISPENSE_QUEUE"
    RETURNED_TO_VET = "RETURNED_TO_VET"


PHARMACY_REVIEW_WORKFLOW_AUDIT_EVENTS: tuple[str, ...] = (
    "prescription.review.workflow_started",
    "prescription.review.note_added",
    "prescription.review.reason_recorded",
    "prescription.review.status_changed",
    "prescription.review.read_model_viewed",
    "prescription.review.list_viewed",
)

PHARMACY_REVIEW_REASON_CODES: tuple[str, ...] = (
    "WARNING_ACKNOWLEDGED",
    "CLARIFICATION_REQUIRED",
    "RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT",
    "READY_FOR_QUEUE_CONFIRMATION",
)

PHARMACY_REVIEW_DECISION_TO_STATUS: dict[str, PharmacyReviewStatus] = {
    "ACKNOWLEDGE_WARNINGS": PharmacyReviewStatus.ACKNOWLEDGED,
    "APPROVE_FOR_DISPENSE_QUEUE": PharmacyReviewStatus.READY_FOR_DISPENSE_QUEUE,
    "RETURN_TO_VET_REVIEW": PharmacyReviewStatus.RETURNED_TO_VET,
}


@dataclass(frozen=True)
class PharmacyReviewNote:
    note_id: str
    actor_user_id: str
    reason_code: str
    note_text: str
    created_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "note_id": self.note_id,
            "actor_user_id": self.actor_user_id,
            "reason_code": self.reason_code,
            "note_text": self.note_text,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class PharmacyReviewRecord:
    review_id: str
    prescription_id: str
    tenant_id: str
    consultation_id: str
    pet_id: str
    medication_name: str
    source_prescription_status: str
    review_status: PharmacyReviewStatus
    created_by_user_id: str
    created_at: str
    last_updated_at: str
    notes: tuple[PharmacyReviewNote, ...] = ()
    audit_trail: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    def with_event(
        self,
        event_name: str,
        actor_user_id: str,
        details: Mapping[str, Any] | None = None,
    ) -> "PharmacyReviewRecord":
        payload: dict[str, Any] = {
            "event_name": event_name,
            "actor_user_id": actor_user_id,
            "occurred_at": _utc_now(),
        }
        if details:
            payload["details"] = dict(sorted(details.items()))
        return replace(
            self,
            last_updated_at=payload["occurred_at"],
            audit_trail=self.audit_trail + (payload,),
        )

    def to_read_model(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "prescription_id": self.prescription_id,
            "tenant_id": self.tenant_id,
            "consultation_id": self.consultation_id,
            "pet_id": self.pet_id,
            "medication_name": self.medication_name,
            "source_prescription_status": self.source_prescription_status,
            "review_status": self.review_status.value,
            "created_by_user_id": self.created_by_user_id,
            "created_at": self.created_at,
            "last_updated_at": self.last_updated_at,
            "notes": [note.to_dict() for note in self.notes],
            "audit_trail": [dict(item) for item in self.audit_trail],
        }


def _new_review_id() -> str:
    return f"rx_review_{uuid4().hex}"


def _new_note_id() -> str:
    return f"rx_review_note_{uuid4().hex}"


def start_pharmacy_review(
    prescription: Prescription,
    *,
    actor_user_id: str,
    actor_role: str,
) -> PharmacyReviewRecord:
    if actor_role != ROLE_PHARMACY:
        raise PermissionError("Pharmacy operator role is required for review workflow.")
    if prescription.status not in (PrescriptionStatus.AUTHORIZED, PrescriptionStatus.SUBMITTED):
        raise ValueError("Only AUTHORIZED or SUBMITTED prescriptions may enter pharmacy review workflow.")

    created_at = _utc_now()
    record = PharmacyReviewRecord(
        review_id=_new_review_id(),
        prescription_id=prescription.prescription_id,
        tenant_id=prescription.tenant_id,
        consultation_id=prescription.consultation_id,
        pet_id=prescription.pet_id,
        medication_name=prescription.medication_name,
        source_prescription_status=prescription.status.value,
        review_status=PharmacyReviewStatus.PENDING,
        created_by_user_id=actor_user_id,
        created_at=created_at,
        last_updated_at=created_at,
    )
    return record.with_event(
        "prescription.review.workflow_started",
        actor_user_id,
        {
            "source_prescription_status": prescription.status.value,
            "review_status": PharmacyReviewStatus.PENDING.value,
        },
    )


def add_review_note(
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
    actor_role: str,
    reason_code: str,
    note_text: str,
) -> PharmacyReviewRecord:
    if actor_role != ROLE_PHARMACY:
        raise PermissionError("Pharmacy operator role is required for review notes.")
    if reason_code not in PHARMACY_REVIEW_REASON_CODES:
        raise ValueError("Unsupported pharmacy review reason code.")

    note = PharmacyReviewNote(
        note_id=_new_note_id(),
        actor_user_id=actor_user_id,
        reason_code=reason_code,
        note_text=note_text,
        created_at=_utc_now(),
    )
    updated = replace(review_record, notes=review_record.notes + (note,))
    updated = updated.with_event(
        "prescription.review.note_added",
        actor_user_id,
        {
            "reason_code": reason_code,
            "note_id": note.note_id,
        },
    )
    updated = updated.with_event(
        "prescription.review.reason_recorded",
        actor_user_id,
        {
            "reason_code": reason_code,
        },
    )
    return updated


def progress_pharmacy_review(
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
    actor_role: str,
    decision: str,
    reason_code: str,
    note_text: str,
) -> PharmacyReviewRecord:
    if actor_role != ROLE_PHARMACY:
        raise PermissionError("Pharmacy operator role is required for review workflow progression.")
    if decision not in PHARMACY_REVIEW_DECISION_TO_STATUS:
        raise ValueError("Unsupported pharmacy review decision.")
    if reason_code not in PHARMACY_REVIEW_REASON_CODES:
        raise ValueError("Unsupported pharmacy review reason code.")

    updated = add_review_note(
        review_record,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        reason_code=reason_code,
        note_text=note_text,
    )
    next_status = PHARMACY_REVIEW_DECISION_TO_STATUS[decision]
    updated = replace(updated, review_status=next_status)
    updated = updated.with_event(
        "prescription.review.status_changed",
        actor_user_id,
        {
            "decision": decision,
            "review_status": next_status.value,
        },
    )
    return updated


def get_pharmacy_review_workflow_read_model(
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    _ = actor_user_id
    return review_record.to_read_model()


def list_pharmacy_review_records(
    review_records: Sequence[PharmacyReviewRecord],
    *,
    actor_user_id: str,
) -> list[dict[str, Any]]:
    _ = actor_user_id
    ordered = sorted(
        review_records,
        key=lambda item: (item.created_at, item.review_id),
    )
    return [item.to_read_model() for item in ordered]


__all__ = [
    "PHARMACY_REVIEW_DECISION_TO_STATUS",
    "PHARMACY_REVIEW_REASON_CODES",
    "PHARMACY_REVIEW_WORKFLOW_AUDIT_EVENTS",
    "PharmacyReviewNote",
    "PharmacyReviewRecord",
    "PharmacyReviewStatus",
    "add_review_note",
    "get_pharmacy_review_workflow_read_model",
    "list_pharmacy_review_records",
    "progress_pharmacy_review",
    "start_pharmacy_review",
]
