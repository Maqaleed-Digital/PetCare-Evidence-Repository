import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

def _sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def _canonical_json(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

@dataclass(frozen=True)
class AppendResult:
    ok: bool
    offset: Optional[int] = None
    hash: Optional[str] = None
    prev_hash: Optional[str] = None
    reason: Optional[str] = None

class ImmutableAuditLog:
    def __init__(self, path: str, enable_hash_chain: bool = True) -> None:
        self.path = path
        self.enable_hash_chain = enable_hash_chain
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def _read_last_hash(self) -> Optional[str]:
        if not os.path.exists(self.path):
            return None
        last = None
        try:
            with open(self.path, "rb") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line.decode("utf-8"))
                        last = obj.get("hash")
                    except Exception:
                        continue
        except Exception:
            return None
        return last if isinstance(last, str) and last else None

    def append(self, event: Dict[str, Any], actor_id: Optional[str] = None) -> AppendResult:
        if not isinstance(event, dict):
            return AppendResult(ok=False, reason="event_must_be_dict")

        prev_hash = self._read_last_hash() if self.enable_hash_chain else None

        record: Dict[str, Any] = {
            "ts": int(time.time()),
            "actor_id": actor_id,
            "event": event,
        }
        if self.enable_hash_chain:
            record["prev_hash"] = prev_hash

        payload = _canonical_json(record)
        rec_hash = _sha256_hex(payload)
        record["hash"] = rec_hash

        line = (json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

        try:
            with open(self.path, "ab") as f:
                offset = f.tell()
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
            return AppendResult(ok=True, offset=offset, hash=rec_hash, prev_hash=prev_hash)
        except Exception as e:
            return AppendResult(ok=False, reason=f"append_failed:{type(e).__name__}")

    def verify_chain(self) -> Tuple[bool, str]:
        if not os.path.exists(self.path):
            return True, "empty_ok"
        prev = None
        i = 0
        try:
            with open(self.path, "rb") as f:
                for raw in f:
                    i += 1
                    line = raw.strip()
                    if not line:
                        continue
                    obj = json.loads(line.decode("utf-8"))
                    got_hash = obj.get("hash")
                    exp_prev = obj.get("prev_hash") if self.enable_hash_chain else None

                    record = {
                        "ts": obj.get("ts"),
                        "actor_id": obj.get("actor_id"),
                        "event": obj.get("event"),
                    }
                    if self.enable_hash_chain:
                        record["prev_hash"] = exp_prev

                    payload = _canonical_json(record)
                    exp_hash = _sha256_hex(payload)

                    if got_hash != exp_hash:
                        return False, f"hash_mismatch_line_{i}"
                    if self.enable_hash_chain:
                        if exp_prev != prev:
                            return False, f"prev_hash_mismatch_line_{i}"
                        prev = got_hash
            return True, "ok"
        except Exception as e:
            return False, f"verify_failed:{type(e).__name__}"
