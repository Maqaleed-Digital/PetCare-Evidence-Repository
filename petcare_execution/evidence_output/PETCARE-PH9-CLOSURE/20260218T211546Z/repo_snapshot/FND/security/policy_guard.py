import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from FND.security.auth_stub import evaluate_request_auth, AuthDecision

DEFAULT_POLICY_PATH = os.path.join(os.path.dirname(__file__), "policy.json")

@dataclass(frozen=True)
class Policy:
    schema: str
    mode: str
    require_auth_token: bool
    expected_token: Optional[str]
    actor_header: str
    token_header: str
    deny_by_default: bool

def load_policy(path: Optional[str] = None) -> Policy:
    p = path if path is not None else DEFAULT_POLICY_PATH
    with open(p, "r", encoding="utf-8") as f:
        obj = json.load(f)

    auth = obj.get("auth") if isinstance(obj, dict) else {}
    schema = str(obj.get("schema", "UNKNOWN"))
    mode = str(obj.get("mode", "UNKNOWN"))
    require_auth = bool(auth.get("require_auth_token", False))
    expected = auth.get("expected_token", None)
    expected_token = str(expected) if expected is not None else None
    actor_header = str(auth.get("actor_header", "X-Actor-Id"))
    token_header = str(auth.get("token_header", "X-Auth-Token"))
    deny_default = bool(obj.get("deny_by_default", False))

    return Policy(
        schema=schema,
        mode=mode,
        require_auth_token=require_auth,
        expected_token=expected_token,
        actor_header=actor_header,
        token_header=token_header,
        deny_by_default=deny_default,
    )

def evaluate_with_policy(headers: Dict[str, str], policy: Policy) -> AuthDecision:
    if policy.deny_by_default:
        decision = evaluate_request_auth(
            headers=headers,
            require_auth_token=True,
            expected_token=policy.expected_token,
            actor_header=policy.actor_header,
            token_header=policy.token_header,
        )
        if not decision.ok:
            return decision
        return decision

    return evaluate_request_auth(
        headers=headers,
        require_auth_token=policy.require_auth_token,
        expected_token=policy.expected_token,
        actor_header=policy.actor_header,
        token_header=policy.token_header,
    )

def decision_to_http(decision: AuthDecision) -> Tuple[Dict[str, Any], int]:
    if decision.ok:
        return {"ok": True, "actor_id": decision.actor_id}, 200
    return {"ok": False, "reason": decision.reason}, int(decision.status_code)
