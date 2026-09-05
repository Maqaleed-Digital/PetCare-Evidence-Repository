"""W0-A2 — the retired signing key must not exist in any tracked file.

WHY THIS IS A SEPARATE GUARD
----------------------------
A Gate-5 offline rehearsal rewrote the retired key out of history and produced a
tree whose `_require_secret_key` compared against the tombstone instead of the
key. That tree ACCEPTED the real retired key — and the entire test suite passed,
because the content-based rewrite had edited the assertions in step with the
implementation.

The root cause was not the rewrite. It was that the plaintext lived at HEAD at
all: as a guard comparand, as test constants, as scanner fixtures, as prose. A
content-based rewrite cannot distinguish the secret as a leaked value from the
secret as the value something refuses.

So the standing rule is: the retired key exists in this repository's HEAD in
exactly zero places, and everything needing to refer to it refers to its
SHA-256.

HOW THIS FILE AVOIDS BECOMING THE THING IT FORBIDS
--------------------------------------------------
It never contains, reconstructs or prints the plaintext. It knows only the
digest and searches by hashing candidate byte windows. That is slower than a
substring search, and it is the only way a scanner for a secret can be written
without carrying the secret.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: SHA-256 of the retired W0-A signing key. Never the value itself.
RETIRED_KEY_SHA256 = "1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca"

#: Length of the retired key in bytes — needed to size the search window. It
#: reveals nothing beyond what the digest already pins.
RETIRED_KEY_LENGTH = 25

#: Bounds the cost of the window scan. Binaries are excluded separately.
_MAX_SCAN_BYTES = 4_000_000


def _tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [p for p in out.split("\0") if p]


def _contains_retired_key(data: bytes) -> bool:
    """True when any `RETIRED_KEY_LENGTH`-byte window hashes to the fingerprint."""
    n = RETIRED_KEY_LENGTH
    for i in range(len(data) - n + 1):
        if hashlib.sha256(data[i:i + n]).hexdigest() == RETIRED_KEY_SHA256:
            return True
    return False


def _scan() -> tuple[list[str], int, int]:
    hits: list[str] = []
    scanned = skipped = 0
    for rel in _tracked_files():
        path = ROOT / rel
        try:
            if path.stat().st_size > _MAX_SCAN_BYTES:
                skipped += 1
                continue
            data = path.read_bytes()
        except OSError:
            skipped += 1
            continue
        if b"\0" in data[:4096]:      # binary
            skipped += 1
            continue
        scanned += 1
        if _contains_retired_key(data):
            hits.append(rel)
    return hits, scanned, skipped


def test_no_tracked_file_contains_the_retired_signing_key():
    """The load-bearing assertion of W0-A2."""
    hits, scanned, _ = _scan()
    assert scanned > 500, f"only {scanned} tracked files scanned; the guard is near-vacuous"
    assert hits == [], (
        f"the retired signing key is present in {len(hits)} tracked file(s): {hits}. "
        "Replace each occurrence with its SHA-256 fingerprint."
    )


def test_the_window_scanner_finds_a_known_plant():
    """Positive control.

    A scanner that never matches produces the same clean report as one that
    works. This plants a synthetic value, pins its own digest, and proves the
    window search finds it — the real key is not involved at all.
    """
    plant = b"synthetic-retired-value--"      # 25 bytes, same window size
    assert len(plant) == RETIRED_KEY_LENGTH
    digest = hashlib.sha256(plant).hexdigest()

    def contains(data: bytes) -> bool:
        n = RETIRED_KEY_LENGTH
        return any(
            hashlib.sha256(data[i:i + n]).hexdigest() == digest
            for i in range(len(data) - n + 1)
        )

    assert contains(b"prefix " + plant + b" suffix"), "the window scanner missed a plant"
    assert not contains(b"prefix " + plant[:-1] + b"X suffix"), "the scanner over-matched"
    assert not contains(b"nothing to find here at all")


def test_the_guard_knows_the_digest_and_not_the_value():
    """This file must never acquire the plaintext.

    If someone pastes the retired key in to make the scan simpler, the main
    assertion would fail — but only after the value was committed. This checks
    the guard's own bytes directly.
    """
    own = Path(__file__).read_bytes()
    assert not _contains_retired_key(own), (
        "this guard now contains the retired key it exists to forbid"
    )


def test_the_fingerprint_matches_the_production_guard():
    """The digest here and the one the running code refuses must be the same.

    Two independently-maintained copies of a fingerprint drift; when they do,
    this guard polices a key the application no longer rejects.
    """
    import sys

    sys.path.insert(0, str(ROOT / "petcare_api"))
    os.environ.setdefault("SECRET_KEY", "test-only-not-a-deployed-secret")
    from routers import auth  # noqa: E402

    assert RETIRED_KEY_SHA256 in auth.RETIRED_KEY_FINGERPRINTS, (
        "the absence guard and the runtime guard disagree about which key is retired"
    )


def test_the_boundary_this_change_does_not_cross():
    """W0-A2 clears tracked HEAD. History is Gate-5.

    Recorded so the two are never conflated: `CURRENT_HEAD_TRACKED_PLAINTEXT=0`
    is what this PR achieves, and it is not `ALL_GIT_HISTORY_PLAINTEXT=0`.
    """
    proc = subprocess.run(
        ["git", "cat-file", "-e", "5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96^{commit}"],
        cwd=ROOT, capture_output=True,
    )
    introducing_present = proc.returncode == 0
    # Both states are legitimate: before the purge it is present, after it is
    # gone. The assertion is that HEAD is clean either way, which the first test
    # already proves — this one exists to document the boundary in the suite.
    assert introducing_present in (True, False)
