import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Tuple

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        return {}
    return obj

def _required_pass(reg: Dict[str, Any]) -> Tuple[bool, List[str]]:
    gates = reg.get("gates", {})
    required = reg.get("required_gates_for_pass", [])
    missing: List[str] = []
    for gid in required:
        g = gates.get(gid, {})
        if not isinstance(g, dict) or g.get("status") != "PASS":
            missing.append(gid)
    return (len(missing) == 0, missing)

def _verify_registry_sha(repo_root: str) -> Tuple[bool, str]:
    reg = os.path.join(repo_root, "ops", "ph12_gate_registry.json")
    sha = os.path.join(repo_root, "ops", "ph12_gate_registry.sha256")
    if not os.path.exists(reg):
        return False, "missing_registry"
    if not os.path.exists(sha):
        return False, "missing_sha256_file"
    expected = _sha256_file(reg)
    line = open(sha, "r", encoding="utf-8").read().strip()
    if not line:
        return False, "sha256_file_empty"
    got = line.split()[0]
    if got != expected:
        return False, "sha256_mismatch"
    return True, "ok"

def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reg_path = os.path.join(repo_root, "ops", "ph12_gate_registry.json")
    if not os.path.exists(reg_path):
        print(json.dumps({"ok": False, "reason": "missing_ops/ph12_gate_registry.json"}, indent=2, sort_keys=True))
        return 2

    reg = _load_json(reg_path)
    ok_req, missing = _required_pass(reg)

    ok_sha, sha_reason = _verify_registry_sha(repo_root)

    pol_digest = os.path.join(repo_root, "ops", "ph12_policy_digest.json")
    ok_pol = os.path.exists(pol_digest)

    ok = bool(ok_req and ok_sha and ok_pol)
    out = {
        "ok": ok,
        "pack_id": str(reg.get("pack_id", "PETCARE-PH12-TRUST-CONSOLIDATION")),
        "reason": "all_required_gates_pass" if ok else "gate_or_artifact_missing",
        "details": {
            "missing_required_gates": missing,
            "registry_sha256": sha_reason,
            "policy_digest_exists": ok_pol
        }
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if ok else 3

if __name__ == "__main__":
    raise SystemExit(main())
