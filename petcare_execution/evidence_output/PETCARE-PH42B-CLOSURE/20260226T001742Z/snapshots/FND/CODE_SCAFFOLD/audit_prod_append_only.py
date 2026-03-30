import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

ZERO64 = "0" * 64

def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

def sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

@dataclass(frozen=True)
class AuditRecord:
    seq: int
    timestamp_utc: str
    tenant_id: str
    actor_id: str
    actor_role: str
    event_type: str
    payload: Dict[str, Any]
    prev_hash: str
    record_hash: str

def compute_record_hash(record_without_hash: Dict[str, Any]) -> str:
    s = canonical_json(record_without_hash)
    return sha256_hex(s.encode("utf-8"))

def make_record(
    seq: int,
    tenant_id: str,
    actor_id: str,
    actor_role: str,
    event_type: str,
    payload: Dict[str, Any],
    prev_hash: str,
    timestamp_utc: Optional[str] = None,
) -> AuditRecord:
    ts = timestamp_utc or utc_now_compact()
    base = {
        "seq": seq,
        "timestamp_utc": ts,
        "tenant_id": tenant_id,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "event_type": event_type,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    rh = compute_record_hash(base)
    return AuditRecord(**base, record_hash=rh)

def append_record(ledger: List[AuditRecord], record: AuditRecord) -> List[AuditRecord]:
    if not ledger:
        if record.seq != 1:
            raise ValueError("first record must have seq=1")
        if record.prev_hash != ZERO64:
            raise ValueError("first record must have prev_hash=ZERO64")
        return [record]
    last = ledger[-1]
    if record.seq != last.seq + 1:
        raise ValueError("seq must increment by 1")
    if record.prev_hash != last.record_hash:
        raise ValueError("prev_hash must equal last.record_hash")
    return ledger + [record]

def to_jsonl(ledger: Iterable[AuditRecord]) -> str:
    lines = []
    for r in ledger:
        d = {
            "seq": r.seq,
            "timestamp_utc": r.timestamp_utc,
            "tenant_id": r.tenant_id,
            "actor_id": r.actor_id,
            "actor_role": r.actor_role,
            "event_type": r.event_type,
            "payload": r.payload,
            "prev_hash": r.prev_hash,
            "record_hash": r.record_hash,
        }
        lines.append(canonical_json(d))
    return "\n".join(lines) + ("\n" if lines else "")
