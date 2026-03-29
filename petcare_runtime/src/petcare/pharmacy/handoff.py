from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .models import Prescription, PrescriptionQueueEntry, PrescriptionStatus
from .review import PharmacyReviewRecord, PharmacyReviewStatus


REVIEW_HANDOFF_AUDIT_EVENTS: tuple[str, ...] = (
    "prescription.review.handoff.read_model_viewed",
    "prescription.review.handoff.list_viewed",
    "prescription.review.handoff.summary_viewed",
)

REVIEW_HANDOFF_OUTCOMES: tuple[str, ...] = (
    "READY_FOR_DISPENSE_QUEUE",
    "RETURNED_TO_VET",
    "REVIEW_IN_PROGRESS",
)


@dataclass(frozen=True)
class ReviewHandoffRecord:
    prescription_id: str
    review_id: str
    tenant_id: str
    consultation_id: str
    pet_id: str
    medication_name: str
    source_prescription_status: str
    review_status: str
    handoff_outcome: str
    latest_reason_code: str | None
    latest_note_text: str | None
    warning_count: int
    review_note_count: int
    created_at: str
    last_updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prescription_id": self.prescription_id,
            "review_id": self.review_id,
            "tenant_id": self.tenant_id,
            "consultation_id": self.consultation_id,
            "pet_id": self.pet_id,
            "medication_name": self.medication_name,
            "source_prescription_status": self.source_prescription_status,
            "review_status": self.review_status,
            "handoff_outcome": self.handoff_outcome,
            "latest_reason_code": self.latest_reason_code,
            "latest_note_text": self.latest_note_text,
            "warning_count": self.warning_count,
            "review_note_count": self.review_note_count,
            "created_at": self.created_at,
            "last_updated_at": self.last_updated_at,
        }


def _latest_reason_code(review_record: PharmacyReviewRecord) -> str | None:
    if not review_record.notes:
        return None
    return review_record.notes[-1].reason_code


def _latest_note_text(review_record: PharmacyReviewRecord) -> str | None:
    if not review_record.notes:
        return None
    return review_record.notes[-1].note_text


def _handoff_outcome(review_record: PharmacyReviewRecord) -> str:
    if review_record.review_status is PharmacyReviewStatus.READY_FOR_DISPENSE_QUEUE:
        return "READY_FOR_DISPENSE_QUEUE"
    if review_record.review_status is PharmacyReviewStatus.RETURNED_TO_VET:
        return "RETURNED_TO_VET"
    return "REVIEW_IN_PROGRESS"


def build_review_handoff_record(
    prescription: Prescription,
    review_record: PharmacyReviewRecord,
) -> ReviewHandoffRecord:
    if prescription.prescription_id != review_record.prescription_id:
        raise ValueError("Prescription and review record must refer to the same prescription.")

    return ReviewHandoffRecord(
        prescription_id=prescription.prescription_id,
        review_id=review_record.review_id,
        tenant_id=prescription.tenant_id,
        consultation_id=prescription.consultation_id,
        pet_id=prescription.pet_id,
        medication_name=prescription.medication_name,
        source_prescription_status=prescription.status.value,
        review_status=review_record.review_status.value,
        handoff_outcome=_handoff_outcome(review_record),
        latest_reason_code=_latest_reason_code(review_record),
        latest_note_text=_latest_note_text(review_record),
        warning_count=len(prescription.safety_warnings),
        review_note_count=len(review_record.notes),
        created_at=review_record.created_at,
        last_updated_at=review_record.last_updated_at,
    )


def get_review_handoff_read_model(
    prescription: Prescription,
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    _ = actor_user_id
    return build_review_handoff_record(prescription, review_record).to_dict()


def list_review_handoff_records(
    prescriptions: Sequence[Prescription],
    review_records: Sequence[PharmacyReviewRecord],
    *,
    actor_user_id: str,
) -> list[dict[str, Any]]:
    _ = actor_user_id

    prescriptions_by_id = {
        prescription.prescription_id: prescription
        for prescription in prescriptions
    }

    handoffs: list[dict[str, Any]] = []
    for review_record in review_records:
        prescription = prescriptions_by_id.get(review_record.prescription_id)
        if prescription is None:
            continue
        handoffs.append(build_review_handoff_record(prescription, review_record).to_dict())

    return sorted(
        handoffs,
        key=lambda item: (
            item["created_at"],
            item["review_id"],
        ),
    )


def get_latest_review_decision_summary(
    prescription: Prescription,
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    _ = actor_user_id

    handoff = build_review_handoff_record(prescription, review_record)
    return {
        "prescription_id": handoff.prescription_id,
        "review_id": handoff.review_id,
        "medication_name": handoff.medication_name,
        "handoff_outcome": handoff.handoff_outcome,
        "review_status": handoff.review_status,
        "latest_reason_code": handoff.latest_reason_code,
        "latest_note_text": handoff.latest_note_text,
        "review_note_count": handoff.review_note_count,
        "warning_count": handoff.warning_count,
        "source_prescription_status": handoff.source_prescription_status,
        "last_updated_at": handoff.last_updated_at,
    }


def list_ready_for_dispense_queue_from_reviews(
    prescriptions: Sequence[Prescription],
    review_records: Sequence[PharmacyReviewRecord],
    *,
    actor_user_id: str,
) -> list[PrescriptionQueueEntry]:
    _ = actor_user_id

    review_by_prescription_id = {
        review_record.prescription_id: review_record
        for review_record in review_records
        if review_record.review_status is PharmacyReviewStatus.READY_FOR_DISPENSE_QUEUE
    }

    eligible: list[PrescriptionQueueEntry] = []
    for prescription in prescriptions:
        review_record = review_by_prescription_id.get(prescription.prescription_id)
        if review_record is None:
            continue
        if prescription.status not in (PrescriptionStatus.AUTHORIZED, PrescriptionStatus.SUBMITTED):
            continue

        eligible.append(
            PrescriptionQueueEntry(
                prescription_id=prescription.prescription_id,
                tenant_id=prescription.tenant_id,
                pet_id=prescription.pet_id,
                consultation_id=prescription.consultation_id,
                medication_name=prescription.medication_name,
                status=prescription.status.value,
                authorized_at=prescription.authorized_at,
                submitted_at=prescription.submitted_at,
                warning_count=len(prescription.safety_warnings),
            )
        )

    return sorted(
        eligible,
        key=lambda item: (
            item.authorized_at or "",
            item.submitted_at or "",
            item.prescription_id,
        ),
    )


__all__ = [
    "REVIEW_HANDOFF_AUDIT_EVENTS",
    "REVIEW_HANDOFF_OUTCOMES",
    "ReviewHandoffRecord",
    "build_review_handoff_record",
    "get_latest_review_decision_summary",
    "get_review_handoff_read_model",
    "list_ready_for_dispense_queue_from_reviews",
    "list_review_handoff_records",
]
