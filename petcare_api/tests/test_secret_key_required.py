"""W0-A — the session signing key must be required, never defaulted.

ARMED negative controls. The original defect was a `getenv` call with a literal
fallback: wherever the variable was unset, every session token was signed with a
key published in the source tree.

This ordering is binding: the fallback is removed BEFORE W0-B binds
authorization to the session, because binding authorization to a session signed
with a publicly-known key replaces a header bypass with a forgery bypass.

W0-A2 — the retired key is no longer written here. Rejection is by SHA-256
fingerprint, and these tests exercise the MECHANISM against a synthetic value
whose fingerprint is patched in. Proving the *real* retired key is refused needs
the plaintext, and the plaintext must not live in a tracked file, so that proof
is out-of-band: see
`EVIDENCE/MVC-W0A2-FINGERPRINT-GUARD/*/REAL_LITERAL_OOB_PROOF.md`.
"""
import ast
import hashlib
import os
from pathlib import Path

import pytest

from routers import auth

SOURCE = Path(auth.__file__)

#: SHA-256 of the retired W0-A default — the fingerprint, never the value.
RETIRED_KEY_SHA256 = "1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca"

#: Invented for these tests. Not a real key, and never was one.
SYNTHETIC_RETIRED_VALUE = "synthetic-retired-value"
SYNTHETIC_RETIRED_FINGERPRINT = hashlib.sha256(
    SYNTHETIC_RETIRED_VALUE.encode()
).hexdigest()


def test_t_sec_01_unset_secret_refuses_to_start(monkeypatch):
    """T-SEC-01 (ARMED) — no SECRET_KEY must be a hard failure, not a default."""
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY is not set"):
        auth._require_secret_key()


def test_t_sec_01b_blank_secret_refuses_to_start(monkeypatch):
    """Whitespace is not a key."""
    monkeypatch.setenv("SECRET_KEY", "   ")
    with pytest.raises(RuntimeError, match="SECRET_KEY is not set"):
        auth._require_secret_key()


def test_t_sec_02_a_retired_key_is_rejected_by_fingerprint(monkeypatch):
    """T-SEC-02 (ARMED) — a retired key must be refused even if supplied.

    Removing the fallback is not enough if an operator can paste the same value
    back in via the environment; tokens signed with it remain forgeable.

    The mechanism is exercised with a synthetic value whose fingerprint is
    patched into the forbidden set, so this test proves the *guard* without the
    repository holding any real retired key.
    """
    monkeypatch.setattr(
        auth, "RETIRED_KEY_FINGERPRINTS", frozenset({SYNTHETIC_RETIRED_FINGERPRINT})
    )
    monkeypatch.setenv("SECRET_KEY", SYNTHETIC_RETIRED_VALUE)
    with pytest.raises(RuntimeError, match="retired signing key"):
        auth._require_secret_key()


def test_t_sec_02b_a_near_miss_is_accepted(monkeypatch):
    """The guard must reject the retired value, not values resembling it.

    A comparison that matched a prefix, a substring or a normalised form would
    also pass the test above; only a near-miss separates them.
    """
    monkeypatch.setattr(
        auth, "RETIRED_KEY_FINGERPRINTS", frozenset({SYNTHETIC_RETIRED_FINGERPRINT})
    )
    monkeypatch.setenv("SECRET_KEY", SYNTHETIC_RETIRED_VALUE + "-x")
    assert auth._require_secret_key() == SYNTHETIC_RETIRED_VALUE + "-x"


def test_t_sec_02c_surrounding_whitespace_does_not_evade_the_guard(monkeypatch):
    """The old equality check compared `key.strip()`. The fingerprint is taken
    over the same normalised form, so padding must not smuggle a retired key
    past it."""
    monkeypatch.setattr(
        auth, "RETIRED_KEY_FINGERPRINTS", frozenset({SYNTHETIC_RETIRED_FINGERPRINT})
    )
    monkeypatch.setenv("SECRET_KEY", f"  {SYNTHETIC_RETIRED_VALUE}\t")
    with pytest.raises(RuntimeError, match="retired signing key"):
        auth._require_secret_key()


def test_t_sec_02d_the_production_fingerprint_set_is_pinned():
    """The real forbidden set, asserted by fingerprint only.

    Without this, W0-A2 could be silently defeated by emptying the set — the
    synthetic tests above patch it and would still pass.
    """
    assert auth.RETIRED_KEY_FINGERPRINTS == frozenset({RETIRED_KEY_SHA256})
    assert isinstance(auth.RETIRED_KEY_FINGERPRINTS, frozenset), (
        "the forbidden set must be immutable"
    )


def test_t_sec_03_valid_secret_is_accepted(monkeypatch):
    """Positive control — a real key is returned unchanged."""
    monkeypatch.setenv("SECRET_KEY", "a-real-key-from-governed-secret-storage")
    assert auth._require_secret_key() == "a-real-key-from-governed-secret-storage"


def test_t_sec_04_no_literal_fallback_in_source():
    """The defect must not be reintroduced as a getenv default anywhere.

    Checked over the parsed AST rather than raw text: the docstrings in this
    module and in auth.py legitimately QUOTE the retired expression to explain
    the defect, and a text scan flags those as violations. Only a real call
    counts.
    """
    tree = ast.parse(SOURCE.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
        if name != "getenv" or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and first.value == "SECRET_KEY":
            assert len(node.args) == 1 and not node.keywords, (
                "os.getenv('SECRET_KEY', <default>) reintroduces the W0-A defect"
            )
