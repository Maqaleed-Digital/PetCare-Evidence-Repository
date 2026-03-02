#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="strict")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy_sha_path", default="FND/VERIFICATION_POLICY.sha256")
    ap.add_argument("--changelog_path", default="FND/VERIFICATION_POLICY_CHANGELOG.md")
    ap.add_argument("--require_last_entry_matches", action="store_true",
                    help="Require changelog last entry to contain policy_sha256=<current sha> (strict)")
    args = ap.parse_args()

    policy_sha_p = Path(args.policy_sha_path)
    changelog_p = Path(args.changelog_path)

    if not policy_sha_p.exists():
        fail(f"missing policy sha sidecar: {policy_sha_p}")

    if not changelog_p.exists():
        fail(f"missing changelog: {changelog_p}")

    policy_sha = read_text(policy_sha_p).strip().split()[0]
    if not HEX64_RE.match(policy_sha):
        fail(f"policy sha sidecar invalid (expected 64-hex): {policy_sha}")

    txt = read_text(changelog_p)

    # Must contain at least one 'policy_sha256=' occurrence
    if "policy_sha256=" not in txt:
        fail("changelog missing any policy_sha256= entries")

    # Strict mode: last entry must match current sha
    if args.require_last_entry_matches:
        lines = [ln.strip() for ln in txt.splitlines()]
        # scan from bottom for first policy_sha256=
        found = None
        for ln in reversed(lines):
            if ln.startswith("policy_sha256="):
                found = ln.split("=", 1)[1].strip()
                break
        if not found:
            fail("changelog has no parsable policy_sha256= line")
        if found != policy_sha:
            fail(f"changelog last policy_sha256 does not match sidecar (want={policy_sha} got={found})")

    print("OK verification policy changelog guard PASS")
    print(f"policy_sha256={policy_sha}")
    print(f"changelog_path={changelog_p}")

if __name__ == "__main__":
    main()
