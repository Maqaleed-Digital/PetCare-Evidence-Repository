import json
import hashlib
from typing import Any, Dict, List, Tuple

ZERO64 = "0" * 64

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

def sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def compute_record_hash_without_record_hash(rec: Dict[str, Any]) -> str:
    base = dict(rec)
    base.pop("record_hash", None)
    s = canonical_json(base)
    return sha256_hex(s.encode("utf-8"))

def verify_chain(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
    if not records:
        return True, "EMPTY_OK"
    for i, rec in enumerate(records):
        seq_expected = i + 1
        if rec.get("seq") != seq_expected:
            return False, f"SEQ_MISMATCH idx={i} have={rec.get('seq')} want={seq_expected}"
        if i == 0:
            if rec.get("prev_hash") != ZERO64:
                return False, "FIRST_PREV_HASH_NOT_ZERO64"
        else:
            prev = records[i - 1]
            if rec.get("prev_hash") != prev.get("record_hash"):
                return False, f"PREV_HASH_MISMATCH idx={i}"
        rh_have = rec.get("record_hash")
        rh_want = compute_record_hash_without_record_hash(rec)
        if rh_have != rh_want:
            return False, f"RECORD_HASH_MISMATCH idx={i}"
    return True, "PASS"

def parse_jsonl(s: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for line in s.splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out
