from dataclasses import dataclass
from typing import Dict, Optional

from FND.security.actor_id import validate_actor_id, ActorValidationResult

@dataclass(frozen=True)
class AuthDecision:
    ok: bool
    status_code: int
    reason: str
    actor_id: Optional[str] = None

def _get_header(headers: Dict[str, str], key: str) -> Optional[str]:
    if not headers:
        return None
    kl = key.lower()
    for k, v in headers.items():
        if str(k).lower() == kl:
            return v
    return None

def evaluate_request_auth(
    headers: Dict[str, str],
    require_auth_token: bool = False,
    expected_token: Optional[str] = None,
    actor_header: str = "X-Actor-Id",
    token_header: str = "X-Auth-Token",
) -> AuthDecision:
    actor_raw = _get_header(headers, actor_header)
    v: ActorValidationResult = validate_actor_id(actor_raw)
    if not v.ok:
        return AuthDecision(ok=False, status_code=400, reason=v.reason or "actor_validation_failed")

    if require_auth_token:
        token = _get_header(headers, token_header)
        if token is None or str(token).strip() == "":
            return AuthDecision(ok=False, status_code=401, reason="missing_auth_token", actor_id=v.actor_id)
        if expected_token is not None and token != expected_token:
            return AuthDecision(ok=False, status_code=403, reason="invalid_auth_token", actor_id=v.actor_id)

    return AuthDecision(ok=True, status_code=200, reason="ok", actor_id=v.actor_id)
