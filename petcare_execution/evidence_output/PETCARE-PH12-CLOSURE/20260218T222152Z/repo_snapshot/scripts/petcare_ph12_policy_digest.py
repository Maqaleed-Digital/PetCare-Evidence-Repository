import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def _canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    policy_path = os.path.join(repo_root, "FND", "security", "policy.json")
    out_path = os.path.join(repo_root, "ops", "ph12_policy_digest.json")

    if not os.path.exists(policy_path):
        print(f"ERROR: missing {policy_path}")
        return 2

    with open(policy_path, "r", encoding="utf-8") as f:
        policy = json.load(f)

    canon = _canonical_json_bytes(policy)
    digest = _sha256_bytes(canon)

    payload: Dict[str, Any] = {
        "schema": str(policy.get("schema", "UNKNOWN")) if isinstance(policy, dict) else "UNKNOWN",
        "mode": str(policy.get("mode", "UNKNOWN")) if isinstance(policy, dict) else "UNKNOWN",
        "policy_path": "FND/security/policy.json",
        "policy_sha256_canonical": digest,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")

    os.replace(tmp, out_path)
    print(out_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
