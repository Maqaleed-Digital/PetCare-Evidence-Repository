from typing import Any, Dict, Optional, Tuple

from FND.security.policy_guard import load_policy, evaluate_with_policy, decision_to_http

def guard_flask_request(headers: Dict[str, str], policy_path: Optional[str] = None) -> Tuple[bool, Dict[str, Any], int]:
    policy = load_policy(policy_path)
    decision = evaluate_with_policy(headers=headers, policy=policy)
    body, code = decision_to_http(decision)
    return bool(decision.ok), body, int(code)
