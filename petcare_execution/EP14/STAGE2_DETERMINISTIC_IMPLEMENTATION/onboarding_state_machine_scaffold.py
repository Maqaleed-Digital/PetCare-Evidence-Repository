from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, List


ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    "INACTIVE": ["SANDBOX_ENABLED", "REVOKED"],
    "SANDBOX_ENABLED": ["VALIDATING", "REVOKED"],
    "VALIDATING": ["CERTIFIED", "REVOKED"],
    "CERTIFIED": ["ACTIVE", "REVOKED"],
    "ACTIVE": ["SUSPENDED", "REVOKED"],
    "SUSPENDED": ["ACTIVE", "REVOKED"],
    "REVOKED": [],
}


@dataclass(frozen=True)
class TransitionResult:
    from_state: str
    to_state: str
    allowed: bool
    reason: str


def validate_transition(from_state: str, to_state: str, certification_passed: bool = False) -> TransitionResult:
    allowed_targets = ALLOWED_TRANSITIONS.get(from_state)
    if allowed_targets is None:
        raise ValueError(f"Unsupported from_state: {from_state}")
    if to_state not in allowed_targets:
        return TransitionResult(from_state=from_state, to_state=to_state, allowed=False, reason="TRANSITION_NOT_ALLOWED")
    if to_state == "ACTIVE" and not certification_passed:
        return TransitionResult(from_state=from_state, to_state=to_state, allowed=False, reason="CERTIFICATION_REQUIRED_BEFORE_ACTIVE")
    return TransitionResult(from_state=from_state, to_state=to_state, allowed=True, reason="TRANSITION_ALLOWED")


if __name__ == "__main__":
    samples: List[Dict[str, object]] = [
        asdict(validate_transition("INACTIVE", "SANDBOX_ENABLED")),
        asdict(validate_transition("CERTIFIED", "ACTIVE", certification_passed=True)),
        asdict(validate_transition("CERTIFIED", "ACTIVE", certification_passed=False)),
    ]
    print(json.dumps(samples, indent=2, sort_keys=True))
