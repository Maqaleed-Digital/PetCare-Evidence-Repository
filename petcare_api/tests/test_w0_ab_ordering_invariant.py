"""
W0-A/W0-B ordering invariant — the pair is all-or-nothing.

W0-A's own commit message states the rule and the reason:

    "This ordering is binding and must not be reversed: the fallback is removed
    BEFORE W0-B binds authorization to the session. Binding authorization to a
    session signed with a publicly-known key would replace a header bypass with
    a forgery bypass, which is strictly worse because forged sessions look
    legitimate."

The dangerous state is therefore asymmetric. W0-A without W0-B is merely
incomplete. W0-B without W0-A is *worse than neither*, because authorization now
rests entirely on a session token that anyone who can read this repository can
forge, and a forged session is indistinguishable from a real one.

These tests exist so that state cannot be reached by a later refactor, a partial
revert, or a port that carries W0-B's shape across without W0-A's protection.
They assert the parsed AST rather than raw text, because the docstrings here and
in auth.py legitimately quote the retired expression and a text scan would flag
them as violations.
"""
from __future__ import annotations

import ast
from pathlib import Path

API = Path(__file__).resolve().parent.parent

RETIRED_LITERAL = "dev-secret-change-in-prod"


def _tree(relative: str) -> ast.AST:
    return ast.parse((API / relative).read_text(encoding="utf-8"))


def _calls(tree: ast.AST) -> list[ast.Call]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call)]


def _defines(tree: ast.AST, name: str) -> bool:
    return any(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
        for n in ast.walk(tree)
    )


def _w0a_present() -> bool:
    return _defines(_tree("routers/auth.py"), "_require_secret_key")


def _w0b_present() -> bool:
    """W0-B: require_role derives the role from the request/session, not a header."""
    main = _tree("main.py")
    for node in ast.walk(main):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name == "require_role":
            return "request" in [a.arg for a in node.args.args]
    return False


# ---------------------------------------------------------------------------
# W0-A present
# ---------------------------------------------------------------------------

def test_w0a_the_signing_key_is_required_not_defaulted():
    """The key must come from the environment or the service must refuse to run."""
    assert _w0a_present(), (
        "W0-A is absent: routers/auth.py no longer requires the session signing key"
    )


def test_w0a_no_getenv_supplies_a_default_signing_key():
    """
    A two-argument os.getenv for the key is the exact defect W0-A removed: it
    silently substitutes a published literal wherever the variable is unset.
    """
    offenders = []
    for call in _calls(_tree("routers/auth.py")):
        func = call.func
        is_getenv = (
            (isinstance(func, ast.Attribute) and func.attr == "getenv")
            or (isinstance(func, ast.Name) and func.id == "getenv")
        )
        if not is_getenv or len(call.args) < 2:
            continue
        first = call.args[0]
        if isinstance(first, ast.Constant) and "SECRET" in str(first.value).upper():
            offenders.append(getattr(call, "lineno", "?"))
    assert offenders == [], (
        f"W0-A reversed: a defaulted SECRET getenv reappeared at line(s) {offenders}"
    )


def test_w0a_the_retired_literal_is_not_assigned_as_a_value():
    """The literal may be quoted in prose; it may not be assigned to anything."""
    tree = _tree("routers/auth.py")
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, ast.Constant) and value.value == RETIRED_LITERAL:
                offenders.append(getattr(node, "lineno", "?"))
    assert offenders == [], (
        f"W0-A reversed: the retired signing key is assigned at line(s) {offenders}"
    )


# ---------------------------------------------------------------------------
# The invariant itself
# ---------------------------------------------------------------------------

def test_w0b_is_present_and_derives_the_role_from_the_session():
    assert _w0b_present(), (
        "W0-B is absent: require_role no longer takes the request, so the role is "
        "not derived from the validated session"
    )


def test_w0b_never_exists_without_w0a():
    """
    The binding invariant. B without A converts a header bypass into a session
    forgery bypass, so this fails loudly rather than letting the pair separate.
    """
    if _w0b_present():
        assert _w0a_present(), (
            "SECURITY INVARIANT VIOLATED: W0-B (session-derived authorization) is "
            "present while W0-A (required signing key) is absent. Authorization "
            "now rests on a session token signed with a key published in this "
            "repository. Restore W0-A or remove W0-B; the pair is all-or-nothing."
        )


def test_the_role_is_not_taken_from_a_client_header():
    """The pre-W0-B defect: a caller naming its own role."""
    main = _tree("main.py")
    for node in ast.walk(main):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name == "require_role":
            for default in node.args.defaults:
                if isinstance(default, ast.Call) \
                        and isinstance(default.func, ast.Name) \
                        and default.func.id == "Header":
                    raise AssertionError(
                        "W0-B reversed: require_role takes its role from a client "
                        "header again"
                    )


def test_the_invariant_assertion_set_is_not_vacuous():
    """Guard against the guard: if neither side parses, nothing above asserts."""
    assert (API / "routers" / "auth.py").exists()
    assert (API / "main.py").exists()
    assert _w0a_present() and _w0b_present(), (
        "both W0-A and W0-B must be present in the integrated canonical branch"
    )
