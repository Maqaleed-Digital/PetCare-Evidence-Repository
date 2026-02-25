import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

@dataclass(frozen=True)
class ChainVerifyResult:
    ok: bool
    reason: str
    index: int
    expected: Optional[str]
    actual: Optional[str]

def _canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def compute_event_hash(prev_hash: str, event: Dict[str, Any]) -> str:
    payload = {
        "prev_hash": prev_hash,
        "event": event,
    }
    b = _canon(payload).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

def verify_hash_chain(events: List[Dict[str, Any]], genesis: str = "GENESIS") -> ChainVerifyResult:
    prev = genesis
    for i, ev in enumerate(events):
        ev_prev = ev.get("prev_hash")
        ev_hash = ev.get("hash")

        if ev_prev is None or ev_hash is None:
            return ChainVerifyResult(ok=False, reason="missing_hash_fields", index=i, expected=None, actual=None)

        if str(ev_prev) != str(prev):
            return ChainVerifyResult(ok=False, reason="prev_hash_mismatch", index=i, expected=str(prev), actual=str(ev_prev))

        core = dict(ev)
        core.pop("hash", None)
        core.pop("prev_hash", None)

        expected = compute_event_hash(prev, core)
        if str(ev_hash) != str(expected):
            return ChainVerifyResult(ok=False, reason="hash_mismatch", index=i, expected=str(expected), actual=str(ev_hash))

        prev = expected

    return ChainVerifyResult(ok=True, reason="ok", index=len(events) - 1 if events else -1, expected=None, actual=None)
