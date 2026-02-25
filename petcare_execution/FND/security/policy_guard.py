import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from FND.security.auth_stub import evaluate_request_auth, AuthDecision

DEFAULT_POLICY_PATH = os.path.join(os.path.dirname(__file__), "policy.json")
ENV_EXPECTED_TOKEN = "PETCARE_EXPECTED_TOKEN"
ENV_POLICY_PATH = "PETCARE_POLICY_PATH"

@dataclass(frozen=True)
class Policy:
    schema: str
    mode: str
    require_auth_token: bool
    expected_token: Optional[str]
    actor_header: str
    token_header: str
    deny_by_default: bool
    pii_requires_watermark: bool
    pii_requires_encryption: bool

def load_policy(path: Optional[str] = None) -> Policy:
    p = path
    if p is None:
        env_p = os.environ.get(ENV_POLICY_PATH)
        if env_p is not None and str(env_p).strip():
            p = str(env_p).strip()
        else:
            p = DEFAULT_POLICY_PATH

    with open(p, "r", encoding="utf-8") as f:
        obj = json.load(f)

    if not isinstance(obj, dict):
        obj = {}

    auth = obj.get("auth")
    if not isinstance(auth, dict):
        auth = {}

    schema = str(obj.get("schema", "UNKNOWN"))
    mode = str(obj.get("mode", "UNKNOWN")).upper()

    require_auth = bool(auth.get("require_auth_token", False))
    expected = auth.get("expected_token", None)
    expected_token = str(expected) if expected is not None else None

    actor_header = str(auth.get("actor_header", "X-Actor-Id"))
    token_header = str(auth.get("token_header", "X-Auth-Token"))
    deny_default = bool(obj.get("deny_by_default", False))

    export = obj.get("evidence_export")
    if not isinstance(export, dict):
        export = {}

    pii_requires_watermark = bool(export.get("pii_requires_watermark", True))
    pii_requires_encryption = bool(export.get("pii_requires_encryption", True))

    if mode == "TRUST":
        deny_default = True
        require_auth = True

    if expected_token is None:
        env_token = os.environ.get(ENV_EXPECTED_TOKEN)
        if env_token is not None and str(env_token).strip():
            expected_token = str(env_token).strip()

    return Policy(
        schema=schema,
        mode=mode,
        require_auth_token=require_auth,
        expected_token=expected_token,
        actor_header=actor_header,
        token_header=token_header,
        deny_by_default=deny_default,
        pii_requires_watermark=pii_requires_watermark,
        pii_requires_encryption=pii_requires_encryption,
    )

def evaluate_with_policy(headers: Dict[str, str], policy: Policy) -> AuthDecision:
    require_auth = policy.require_auth_token or policy.deny_by_default
    return evaluate_request_auth(
        headers=headers,
        require_auth_token=require_auth,
        expected_token=policy.expected_token,
        actor_header=policy.actor_header,
        token_header=policy.token_header,
    )

def decision_to_http(decision: AuthDecision) -> Tuple[Dict[str, Any], int]:
    if decision.ok:
        return {"ok": True, "actor_id": decision.actor_id}, 200
    return {"ok": False, "reason": decision.reason}, int(decision.status_code)

def enforce_evidence_export(policy: Policy, include_pii: bool, watermark: bool, encryption: bool) -> Tuple[bool, str, int]:
    if not include_pii:
        return True, "ok_non_pii", 200

    if policy.pii_requires_watermark and not watermark:
        return False, "pii_requires_watermark", 400

    if policy.pii_requires_encryption and not encryption:
        return False, "pii_requires_encryption", 400

    return True, "ok_pii_requirements_met", 200
