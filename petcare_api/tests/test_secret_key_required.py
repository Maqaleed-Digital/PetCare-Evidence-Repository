"""W0-A — the session signing key must be required, never defaulted.

ARMED negative controls. The original defect was
`SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")`: wherever
the variable was unset, every session token was signed with a key published in
the source tree.

This ordering is binding: the fallback is removed BEFORE W0-B binds
authorization to the session, because binding authorization to a session signed
with a publicly-known key replaces a header bypass with a forgery bypass.
"""
import ast
import os
from pathlib import Path

import pytest

from routers import auth

SOURCE = Path(auth.__file__)
RETIRED_LITERAL = "dev-secret-change-in-prod"


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


def test_t_sec_02_retired_literal_is_rejected(monkeypatch):
    """T-SEC-02 (ARMED) — the retired default must be refused even if supplied.

    Removing the fallback is not enough if an operator can paste the same value
    back in via the environment; tokens signed with it remain forgeable.
    """
    monkeypatch.setenv("SECRET_KEY", RETIRED_LITERAL)
    with pytest.raises(RuntimeError, match="retired literal default"):
        auth._require_secret_key()


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
