#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
from typing import Any, Dict, List

SCHEMA = "petcare.verification_policy.v1"
PACK_RE = re.compile(r"^PETCARE-[A-Z0-9]+-CLOSURE$")

def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_sidecar_first_token(path: str) -> str:
    txt = open(path, "r", encoding="utf-8").read().strip()
    if not txt:
        fail(f"empty sha sidecar: {path}", 3)
    tok = txt.split()[0].strip()
    if not re.fullmatch(r"[0-9a-f]{64}", tok):
        fail(f"sha sidecar first token not 64-hex: {path}", 4)
    return tok

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json")
    ap.add_argument("--policy_sha", default="FND/VERIFICATION_POLICY.sha256")
    args = ap.parse_args()

    if not os.path.isfile(args.policy):
        fail(f"missing policy file: {args.policy}", 10)
    if not os.path.isfile(args.policy_sha):
        fail(f"missing policy sha file: {args.policy_sha}", 11)

    want = read_sidecar_first_token(args.policy_sha)
    got = sha256_file(args.policy)
    if got != want:
        fail(f"policy sha mismatch: want={want} got={got}", 12)

    try:
        pol = json.load(open(args.policy, "r", encoding="utf-8"))
    except Exception as e:
        fail(f"policy json invalid: {e}", 13)

    if pol.get("schema") != SCHEMA:
        fail(f"policy schema mismatch: {pol.get('schema')}", 14)

    allow = pol.get("meta_verifiers_allowlist")
    if not isinstance(allow, list):
        fail("policy meta_verifiers_allowlist must be a list", 15)

    for i, v in enumerate(allow):
        if not isinstance(v, str) or not v:
            fail(f"allowlist entry[{i}] must be non-empty string", 16)
        if not PACK_RE.match(v):
            fail(f"allowlist entry[{i}] invalid pack id: {v}", 17)

    # Deterministic: ensure unique/sorted (policy may enforce in future; here we just validate)
    if len(allow) != len(set(allow)):
        fail("allowlist contains duplicates (must be unique)", 18)
    if allow != sorted(allow):
        fail("allowlist must be sorted ascending", 19)

    print("OK verification policy PASS")
    print(f"policy={args.policy}")
    print(f"policy_sha={args.policy_sha}")
    print(f"allowlist_count={len(allow)}")

if __name__ == "__main__":
    main()
