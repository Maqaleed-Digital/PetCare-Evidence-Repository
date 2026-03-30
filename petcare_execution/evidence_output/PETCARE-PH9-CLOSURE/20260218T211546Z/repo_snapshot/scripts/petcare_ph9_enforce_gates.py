import json
import os
import sys
from typing import Any, Dict, List

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python3 scripts/petcare_ph9_enforce_gates.py <ops/ph9_gate_registry.json>")
        return 2

    p = sys.argv[1]
    with open(p, "r", encoding="utf-8") as f:
        reg = json.load(f)

    required: List[str] = list(reg.get("required_gates", []))
    gates: Dict[str, Any] = dict(reg.get("gates", {}))

    missing = [g for g in required if g not in gates]
    if missing:
        print(json.dumps({"ok": False, "reason": "missing_gate_entries", "missing": missing}, indent=2, sort_keys=True))
        return 2

    not_pass = [g for g in required if str(gates.get(g, {}).get("status", "")).upper() != "PASS"]
    if not_pass:
        print(json.dumps({"ok": False, "reason": "gates_not_pass", "not_pass": not_pass}, indent=2, sort_keys=True))
        return 3

    print(json.dumps({"ok": True, "reason": "all_required_gates_pass", "pack_id": reg.get("pack_id")}, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
