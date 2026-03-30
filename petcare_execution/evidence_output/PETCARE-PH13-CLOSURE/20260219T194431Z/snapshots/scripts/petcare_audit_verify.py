import json
import os
import sys
from typing import Any, Dict

from FND.audit.immutable_audit import ImmutableAuditLog

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python3 scripts/petcare_audit_verify.py <audit_jsonl_path>")
        return 2

    p = sys.argv[1]
    log = ImmutableAuditLog(p, enable_hash_chain=True)
    ok, msg = log.verify_chain()

    report: Dict[str, Any] = {
        "audit_path": os.path.abspath(p),
        "ok": bool(ok),
        "message": msg,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
