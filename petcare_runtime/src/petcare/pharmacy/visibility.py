from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .handoff import build_review_handoff_record
from .models import Prescription
from .review import (
    PHARMACY_REVIEW_DECISION_TO_STATUS,
    PHARMACY_REVIEW_REASON_CODES,
    PharmacyReviewRecord,
    PharmacyReviewStatus,
)


REVIEW_ACCESS_AUDIT_EVENTS: tuple[str, ...] = (
    "prescription.review.history_viewed",
    "prescription.review.timeline_viewed",
    "prescription.review.follow_up_link_viewed",
    "prescription.review.disposition_registry_viewed",
    "prescription.review.operational_summary_viewed",
)

REVIEW_DISPOSITION_REGISTRY: tuple[dict[str, str], ...] = (
    {
        "decision": "ACKNOWLEDGE_WARNINGS",
        "review_status": "ACKNOWLEDGED",
        "handoff_outcome": "REVIEW_IN_PROGRESS",
    },
    {
        "decision": "APPROVE_FOR_DISPENSE_QUEUE",
        "review_status": "READY_FOR_DISPENSE_QUEUE",
        "handoff_outcome": "READY_FOR_DISPENSE_QUEUE",
    },
    {
        "decision": "RETURN_TO_VET_REVIEW",
        "review_status": "RETURNED_TO_VET",
        "handoff_outcome": "RETURNED_TO_VET",
    },
)

RETURN_TO_VET_REASON_CODES: tuple[str, ...] = (
    "CLARIFICATION_REQUIRED",
    "RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT",
)


@dataclass(frozen=True)
class ReviewTimelineEntry:
    occurred_at: str
    event_name: str
    actor_user_id: str
    review_status: str
    reason_code: str | None
    note_text: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "occurred_at": self.occurred_at,
            "event_name": self.event_name,
            "actor_user_id": self.actor_user_id,
            "review_status": self.review_status,
            "reason_code": self.reason_code,
            "note_text": self.note_text,
        }


@dataclass(frozen=True)
class ReturnToVetFollowUpLink:
    prescription_id: str
    review_id: str
    consultation_id: str
    pet_id: str
    follow_up_required: bool
    follow_up_reason_code: str | None
    latest_note_text: str | None
    review_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prescription_id": self.prescription_id,
            "review_id": self.review_id,
            "consultation_id": self.consultation_id,
            "pet_id": self.pet_id,
            "follow_up_required": self.follow_up_required,
            "follow_up_reason_code": self.follow_up_reason_code,
            "latest_note_text": self.latest_note_text,
            "review_status": self.review_status,
        }


def _audit_entry(event_name: str, actor_user_id: str, target_id: str) -> dict[str, str]:
    return {
        "event_name": event_name,
        "actor_user_id": actor_user_id,
        "target_id": target_id,
    }


def _latest_reason_code(review_record: PharmacyReviewRecord) -> str | None:
    if not review_record.notes:
        return None
    return review_record.notes[-1].reason_code


def _latest_note_text(review_record: PharmacyReviewRecord) -> str | None:
    if not review_record.notes:
        return None
    return review_record.notes[-1].note_text


def get_review_history_read_model(
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    return {
        "review_id": review_record.review_id,
        "review_status": review_record.review_status.value,
        "note_count": len(review_record.notes),
        "notes": [note.to_dict() for note in review_record.notes],
        "audit_trail": [dict(item) for item in review_record.audit_trail],
        "access_audit": _audit_entry(
            "prescription.review.history_viewed",
            actor_user_id,
            review_record.review_id,
        ),
    }


def list_review_timeline_entries(
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    latest_reason = _latest_reason_code(review_record)
    latest_note = _latest_note_text(review_record)

    timeline = [
        ReviewTimelineEntry(
            occurred_at=item["occurred_at"],
            event_name=item["event_name"],
            actor_user_id=item["actor_user_id"],
            review_status=review_record.review_status.value,
            reason_code=item.get("details", {}).get("reason_code", latest_reason),
            note_text=latest_note if item["event_name"] in (
                "prescription.review.note_added",
                "prescription.review.status_changed",
            ) else None,
        ).to_dict()
        for item in sorted(
            review_record.audit_trail,
            key=lambda entry: (
                entry["occurred_at"],
                entry["event_name"],
                entry["actor_user_id"],
            ),
        )
    ]

    return {
        "review_id": review_record.review_id,
        "timeline": timeline,
        "access_audit": _audit_entry(
            "prescription.review.timeline_viewed",
            actor_user_id,
            review_record.review_id,
        ),
    }


def get_return_to_vet_follow_up_link(
    prescription: Prescription,
    review_record: PharmacyReviewRecord,
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    if prescription.prescription_id != review_record.prescription_id:
        raise ValueError("Prescription and review record must refer to the same prescription.")

    latest_reason = _latest_reason_code(review_record)
    latest_note = _latest_note_text(review_record)

    follow_up = ReturnToVetFollowUpLink(
        prescription_id=prescription.prescription_id,
        review_id=review_record.review_id,
        consultation_id=prescription.consultation_id,
        pet_id=prescription.pet_id,
        follow_up_required=review_record.review_status is PharmacyReviewStatus.RETURNED_TO_VET,
        follow_up_reason_code=latest_reason if latest_reason in RETURN_TO_VET_REASON_CODES else None,
        latest_note_text=latest_note,
        review_status=review_record.review_status.value,
    )

    return {
        "follow_up_link": follow_up.to_dict(),
        "access_audit": _audit_entry(
            "prescription.review.follow_up_link_viewed",
            actor_user_id,
            review_record.review_id,
        ),
    }


def get_review_disposition_registry(
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    _ = PHARMACY_REVIEW_DECISION_TO_STATUS
    _ = PHARMACY_REVIEW_REASON_CODES
    return {
        "registry": [dict(item) for item in REVIEW_DISPOSITION_REGISTRY],
        "access_audit": _audit_entry(
            "prescription.review.disposition_registry_viewed",
            actor_user_id,
            "review_disposition_registry",
        ),
    }


def get_operational_review_status_summary(
    prescriptions: Sequence[Prescription],
    review_records: Sequence[PharmacyReviewRecord],
    *,
    actor_user_id: str,
) -> dict[str, Any]:
    handoffs = [
        build_review_handoff_record(prescription, review_record)
        for prescription in prescriptions
        for review_record in review_records
        if prescription.prescription_id == review_record.prescription_id
    ]

    review_status_counts: dict[str, int] = {}
    handoff_outcome_counts: dict[str, int] = {}
    source_status_counts: dict[str, int] = {}

    for handoff in handoffs:
        review_status_counts[handoff.review_status] = review_status_counts.get(handoff.review_status, 0) + 1
        handoff_outcome_counts[handoff.handoff_outcome] = handoff_outcome_counts.get(handoff.handoff_outcome, 0) + 1
        source_status_counts[handoff.source_prescription_status] = source_status_counts.get(handoff.source_prescription_status, 0) + 1

    return {
        "total_reviews": len(handoffs),
        "review_status_counts": dict(sorted(review_status_counts.items())),
        "handoff_outcome_counts": dict(sorted(handoff_outcome_counts.items())),
        "source_prescription_status_counts": dict(sorted(source_status_counts.items())),
        "access_audit": _audit_entry(
            "prescription.review.operational_summary_viewed",
            actor_user_id,
            "review_operational_summary",
        ),
    }


__all__ = [
    "REVIEW_ACCESS_AUDIT_EVENTS",
    "REVIEW_DISPOSITION_REGISTRY",
    "RETURN_TO_VET_REASON_CODES",
    "ReturnToVetFollowUpLink",
    "ReviewTimelineEntry",
    "get_operational_review_status_summary",
    "get_return_to_vet_follow_up_link",
    "get_review_disposition_registry",
    "get_review_history_read_model",
    "list_review_timeline_entries",
]
