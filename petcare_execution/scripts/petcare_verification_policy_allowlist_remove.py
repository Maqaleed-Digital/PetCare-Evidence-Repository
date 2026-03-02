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
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

def verify_sidecar(policy_path: Path, sidecar_path: Path) -> None:
    actual = sha256_file(policy_path)
    sidecar = sidecar_path.read_text(encoding="utf-8").strip().split()[0]
    if actual != sidecar:
        print("FATAL: policy sha mismatch (sidecar does not match policy).", file=sys.stderr)
        sys.exit(EXIT_SHA_MISMATCH)

def main() -> None:
    ap = argparse.ArgumentParser(description="PH59: remove/revoke a meta verifier from allowlist deterministically (updates sha).")
    ap.add_argument("--pack", required=True, help="Exact pack id to remove")
    ap.add_argument("--force", action="store_true", help="Emergency revoke: allow quorum violation check bypass? (Still refuses if would make policy invalid.)")
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json")
    ap.add_argument("--policy-sha", default="FND/VERIFICATION_POLICY.sha256")
    args = ap.parse_args()

    pack = args.pack.strip()
    if not pack:
        print("FATAL: --pack empty", file=sys.stderr); sys.exit(EXIT_USAGE)

    policy_path = Path(args.policy)
    sidecar_path = Path(getattr(args, "policy_sha"))
    must_exist(policy_path, "policy")
    must_exist(sidecar_path, "policy sidecar")

    verify_sidecar(policy_path, sidecar_path)

    pol = load_policy(policy_path)
    allow = pol.get("meta_verifiers_allowlist", [])
    if not isinstance(allow, list):
        print("FATAL: meta_verifiers_allowlist not list", file=sys.stderr); sys.exit(EXIT_VALIDATION)

    if pack not in allow:
        print("OK: pack not present (noop)")
        return

    new_allow = [x for x in allow if x != pack]
    pol["meta_verifiers_allowlist"] = new_allow

    # Enforce cap/quorum consistency if fields exist
    cap = pol.get("meta_verifiers_allowlist_cap", None)
    quorum = pol.get("meta_verifiers_quorum", None)
    if cap is not None and isinstance(cap, int) and cap < len(new_allow):
        print("FATAL: resulting allowlist exceeds cap (invalid).", file=sys.stderr)
        sys.exit(EXIT_VALIDATION)
    if quorum is not None and isinstance(quorum, int) and quorum > len(new_allow):
        # Even with --force, do not allow an invalid policy to be written.
        print("FATAL: resulting allowlist would violate quorum (invalid).", file=sys.stderr)
        sys.exit(EXIT_VALIDATION)

    out_text = dump_policy(pol)
    atomic_write_text(policy_path, out_text)
    sha = sha256_bytes(out_text.encode("utf-8"))
    atomic_write_text(sidecar_path, f"{sha}  {policy_path.name}\n")

    print("OK: removed pack from allowlist")
    print(f"removed={pack}")
    print(f"allowlist_count={len(new_allow)}")
    print(f"policy_sha256={sha}")

if __name__ == "__main__":
    main()
