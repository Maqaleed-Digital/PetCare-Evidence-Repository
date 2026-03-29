from __future__ import annotations

from typing import Any, Dict

from .handoff import build_review_handoff_record
from .repository import PharmacyRepository
from .visibility import get_review_history_read_model


def get_full_review_context(
    repo: PharmacyRepository,
    *,
    review_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    review = repo.get_review(review_id)
    prescription = repo.get_prescription(review.prescription_id)

    return {
        "prescription": prescription.prescription_id,
        "review": review.review_id,
        "handoff": build_review_handoff_record(prescription, review).to_dict(),
        "history": get_review_history_read_model(review, actor_user_id=actor_user_id),
    }


def list_reviews_for_prescription(
    repo: PharmacyRepository,
    *,
    prescription_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    reviews = repo.list_reviews_by_prescription_id(prescription_id)

    return {
        "prescription_id": prescription_id,
        "review_ids": [r.review_id for r in reviews],
        "count": len(reviews),
        "actor_user_id": actor_user_id,
    }
