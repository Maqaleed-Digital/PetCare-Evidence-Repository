import re
from dataclasses import dataclass
from typing import Optional

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)

@dataclass(frozen=True)
class ActorValidationResult:
    ok: bool
    actor_id: Optional[str] = None
    reason: Optional[str] = None

def validate_actor_id(actor_id: Optional[str]) -> ActorValidationResult:
    if actor_id is None:
        return ActorValidationResult(ok=False, reason="missing_actor_id")
    s = str(actor_id).strip()
    if not s:
        return ActorValidationResult(ok=False, reason="empty_actor_id")
    if not _UUID_RE.match(s):
        return ActorValidationResult(ok=False, reason="invalid_actor_id_format")
    return ActorValidationResult(ok=True, actor_id=s)
