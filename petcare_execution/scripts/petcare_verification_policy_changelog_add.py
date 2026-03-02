#!/usr/bin/env python3
import argparse
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_USAGE = 2
EXIT_MISSING = 3
EXIT_SHA_MISMATCH = 33
EXIT_NO_CHANGELOG = 34

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def must_exist(p: Path, label: str) -> None:
    if not p.exists() or not p.is_file():
        print(f"FATAL: missing {label} at {p}", file=sys.stderr)
        sys.exit(EXIT_MISSING)

def utc_now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def main() -> None:
    ap = argparse.ArgumentParser(description="Append governed entry to VERIFICATION_POLICY_CHANGELOG.md (tool-based, atomic).")
    ap.add_argument("--pack", required=True, help="Exact pack id being allowlisted (e.g., PETCARE-PH44B-CLOSURE)")
    ap.add_argument("--ts", default="", help="UTC timestamp (YYYYMMDDTHHMMSSZ). If empty, uses current UTC.")
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json", help="Policy JSON path.")
    ap.add_argument("--policy-sha", default="FND/VERIFICATION_POLICY.sha256", help="Policy SHA sidecar path.")
    ap.add_argument("--changelog", default="FND/VERIFICATION_POLICY_CHANGELOG.md", help="Changelog path.")
    args = ap.parse_args()

    pack = args.pack.strip()
    if not pack:
        print("FATAL: --pack is empty", file=sys.stderr)
        sys.exit(EXIT_USAGE)

    ts = args.ts.strip() or utc_now_ts()
    if not re.fullmatch(r"\d{8}T\d{6}Z", ts):
        print(f"FATAL: invalid --ts format: {ts} (expected YYYYMMDDTHHMMSSZ)", file=sys.stderr)
        sys.exit(EXIT_USAGE)

    policy_path = Path(args.policy)
    policy_sha_path = Path(getattr(args, "policy_sha"))
    changelog_path = Path(args.changelog)

    must_exist(policy_path, "policy json")
    must_exist(policy_sha_path, "policy sha sidecar")
    must_exist(changelog_path, "changelog")

    # Verify sidecar matches policy *before* writing changelog (no guessing).
    actual = sha256_file(policy_path)
    sidecar = policy_sha_path.read_text(encoding="utf-8").strip().split()[0]
    if actual != sidecar:
        print("FATAL: policy sha mismatch (sidecar does not match policy file).", file=sys.stderr)
        print(f"policy={policy_path}", file=sys.stderr)
        print(f"sidecar={policy_sha_path}", file=sys.stderr)
        print(f"actual_sha256={actual}", file=sys.stderr)
        print(f"sidecar_sha256={sidecar}", file=sys.stderr)
        sys.exit(EXIT_SHA_MISMATCH)

    # Deterministic entry format:
    # PH56|<TS>|ALLOWLIST_ADD|pack=<PACK>|policy_sha256=<SHA>
    entry = f"PH56|{ts}|ALLOWLIST_ADD|pack={pack}|policy_sha256={actual}\n"

    old = changelog_path.read_text(encoding="utf-8")
    if "Verification Policy Changelog" not in old:
        # Not enforcing a header format, but avoid writing to an unexpected file.
        print("FATAL: changelog missing expected marker text; refusing to write (no guessing).", file=sys.stderr)
        sys.exit(EXIT_NO_CHANGELOG)

    if entry in old:
        print("OK: changelog entry already present (noop).")
        return

    tmp = changelog_path.with_suffix(changelog_path.suffix + ".tmp")
    tmp.write_text(old + entry, encoding="utf-8", newline="\n")
    os.replace(tmp, changelog_path)

    print("OK: appended changelog entry")
    print(entry.strip())

if __name__ == "__main__":
    main()
