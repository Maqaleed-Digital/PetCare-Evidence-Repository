from __future__ import annotations

from typing import Any, Mapping

try:
    from fastapi import FastAPI, Request
except Exception:
    FastAPI = None
    Request = None

from .gateway_auth import build_gateway_auth_context
from .gateway_observability import (
    build_gateway_health_payload,
    build_gateway_readiness_payload,
    build_request_observation,
)
from .http_adapter import ROUTE_REGISTRY, handle_request
from .repository import PharmacyRepository

FASTAPI_ROUTE_SPECS: tuple[dict[str, str], ...] = (
    {"method": "GET", "path": "/health"},
    {"method": "GET", "path": "/ready"},
    {"method": "GET", "path": "/api/pharmacy/review/context"},
    {"method": "GET", "path": "/api/pharmacy/review/list"},
    {"method": "GET", "path": "/api/pharmacy/review/handoff"},
    {"method": "GET", "path": "/api/pharmacy/review/handoffs"},
    {"method": "GET", "path": "/api/pharmacy/review/summary"},
    {"method": "GET", "path": "/api/pharmacy/review/queue"},
    {"method": "GET", "path": "/api/pharmacy/review/history"},
    {"method": "GET", "path": "/api/pharmacy/review/timeline"},
    {"method": "GET", "path": "/api/pharmacy/review/follow-up"},
    {"method": "GET", "path": "/api/pharmacy/review/registry"},
    {"method": "GET", "path": "/api/pharmacy/review/operational-summary"},
)

ROUTE_PARAM_SPECS: dict[str, tuple[str, ...]] = {
    "/review/context": ("review_id",),
    "/review/list": ("prescription_id",),
    "/review/handoff": ("review_id",),
    "/review/handoffs": ("tenant_id",),
    "/review/summary": ("review_id",),
    "/review/queue": ("tenant_id",),
    "/review/history": ("review_id",),
    "/review/timeline": ("review_id",),
    "/review/follow-up": ("review_id",),
    "/review/registry": (),
    "/review/operational-summary": ("tenant_id",),
}


def dispatch_read_only_request(
    repo: PharmacyRepository,
    *,
    route_path: str,
    method: str,
    headers: Mapping[str, str],
    params: Mapping[str, Any],
) -> dict[str, Any]:
    auth_context = build_gateway_auth_context(headers, surface=route_path)
    if not auth_context["ok"]:
        actor_user_id = headers.get("x-petcare-actor-user-id", "anonymous")
        return {
            "response": auth_context["error"],
            "observation": build_request_observation(
                path=route_path,
                method=method,
                actor_user_id=actor_user_id,
                status="error",
                route_registered=route_path in ROUTE_REGISTRY,
                tenant_id=headers.get("x-petcare-tenant-id"),
            ),
        }

    response = handle_request(
        repo,
        path=route_path,
        actor_user_id=auth_context["actor_user_id"],
        params=dict(params),
    )
    return {
        "response": response,
        "observation": build_request_observation(
            path=route_path,
            method=method,
            actor_user_id=auth_context["actor_user_id"],
            status=response["status"],
            route_registered=route_path in ROUTE_REGISTRY,
            tenant_id=auth_context.get("tenant_id"),
        ),
    }


def create_fastapi_app(repo: PharmacyRepository):
    if FastAPI is None:
        raise RuntimeError("fastapi is not installed in this environment.")

    app = FastAPI(title="PetCare Pharmacy Gateway", version="1.0.0")

    @app.get("/health")
    async def health():
        return build_gateway_health_payload()

    @app.get("/ready")
    async def ready():
        return build_gateway_readiness_payload(route_count=len(ROUTE_REGISTRY))

    @app.get("/api/pharmacy/review/context")
    async def review_context(request: Request, review_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/context",
            method="GET",
            headers=dict(request.headers),
            params={"review_id": review_id},
        )["response"]

    @app.get("/api/pharmacy/review/list")
    async def review_list(request: Request, prescription_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/list",
            method="GET",
            headers=dict(request.headers),
            params={"prescription_id": prescription_id},
        )["response"]

    @app.get("/api/pharmacy/review/handoff")
    async def review_handoff(request: Request, review_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/handoff",
            method="GET",
            headers=dict(request.headers),
            params={"review_id": review_id},
        )["response"]

    @app.get("/api/pharmacy/review/handoffs")
    async def review_handoffs(request: Request, tenant_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/handoffs",
            method="GET",
            headers=dict(request.headers),
            params={"tenant_id": tenant_id},
        )["response"]

    @app.get("/api/pharmacy/review/summary")
    async def review_summary(request: Request, review_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/summary",
            method="GET",
            headers=dict(request.headers),
            params={"review_id": review_id},
        )["response"]

    @app.get("/api/pharmacy/review/queue")
    async def review_queue(request: Request, tenant_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/queue",
            method="GET",
            headers=dict(request.headers),
            params={"tenant_id": tenant_id},
        )["response"]

    @app.get("/api/pharmacy/review/history")
    async def review_history(request: Request, review_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/history",
            method="GET",
            headers=dict(request.headers),
            params={"review_id": review_id},
        )["response"]

    @app.get("/api/pharmacy/review/timeline")
    async def review_timeline(request: Request, review_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/timeline",
            method="GET",
            headers=dict(request.headers),
            params={"review_id": review_id},
        )["response"]

    @app.get("/api/pharmacy/review/follow-up")
    async def review_follow_up(request: Request, review_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/follow-up",
            method="GET",
            headers=dict(request.headers),
            params={"review_id": review_id},
        )["response"]

    @app.get("/api/pharmacy/review/registry")
    async def review_registry(request: Request):
        return dispatch_read_only_request(
            repo,
            route_path="/review/registry",
            method="GET",
            headers=dict(request.headers),
            params={},
        )["response"]

    @app.get("/api/pharmacy/review/operational-summary")
    async def operational_summary(request: Request, tenant_id: str):
        return dispatch_read_only_request(
            repo,
            route_path="/review/operational-summary",
            method="GET",
            headers=dict(request.headers),
            params={"tenant_id": tenant_id},
        )["response"]

    return app


__all__ = [
    "FASTAPI_ROUTE_SPECS",
    "ROUTE_PARAM_SPECS",
    "create_fastapi_app",
    "dispatch_read_only_request",
]
