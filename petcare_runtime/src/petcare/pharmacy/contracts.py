from __future__ import annotations

from typing import Any, Dict

API_CONTRACT_VERSION = "v1"


def success_envelope(
    *,
    surface: str,
    actor_user_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "contract_version": API_CONTRACT_VERSION,
        "status": "success",
        "surface": surface,
        "actor_user_id": actor_user_id,
        "payload": payload,
    }


def error_envelope(
    *,
    surface: str,
    actor_user_id: str,
    error_code: str,
    message: str,
) -> Dict[str, Any]:
    return {
        "contract_version": API_CONTRACT_VERSION,
        "status": "error",
        "surface": surface,
        "actor_user_id": actor_user_id,
        "error": {
            "code": error_code,
            "message": message,
        },
    }
