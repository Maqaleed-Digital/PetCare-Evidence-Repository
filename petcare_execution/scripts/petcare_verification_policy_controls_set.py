#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

EXIT_USAGE = 2
EXIT_MISSING = 3
EXIT_SHA_MISMATCH = 33
EXIT_VALIDATION = 34

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)

def must_exist(p: Path, label: str) -> None:
    if not p.exists() or not p.is_file():
        print(f"FATAL: missing {label}: {p}", file=sys.stderr)
        sys.exit(EXIT_MISSING)

def load_policy(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def dump_policy(obj: dict) -> str:
    # Deterministic JSON output
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

def verify_sidecar(policy_path: Path, sidecar_path: Path) -> None:
    actual = sha256_file(policy_path)
    sidecar = sidecar_path.read_text(encoding="utf-8").strip().split()[0]
    if actual != sidecar:
        print("FATAL: policy sha mismatch (sidecar does not match policy).", file=sys.stderr)
        print(f"actual_sha256={actual}", file=sys.stderr)
        print(f"sidecar_sha256={sidecar}", file=sys.stderr)
        sys.exit(EXIT_SHA_MISMATCH)

def main() -> None:
    ap = argparse.ArgumentParser(description="PH59: set meta verifier governance controls (cap/quorum) with deterministic SHA update.")
    ap.add_argument("--cap", type=int, required=True, help="Max allowed meta verifiers in allowlist (>= current count).")
    ap.add_argument("--quorum", type=int, required=True, help="Required quorum (>=1 and <= allowlist count). Default recommend 1 initially.")
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json")
    ap.add_argument("--policy-sha", default="FND/VERIFICATION_POLICY.sha256")
    args = ap.parse_args()

    if args.cap < 1:
        print("FATAL: --cap must be >= 1", file=sys.stderr); sys.exit(EXIT_USAGE)
    if args.quorum < 1:
        print("FATAL: --quorum must be >= 1", file=sys.stderr); sys.exit(EXIT_USAGE)

    policy_path = Path(args.policy)
    sidecar_path = Path(getattr(args, "policy_sha"))
    must_exist(policy_path, "policy")
    must_exist(sidecar_path, "policy sidecar")

    # Verify sidecar before mutating (no guessing)
    verify_sidecar(policy_path, sidecar_path)

    pol = load_policy(policy_path)
    allow = pol.get("meta_verifiers_allowlist", [])
    if not isinstance(allow, list) or any((not isinstance(x, str) or not x.strip()) for x in allow):
        print("FATAL: meta_verifiers_allowlist must be list[str]", file=sys.stderr)
        sys.exit(EXIT_VALIDATION)

    allow_count = len(allow)
    if args.cap < allow_count:
        print(f"FATAL: cap={args.cap} < current_allowlist_count={allow_count} (refusing to create invalid policy).", file=sys.stderr)
        sys.exit(EXIT_VALIDATION)
    if args.quorum > allow_count:
        print(f"FATAL: quorum={args.quorum} > current_allowlist_count={allow_count} (refusing).", file=sys.stderr)
        sys.exit(EXIT_VALIDATION)

    # Add PH59 fields (backward-compatible additions)
    pol["meta_verifiers_allowlist_cap"] = args.cap
    pol["meta_verifiers_quorum"] = args.quorum

    out_text = dump_policy(pol)
    # Write policy atomically
    atomic_write_text(policy_path, out_text)

    # Write sha sidecar deterministically (content is "SHA256  filename")
    sha = sha256_bytes(out_text.encode("utf-8"))
    atomic_write_text(sidecar_path, f"{sha}  {policy_path.name}\n")

    changed = True
    print("OK: policy controls set")
    print(f"changed={str(changed).lower()}")
    print(f"allowlist_count={allow_count}")
    print(f"cap={args.cap}")
    print(f"quorum={args.quorum}")
    print(f"policy_sha256={sha}")

if __name__ == "__main__":
    main()
