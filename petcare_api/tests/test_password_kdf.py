"""W0-J — T-PW-01: password storage uses a salted, work-factored KDF.

CP-2 W0-J `CURRENT_STATE`: `_hash_password = unsalted hashlib.sha256`.

`T-PW-01` requires an unsalted/unstretched hash to be REJECTED BY CI, so this is
a static assertion about the source as well as a behavioural one. A behavioural
test alone would pass against a build that still contained the fast-hash path and
simply did not take it.
"""
import ast
import hashlib
import re
from pathlib import Path

import pytest

import routers.auth as auth

SOURCE = Path(auth.__file__)


def test_hashes_are_salted_so_equal_passwords_differ():
    """Unsalted is the defect that breaks every account at once: identical
    passwords produce identical digests, so one table breaks them all and equal
    hashes reveal equal passwords across users."""
    a = auth._hash_password("same-password")
    b = auth._hash_password("same-password")
    assert a != b, "identical passwords produced identical hashes — unsalted"
    assert auth._verify_password("same-password", a)[0] is True
    assert auth._verify_password("same-password", b)[0] is True


def test_wrong_password_is_rejected():
    h = auth._hash_password("correct-horse")
    assert auth._verify_password("wrong", h)[0] is False


def test_t_pw_01_stored_hash_is_not_a_bare_sha256(): 
    """T-PW-01 (ARMED) — a bare digest must never be what gets stored."""
    stored = auth._hash_password("pw")
    assert not re.fullmatch(r"[0-9a-f]{64}", stored), (
        "stored credential is a bare 64-hex digest — unsalted and unstretched"
    )
    assert stored.startswith("scrypt$"), stored[:16]
    assert stored != hashlib.sha256(b"pw").hexdigest()


def test_t_pw_01b_work_factors_are_memory_hard_and_recorded():
    """The parameters must travel WITH the hash, or the work factor can never be
    raised without invalidating every existing credential."""
    stored = auth._hash_password("pw")
    scheme, n, r, p, salt, dk = stored.split("$")
    assert scheme == "scrypt"
    assert int(n) >= 2 ** 14, f"scrypt n={n} is below the memory-hard floor"
    assert int(r) >= 8
    assert len(bytes.fromhex(salt)) >= 16, "salt is too short to be unique per credential"
    assert len(bytes.fromhex(dk)) >= 32


def test_t_pw_01c_source_contains_no_bare_sha256_password_hashing():
    """The static half of T-PW-01.

    `hashlib.sha256` still appears in this module for the W0-A2 key fingerprint,
    which is a correct use — fingerprinting a high-entropy secret needs a fast
    hash, not a slow one. What must not exist is a sha256 digest being RETURNED
    as a stored password. The legacy verify path is permitted and is asserted
    below to be verify-only.
    """
    src = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(src)

    hash_fn = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == "_hash_password"),
        None,
    )
    assert hash_fn is not None, "_hash_password disappeared"

    # Inspect CALLS, not text: the docstring legitimately discusses SHA-256 while
    # explaining why it is the wrong primitive here. A substring check would flag
    # the explanation and miss an aliased call.
    called = set()
    for node in ast.walk(hash_fn):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute):
                called.add(fn.attr)
            elif isinstance(fn, ast.Name):
                called.add(fn.id)

    assert "sha256" not in called, (
        "_hash_password calls sha256 — T-PW-01 forbids storing an unsalted, "
        "unstretched hash"
    )
    assert "scrypt" in called, f"_hash_password does not use a KDF; calls: {sorted(called)}"


def test_legacy_hashes_verify_once_and_are_flagged_for_rehash():
    """A credential migration with no batch and no window.

    The legacy format must still verify — otherwise every existing account is
    locked out — but must be reported as needing a rehash, so it is upgraded at
    the one moment the plaintext is legitimately in hand.
    """
    legacy = hashlib.sha256(b"old-password").hexdigest()
    ok, needs_rehash = auth._verify_password("old-password", legacy)
    assert ok is True, "legacy credential stopped verifying — accounts would lock out"
    assert needs_rehash is True, "legacy credential was not flagged for upgrade"

    fresh = auth._hash_password("old-password")
    ok, needs_rehash = auth._verify_password("old-password", fresh)
    assert ok is True
    assert needs_rehash is False, "a current-format hash asked to be rehashed"


def test_a_stale_work_factor_is_flagged_for_rehash():
    """Raising the work factor must not invalidate credentials — it must upgrade
    them. Verified by presenting a hash built at a lower cost."""
    weak = hashlib.scrypt(b"pw", salt=b"0123456789abcdef", n=2**10, r=8, p=1, dklen=32)
    stored = f"scrypt$1024$8$1${'0123456789abcdef'.encode().hex()}${weak.hex()}"
    ok, needs_rehash = auth._verify_password("pw", stored)
    assert ok is True
    assert needs_rehash is True, "a below-current work factor was not flagged"
