from __future__ import annotations

from typing import Any, Mapping

from .contracts import error_envelope

GATEWAY_AUTH_POLICIES: tuple[str, ...] = (
    "AUTHORIZATION_BEARER_REQUIRED",
    "ACTOR_HEADER_REQUIRED",
    "TENANT_HEADER_OPTIONAL",
)

ACTOR_HEADER_NAME = "x-petcare-actor-user-id"
TENANT_HEADER_NAME = "x-petcare-tenant-id"


def _get_header(headers: Mapping[str, str], name: str) -> str | None:
    return headers.get(name) or headers.get(name.title()) or headers.get(name.upper())


def build_gateway_auth_context(
    headers: Mapping[str, str],
    *,
    surface: str,
) -> dict[str, Any]:
    authorization = _get_header(headers, "authorization")
    actor_user_id = _get_header(headers, ACTOR_HEADER_NAME)
    tenant_id = _get_header(headers, TENANT_HEADER_NAME)

    if not authorization:
        return {
            "ok": False,
            "error": error_envelope(
                surface=surface,
                actor_user_id=actor_user_id or "anonymous",
                error_code="AUTHORIZATION_HEADER_MISSING",
                message="Authorization header is required.",
            ),
        }

    if not authorization.startswith("Bearer "):
        return {
            "ok": False,
            "error": error_envelope(
                surface=surface,
                actor_user_id=actor_user_id or "anonymous",
                error_code="AUTHORIZATION_BEARER_INVALID",
                message="Authorization header must use Bearer token format.",
            ),
        }

    if not actor_user_id:
        return {
            "ok": False,
            "error": error_envelope(
                surface="http_adapter",
                actor_user_id="anonymous",
                error_code="ACTOR_HEADER_MISSING",
                message="X-PetCare-Actor-User-Id header is required.",
            ),
        }

    return {
        "ok": True,
        "actor_user_id": actor_user_id,
        "tenant_id": tenant_id,
        "authorization_scheme": "Bearer",
    }


__all__ = [
    "ACTOR_HEADER_NAME",
    "GATEWAY_AUTH_POLICIES",
    "TENANT_HEADER_NAME",
    "build_gateway_auth_context",
]
