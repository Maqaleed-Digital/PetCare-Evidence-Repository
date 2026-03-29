from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from .handoff import (
    get_latest_review_decision_summary,
    get_review_handoff_read_model,
    list_ready_for_dispense_queue_from_reviews,
    list_review_handoff_records,
)
from .query import get_full_review_context, list_reviews_for_prescription
from .repository import PharmacyRepository
from .visibility import (
    get_operational_review_status_summary,
    get_return_to_vet_follow_up_link,
    get_review_disposition_registry,
    get_review_history_read_model,
    list_review_timeline_entries,
)


READ_ONLY_API_SURFACES: tuple[str, ...] = (
    "get_review_context_endpoint",
    "list_reviews_for_prescription_endpoint",
    "get_review_handoff_endpoint",
    "list_review_handoffs_endpoint",
    "get_latest_review_summary_endpoint",
    "list_ready_for_dispense_queue_endpoint",
    "get_review_history_endpoint",
    "get_review_timeline_endpoint",
    "get_return_to_vet_follow_up_endpoint",
    "get_review_disposition_registry_endpoint",
    "get_operational_review_status_summary_endpoint",
)


def _read_only_envelope(surface: str, payload: Dict[str, Any], actor_user_id: str) -> Dict[str, Any]:
    return {
        "surface": surface,
        "read_only": True,
        "actor_user_id": actor_user_id,
        "payload": payload,
    }


def get_review_context_endpoint(
    repo: PharmacyRepository,
    *,
    review_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    payload = get_full_review_context(
        repo,
        review_id=review_id,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_review_context_endpoint", payload, actor_user_id)


def list_reviews_for_prescription_endpoint(
    repo: PharmacyRepository,
    *,
    prescription_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    payload = list_reviews_for_prescription(
        repo,
        prescription_id=prescription_id,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("list_reviews_for_prescription_endpoint", payload, actor_user_id)


def get_review_handoff_endpoint(
    repo: PharmacyRepository,
    *,
    review_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    review = repo.get_review(review_id)
    prescription = repo.get_prescription(review.prescription_id)
    payload = get_review_handoff_read_model(
        prescription,
        review,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_review_handoff_endpoint", payload, actor_user_id)


def list_review_handoffs_endpoint(
    repo: PharmacyRepository,
    *,
    tenant_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    reviews = repo.list_reviews_by_tenant_id(tenant_id)
    prescriptions = [repo.get_prescription(review.prescription_id) for review in reviews]
    payload = {
        "tenant_id": tenant_id,
        "items": list_review_handoff_records(
            prescriptions,
            reviews,
            actor_user_id=actor_user_id,
        ),
    }
    return _read_only_envelope("list_review_handoffs_endpoint", payload, actor_user_id)


def get_latest_review_summary_endpoint(
    repo: PharmacyRepository,
    *,
    review_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    review = repo.get_review(review_id)
    prescription = repo.get_prescription(review.prescription_id)
    payload = get_latest_review_decision_summary(
        prescription,
        review,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_latest_review_summary_endpoint", payload, actor_user_id)


def list_ready_for_dispense_queue_endpoint(
    repo: PharmacyRepository,
    *,
    tenant_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    reviews = repo.list_reviews_by_tenant_id(tenant_id)
    prescriptions = [repo.get_prescription(review.prescription_id) for review in reviews]
    payload = {
        "tenant_id": tenant_id,
        "items": [
            asdict(item)
            for item in list_ready_for_dispense_queue_from_reviews(
                prescriptions,
                reviews,
                actor_user_id=actor_user_id,
            )
        ],
    }
    return _read_only_envelope("list_ready_for_dispense_queue_endpoint", payload, actor_user_id)


def get_review_history_endpoint(
    repo: PharmacyRepository,
    *,
    review_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    review = repo.get_review(review_id)
    payload = get_review_history_read_model(
        review,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_review_history_endpoint", payload, actor_user_id)


def get_review_timeline_endpoint(
    repo: PharmacyRepository,
    *,
    review_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    review = repo.get_review(review_id)
    payload = list_review_timeline_entries(
        review,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_review_timeline_endpoint", payload, actor_user_id)


def get_return_to_vet_follow_up_endpoint(
    repo: PharmacyRepository,
    *,
    review_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    review = repo.get_review(review_id)
    prescription = repo.get_prescription(review.prescription_id)
    payload = get_return_to_vet_follow_up_link(
        prescription,
        review,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_return_to_vet_follow_up_endpoint", payload, actor_user_id)


def get_review_disposition_registry_endpoint(
    *,
    actor_user_id: str,
) -> Dict[str, Any]:
    payload = get_review_disposition_registry(
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_review_disposition_registry_endpoint", payload, actor_user_id)


def get_operational_review_status_summary_endpoint(
    repo: PharmacyRepository,
    *,
    tenant_id: str,
    actor_user_id: str,
) -> Dict[str, Any]:
    reviews = repo.list_reviews_by_tenant_id(tenant_id)
    prescriptions = [repo.get_prescription(review.prescription_id) for review in reviews]
    payload = get_operational_review_status_summary(
        prescriptions,
        reviews,
        actor_user_id=actor_user_id,
    )
    return _read_only_envelope("get_operational_review_status_summary_endpoint", payload, actor_user_id)


__all__ = [
    "READ_ONLY_API_SURFACES",
    "get_latest_review_summary_endpoint",
    "get_operational_review_status_summary_endpoint",
    "get_return_to_vet_follow_up_endpoint",
    "get_review_context_endpoint",
    "get_review_disposition_registry_endpoint",
    "get_review_handoff_endpoint",
    "get_review_history_endpoint",
    "get_review_timeline_endpoint",
    "list_ready_for_dispense_queue_endpoint",
    "list_review_handoffs_endpoint",
    "list_reviews_for_prescription_endpoint",
]
