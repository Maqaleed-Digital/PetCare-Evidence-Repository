#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

EXIT_FAIL = 59
EXIT_MISSING = 3
EXIT_SHA_MISMATCH = 33

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    policy_path = Path("FND/VERIFICATION_POLICY.json")
    sidecar_path = Path("FND/VERIFICATION_POLICY.sha256")

    if not policy_path.exists() or not sidecar_path.exists():
        print("FATAL: missing policy or sidecar", file=sys.stderr)
        sys.exit(EXIT_MISSING)

    actual = sha256_file(policy_path)
    sidecar = sidecar_path.read_text(encoding="utf-8").strip().split()[0]
    if actual != sidecar:
        print("FATAL: policy sha mismatch", file=sys.stderr)
        sys.exit(EXIT_SHA_MISMATCH)

    pol = json.loads(policy_path.read_text(encoding="utf-8"))
    allow = pol.get("meta_verifiers_allowlist", [])
    cap = pol.get("meta_verifiers_allowlist_cap", None)
    quorum = pol.get("meta_verifiers_quorum", None)

    if not isinstance(allow, list) or any((not isinstance(x, str) or not x.strip()) for x in allow):
        print("FAIL: meta_verifiers_allowlist invalid", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    if cap is not None:
        if not isinstance(cap, int) or cap < 1:
            print("FAIL: meta_verifiers_allowlist_cap must be int>=1", file=sys.stderr)
            sys.exit(EXIT_FAIL)
        if len(allow) > cap:
            print(f"FAIL: allowlist_count={len(allow)} exceeds cap={cap}", file=sys.stderr)
            sys.exit(EXIT_FAIL)

    if quorum is not None:
        if not isinstance(quorum, int) or quorum < 1:
            print("FAIL: meta_verifiers_quorum must be int>=1", file=sys.stderr)
            sys.exit(EXIT_FAIL)
        if quorum > len(allow):
            print(f"FAIL: quorum={quorum} > allowlist_count={len(allow)}", file=sys.stderr)
            sys.exit(EXIT_FAIL)

    print("OK: PH59 meta verifier governance guard PASS")
    print(f"allowlist_count={len(allow)}")
    print(f"cap={cap}")
    print(f"quorum={quorum}")
    print(f"policy_sha256={actual}")

if __name__ == "__main__":
    main()
