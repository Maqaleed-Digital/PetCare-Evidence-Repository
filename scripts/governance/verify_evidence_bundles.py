"""Verify every evidence bundle under petcare_execution/EVIDENCE.

Two manifest schemes exist in this repository and a verifier that knows only
one of them fails on the other for a reason that is not drift:

  SCHEME_A  `EVIDENCE_SHA256.txt` is a per-file list, `<sha256>  <filename>`.
            Verifiable with `sha256sum -c`.

  SCHEME_B  `EVIDENCE_SHA256.txt` holds ONE line whose "filename" is the bundle
            id, not a file. The per-artefact hashes live in `MANIFEST.json`
            alongside a `bundle_sha256` aggregate. `sha256sum -c` cannot read
            it and reports "No such file or directory" — which looks exactly
            like missing evidence and is not.

Both are verified here. What is deliberately NOT claimed: `bundle_sha256`'s
derivation from the artefact hashes could not be reproduced from the artefacts
themselves, so it is checked only for internal consistency against the
`EVIDENCE_SHA256.txt` line and is otherwise reported as UNDERIVED. Guessing a
derivation until one matched would manufacture an integrity check that proves
nothing.

Fails closed: verifying zero bundles, or zero artefacts, is an error.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = ROOT / "petcare_execution" / "EVIDENCE"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_scheme_b(directory: Path) -> bool:
    manifest = directory / "MANIFEST.json"
    if not manifest.exists():
        return False
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "artefacts" in data and "bundle_sha256" in data


def verify_bundle(directory: Path) -> dict:
    """Verify one bundle. Returns a result record; never raises on mismatch."""
    listing = directory / "EVIDENCE_SHA256.txt"
    mismatches: list[tuple[str, str]] = []
    artefacts = 0

    if _is_scheme_b(directory):
        scheme = "B"
        data = json.loads((directory / "MANIFEST.json").read_text(encoding="utf-8"))
        for entry in data["artefacts"]:
            artefacts += 1
            target = directory / entry["name"]
            if not target.exists():
                mismatches.append((entry["name"], "MISSING"))
                continue
            actual = _sha256(target)
            if actual != entry["sha256"]:
                mismatches.append((entry["name"], f"{entry['sha256'][:12]}!={actual[:12]}"))
            elif target.stat().st_size != entry["bytes"]:
                mismatches.append((entry["name"], "BYTE_COUNT"))
        # The single line must restate the bundle aggregate.
        first = listing.read_text(encoding="utf-8").split()
        if not first or first[0] != data["bundle_sha256"]:
            mismatches.append(("EVIDENCE_SHA256.txt", "BUNDLE_LINE_MISMATCH"))
        aggregate = "UNDERIVED"
    else:
        scheme = "A"
        for line in listing.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            artefacts += 1
            sha, _, name = line.partition("  ")
            target = directory / name.strip()
            if not target.exists():
                mismatches.append((name.strip(), "MISSING"))
                continue
            actual = _sha256(target)
            if actual != sha.strip():
                mismatches.append((name.strip(), f"{sha[:12]}!={actual[:12]}"))
        aggregate = "PER_FILE"

    return {
        "bundle": str(directory.relative_to(ROOT)),
        "scheme": scheme,
        "artefacts": artefacts,
        "aggregate": aggregate,
        "mismatches": mismatches,
    }


def verify_all() -> list[dict]:
    results = [verify_bundle(m.parent) for m in sorted(EVIDENCE_ROOT.rglob("EVIDENCE_SHA256.txt"))]
    if not results:
        raise RuntimeError(
            "no evidence bundles found; refusing to report success over an "
            "empty set"
        )
    if sum(r["artefacts"] for r in results) == 0:
        raise RuntimeError(
            "bundles found but zero artefacts hashed; the check would be vacuous"
        )
    return results


def main() -> int:
    results = verify_all()
    failed = [r for r in results if r["mismatches"]]
    for r in results:
        status = "FAIL" if r["mismatches"] else "OK"
        print(f"[{status}] scheme {r['scheme']}  {r['artefacts']:>3} artefacts  {r['bundle']}")
        for name, why in r["mismatches"]:
            print(f"         {name}: {why}")
    print(
        f"\nBUNDLES={len(results)} "
        f"ARTEFACTS={sum(r['artefacts'] for r in results)} "
        f"FAILED={len(failed)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
