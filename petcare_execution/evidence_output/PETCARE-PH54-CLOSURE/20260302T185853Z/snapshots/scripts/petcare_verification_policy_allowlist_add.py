#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

SCHEMA = "petcare.verification_policy.v1"
PACK_RE = re.compile(r"^PETCARE-[A-Z0-9]+-CLOSURE$")

def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())

def load_json(path: str) -> Dict[str, Any]:
    return json.load(open(path, "r", encoding="utf-8"))

def write_json_deterministic(path: str, obj: Dict[str, Any]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)

def read_sha_sidecar_format(path: str) -> Tuple[str, str]:
    """
    Preserve existing sidecar format.
    Returns (mode, tail)
      mode="hash_only": file contains only the hash token
      mode="hash_plus": file contains hash + whitespace + tail (e.g. filename)
    """
    if not os.path.exists(path):
        return ("hash_only", "")
    txt = open(path, "r", encoding="utf-8").read().strip("\n")
    if not txt.strip():
        return ("hash_only", "")
    parts = txt.strip().split(None, 1)
    if len(parts) == 1:
        return ("hash_only", "")
    return ("hash_plus", parts[1])

def write_sha_sidecar(path: str, digest_hex: str, mode: str, tail: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{64}", digest_hex):
        fail("internal: digest not 64-hex", 90)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        if mode == "hash_plus" and tail.strip():
            f.write(f"{digest_hex}  {tail.strip()}\n")
        else:
            f.write(f"{digest_hex}\n")
    os.replace(tmp, path)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True, help="Pack id to allow as meta verifier (e.g., PETCARE-PH99-CLOSURE)")
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json")
    ap.add_argument("--policy_sha", default="FND/VERIFICATION_POLICY.sha256")
    args = ap.parse_args()

    pack = args.pack.strip()
    if not PACK_RE.match(pack):
        fail(f"invalid pack id (must match {PACK_RE.pattern}): {pack}", 10)

    if not os.path.isfile(args.policy):
        fail(f"missing policy file: {args.policy}", 11)

    pol = load_json(args.policy)
    if pol.get("schema") != SCHEMA:
        fail(f"policy schema mismatch: {pol.get('schema')}", 12)

    allow = pol.get("meta_verifiers_allowlist")
    if allow is None:
        allow = []
    if not isinstance(allow, list):
        fail("policy meta_verifiers_allowlist must be a list", 13)

    # Normalize to sorted unique list
    allow_set = set()
    for v in allow:
        if not isinstance(v, str) or not v:
            fail("allowlist contains non-string/empty entry", 14)
        if not PACK_RE.match(v):
            fail(f"allowlist contains invalid pack id: {v}", 15)
        allow_set.add(v)

    before = sorted(allow_set)
    allow_set.add(pack)
    after = sorted(allow_set)

    pol["meta_verifiers_allowlist"] = after
    write_json_deterministic(args.policy, pol)

    # Update sha sidecar (preserve format if file existed)
    mode, tail = read_sha_sidecar_format(args.policy_sha)
    digest = sha256_file(args.policy)
    write_sha_sidecar(args.policy_sha, digest, mode, tail)

    changed = "false" if before == after else "true"
    print("OK policy allowlist updated")
    print(f"changed={changed}")
    print(f"added_pack={pack}")
    print(f"allowlist_count={len(after)}")
    print(f"policy_sha256={digest}")

if __name__ == "__main__":
    main()
