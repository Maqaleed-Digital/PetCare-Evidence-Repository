import json
import os
import sys
from typing import Any, Dict, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from FND.security.audit_chain import verify_hash_chain  # noqa: E402

def main() -> int:
    data: Dict[str, Any] = {"ok": True, "reason": "no_input", "details": {}}

    try:
        raw = sys.stdin.read()
        if raw.strip():
            obj = json.loads(raw)
            events = obj.get("events", [])
            if not isinstance(events, list):
                data = {"ok": False, "reason": "events_not_list", "details": {}}
                print(json.dumps(data, indent=2, sort_keys=True))
                return 2

            r = verify_hash_chain(events)
            data = {
                "ok": bool(r.ok),
                "reason": str(r.reason),
                "details": {
                    "index": int(r.index),
                    "expected": r.expected,
                    "actual": r.actual,
                    "event_count": len(events),
                },
            }
            print(json.dumps(data, indent=2, sort_keys=True))
            return 0 if r.ok else 3

        print(json.dumps(data, indent=2, sort_keys=True))
        return 0

    except Exception as e:
        data = {"ok": False, "reason": f"exception:{type(e).__name__}", "details": {"msg": str(e)}}
        print(json.dumps(data, indent=2, sort_keys=True))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
