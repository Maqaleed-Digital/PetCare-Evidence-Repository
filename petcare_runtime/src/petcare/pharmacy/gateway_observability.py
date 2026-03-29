from __future__ import annotations

from typing import Any

GATEWAY_OBSERVABILITY_EVENTS: tuple[str, ...] = (
    "gateway.health.reported",
    "gateway.readiness.reported",
    "gateway.request.handled",
)


def build_gateway_health_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "event_name": "gateway.health.reported",
        "service": "petcare-pharmacy-gateway",
        "read_only": True,
    }


def build_gateway_readiness_payload(*, route_count: int) -> dict[str, Any]:
    return {
        "status": "ready",
        "event_name": "gateway.readiness.reported",
        "service": "petcare-pharmacy-gateway",
        "route_count": route_count,
        "read_only": True,
    }


def build_request_observation(
    *,
    path: str,
    method: str,
    actor_user_id: str,
    status: str,
    route_registered: bool,
    tenant_id: str | None,
) -> dict[str, Any]:
    return {
        "event_name": "gateway.request.handled",
        "path": path,
        "method": method,
        "actor_user_id": actor_user_id,
        "status": status,
        "route_registered": route_registered,
        "tenant_id": tenant_id,
    }


__all__ = [
    "GATEWAY_OBSERVABILITY_EVENTS",
    "build_gateway_health_payload",
    "build_gateway_readiness_payload",
    "build_request_observation",
]
