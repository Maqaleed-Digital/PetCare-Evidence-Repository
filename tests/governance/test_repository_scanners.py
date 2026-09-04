"""The two repository scanners, exercised against known positives.

Both of these started life as shell one-liners and both were wrong in a way
that a clean report could not distinguish from a correct one:

  * the secret scan matched its OWN regex and failed on a repository containing
    no secrets — a false positive that trains people to ignore the check;
  * the prohibited-literal grep matched the docstring on the FIXED `auth.py`
    and reported every ref as vulnerable, `origin/main` included — a false
    positive that would have blocked the merge that closed the exposure.

A scanner that always returns "clean" and one that works produce identical
output on a clean repository, so each is driven against a synthetic file that
must be caught, and a lookalike that must not be.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))

import prohibited_literal_scan as literal  # noqa: E402
import secret_scan  # noqa: E402


# ---------------------------------------------------------------------------
# Prohibited literal — an active default, and the three lookalikes
# ---------------------------------------------------------------------------

def test_the_active_default_pattern_matches_a_real_active_default():
    source = 'import os\nSECRET_KEY = os.getenv("SECRET_KEY", "***REMOVED_RETIRED_SECRET***")\n'
    assert literal.ACTIVE_DEFAULT.search(source), "the defect itself was not matched"


def test_the_active_default_pattern_accepts_single_quotes_and_spacing():
    for source in (
        "SECRET_KEY=os.getenv('SECRET_KEY','x')\n",
        'SECRET_KEY   =   os.getenv( "SECRET_KEY" ,  "x")\n',
    ):
        assert literal.ACTIVE_DEFAULT.search(source), f"missed a variant: {source!r}"


def test_the_active_default_pattern_ignores_the_three_lookalikes():
    """Every one of these is on the FIXED file or its tests, and every one of
    them is matched by the naive substring search."""
    docstring = '    `os.getenv("SECRET_KEY", "***REMOVED_RETIRED_SECRET***")`. A literal fallback\n'
    guard = '    if key.strip() == "***REMOVED_RETIRED_SECRET***":\n'
    constant = 'RETIRED_LITERAL = "***REMOVED_RETIRED_SECRET***"\n'
    for source in (docstring, guard, constant):
        assert not literal.ACTIVE_DEFAULT.search(source), f"false positive on {source!r}"


def test_the_naive_substring_search_would_have_produced_the_false_positive():
    """Records why the anchored pattern exists, so nobody 'simplifies' it back."""
    docstring = '    `os.getenv("SECRET_KEY", "***REMOVED_RETIRED_SECRET***")`. A literal fallback\n'
    assert 'os.getenv("SECRET_KEY", "' in docstring
    assert not literal.ACTIVE_DEFAULT.search(docstring)


def test_the_literal_scan_reports_the_repository_clean_over_a_real_file_set():
    findings, scanned = literal.scan()
    assert scanned > 100, f"only {scanned} python files scanned; the scan is near-vacuous"
    assert findings == [], f"active literal defaults present: {findings}"


# ---------------------------------------------------------------------------
# Secret scan — armed, allowlist honest, and not scanning nothing
# ---------------------------------------------------------------------------

def test_every_secret_pattern_matches_its_own_synthetic_positive():
    # Every sample is ASSEMBLED rather than written literally. A test file
    # containing a real-looking key header is itself a scanner finding, and the
    # tempting fix would be to allowlist this file — which would blind the
    # scanner to the one place a secret is most likely to be pasted while
    # debugging. The scanner caught this exact case on its first run here.
    positives = {
        "private_key_block": "-----" + "BEGIN RSA PRIVATE KEY" + "-----",
        "aws_access_key_id": "AKIA" + "A" * 16,
        "aws_secret_access_key": "aws_secret_access_key = " + "b" * 40,
        "slack_token": "xoxb-" + "1" * 24,
        "github_token": "ghp_" + "c" * 36,
        "google_api_key": "AIza" + "d" * 35,
    }
    assert set(positives) == set(secret_scan.PATTERNS), (
        "a pattern was added or removed without a synthetic positive"
    )
    for name, sample in positives.items():
        assert secret_scan.PATTERNS[name].search(sample), f"{name} did not match its positive"


def test_no_secret_pattern_fires_on_ordinary_text():
    benign = "SECRET_KEY is required. See W0-A. token = build_token(user)\n"
    for name, pattern in secret_scan.PATTERNS.items():
        assert not pattern.search(benign), f"{name} fired on benign text"


def test_every_allowlisted_path_still_exists_and_carries_a_reason():
    """An allowlist that accumulates dead paths becomes a hole nobody notices."""
    for rel, reason in secret_scan.ALLOWLIST.items():
        assert (ROOT / rel).is_file(), f"allowlisted path no longer exists: {rel}"
        assert len(reason) > 20, f"allowlist entry {rel} has no real reason"


def test_every_allowlisted_path_would_otherwise_have_been_a_finding():
    """An entry that is not actually matched is dead weight, and dead weight in
    an allowlist is where a real finding eventually hides."""
    for rel in secret_scan.ALLOWLIST:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        assert any(p.search(text) for p in secret_scan.PATTERNS.values()), (
            f"{rel} is allowlisted but matches no pattern; remove it"
        )


def test_the_secret_scan_reports_clean_over_a_real_file_set():
    findings, scanned = secret_scan.scan()
    assert scanned > 500, f"only {scanned} files scanned; the scan is near-vacuous"
    assert findings == [], f"secret material found: {findings}"


def test_the_scanners_fail_closed_on_an_empty_file_set(monkeypatch):
    """Zero files scanned must be an error, not a pass. This is the same defect
    class as an empty CI check set being read as green."""
    monkeypatch.setattr(secret_scan, "tracked_files", lambda: [])
    assert secret_scan.main() == 1

    monkeypatch.setattr(literal, "python_files", lambda: [])
    assert literal.main() == 1
