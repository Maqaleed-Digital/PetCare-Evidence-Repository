from __future__ import annotations

from typing import Any, Callable, Dict

from .api import (
    get_latest_review_summary_endpoint,
    get_operational_review_status_summary_endpoint,
    get_return_to_vet_follow_up_endpoint,
    get_review_context_endpoint,
    get_review_disposition_registry_endpoint,
    get_review_handoff_endpoint,
    get_review_history_endpoint,
    get_review_timeline_endpoint,
    list_ready_for_dispense_queue_endpoint,
    list_review_handoffs_endpoint,
    list_reviews_for_prescription_endpoint,
)
from .contracts import error_envelope, success_envelope
from .registry import READ_ONLY_ENDPOINT_REGISTRY
from .repository import PharmacyRepository

ROUTE_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {
    "/review/context": get_review_context_endpoint,
    "/review/list": list_reviews_for_prescription_endpoint,
    "/review/handoff": get_review_handoff_endpoint,
    "/review/handoffs": list_review_handoffs_endpoint,
    "/review/summary": get_latest_review_summary_endpoint,
    "/review/queue": list_ready_for_dispense_queue_endpoint,
    "/review/history": get_review_history_endpoint,
    "/review/timeline": get_review_timeline_endpoint,
    "/review/follow-up": get_return_to_vet_follow_up_endpoint,
    "/review/registry": get_review_disposition_registry_endpoint,
    "/review/operational-summary": get_operational_review_status_summary_endpoint,
}


def handle_request(
    repo: PharmacyRepository,
    *,
    path: str,
    actor_user_id: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    if path not in ROUTE_REGISTRY:
        return error_envelope(
            surface="http_adapter",
            actor_user_id=actor_user_id,
            error_code="ROUTE_NOT_FOUND",
            message=f"Route {path} not registered",
        )
    handler = ROUTE_REGISTRY[path]
    try:
        if "repo" in handler.__code__.co_varnames:
            result = handler(repo, actor_user_id=actor_user_id, **params)
        else:
            result = handler(actor_user_id=actor_user_id, **params)
        return success_envelope(
            surface=path,
            actor_user_id=actor_user_id,
            payload=result,
        )
    except Exception as exc:
        return error_envelope(
            surface=path,
            actor_user_id=actor_user_id,
            error_code="UNHANDLED_EXCEPTION",
            message=str(exc),
        )


__all__ = [
    "ROUTE_REGISTRY",
    "handle_request",
]
