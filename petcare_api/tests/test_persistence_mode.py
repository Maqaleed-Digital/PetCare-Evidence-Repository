"""PERSIST-01 — a process configured for `postgres` never serves from memory.

The failure being prevented is specific, and it is the reason this control
exists rather than a general preference for strictness.

A fallback from `postgres` to `memory` looks like resilience and behaves like
data loss with a clean health check. The service answers, sign-in works, sessions
are issued — and every one of them is invisible to every other instance and gone
at the next restart. For W0-F in particular it is worse than data loss: session
revocation silently stops working across instances, because a session revoked in
one process's memory is still live in another's. AC-7's entire claim is that
sessions are revocable. A silent memory fallback would make that claim false
while every existing test still passed, because every existing test runs in a
single process.

So the assertions below are not only "it raises". They are "it raises AND it did
not hand back a memory store", which is the thing that would actually be wrong.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from persistence import (  # noqa: E402
    MODE_MEMORY,
    MODE_POSTGRES,
    PERSISTENCE_MODE_ENV_VAR,
    Persistence,
    build_persistence,
    current_persistence_mode,
)
from postgres_repositories import PersistenceUnavailable  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

ENV_MODE = {SECRET_MODE_ENV_VAR: "environment"}

#: Nothing listens here, and a refused connection is immediate — so the control
#: proves the refusal rather than a timeout.
UNREACHABLE = "postgresql://nobody@127.0.0.1:1/nowhere"


# ---------------------------------------------------------------------------
# Positive control
# ---------------------------------------------------------------------------

def test_positive_control_memory_mode_builds():
    """Without this, a `build_persistence` that raised unconditionally would
    satisfy every refusal in this file."""
    p = build_persistence(dict(ENV_MODE, **{PERSISTENCE_MODE_ENV_VAR: MODE_MEMORY}))
    assert isinstance(p, Persistence)
    assert p.mode == MODE_MEMORY
    assert p.is_durable is False
    assert p.session_store is not None
    assert p.identities is not None
    assert p.invites is not None


# ---------------------------------------------------------------------------
# PERSIST-01
# ---------------------------------------------------------------------------

def test_persist_01_postgres_with_an_unreachable_store_fails_closed():
    env = dict(ENV_MODE, **{PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES})
    with pytest.raises(PersistenceUnavailable):
        build_persistence(env, connection_url=UNREACHABLE)


def test_persist_01b_it_does_not_quietly_return_a_memory_store():
    """The assertion that matters. `raises` alone would still pass if the
    function returned a memory Persistence on some other path."""
    env = dict(ENV_MODE, **{PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES})
    result = None
    try:
        result = build_persistence(env, connection_url=UNREACHABLE)
    except PersistenceUnavailable:
        pass
    assert result is None, (
        f"postgres was configured and unavailable, yet a {getattr(result, 'mode', '?')} "
        "store was returned — revocation would silently stop working across instances"
    )


def test_persist_01c_a_missing_db_credential_also_fails_closed():
    """The other way the store becomes unavailable: the credential, not the
    network. Both must end in the same refusal, or one of them ends in memory."""
    env = dict(ENV_MODE, **{PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES})
    with pytest.raises(PersistenceUnavailable):
        build_persistence(env)


def test_persist_01d_no_fallback_exists_in_the_source():
    """Behavioural tests prove the absence of the fallbacks they thought to try.

    This asserts the shape: no handler in `persistence.py` returns a memory
    Persistence. A future `except Exception: return Persistence(mode=MODE_MEMORY, ...)`
    would pass every test above by never being reached in them, and would be the
    exact defect this file exists to prevent.
    """
    import pathlib
    import re

    source = (pathlib.Path(__file__).resolve().parents[1]
              / "persistence.py").read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    # Every construction of a memory Persistence must be lexically inside the
    # `if mode == MODE_MEMORY:` branch — i.e. exactly one of them exists.
    assert code.count("mode=MODE_MEMORY") == 1, (
        "more than one path builds a memory store; one of them is a fallback"
    )
    # And no except-handler may be followed by one.
    for handler in re.finditer(r"except[^\n]*:\n((?:[ \t]+[^\n]*\n)+)", code):
        assert "MODE_MEMORY" not in handler.group(1), (
            "an exception handler builds a memory store — that is the silent "
            "fallback PERSIST-01 forbids"
        )


# ---------------------------------------------------------------------------
# Mode selection
# ---------------------------------------------------------------------------

def test_an_unset_persistence_mode_fails_closed():
    """Unset does not become `memory`. A deployment that forgot the variable is
    exactly the deployment that believed it was durable."""
    with pytest.raises(PersistenceUnavailable, match=PERSISTENCE_MODE_ENV_VAR):
        current_persistence_mode({})


@pytest.mark.parametrize("mode", ["postgresql", "pg", "POSTGRES", "sqlite", " "])
def test_an_unknown_persistence_mode_is_refused_rather_than_coerced(mode):
    with pytest.raises(PersistenceUnavailable):
        current_persistence_mode({PERSISTENCE_MODE_ENV_VAR: mode})


def test_build_persistence_refuses_an_unknown_mode_too():
    """The selector being strict is not enough if the builder has its own
    reading of the value."""
    with pytest.raises(PersistenceUnavailable):
        build_persistence(dict(ENV_MODE, **{PERSISTENCE_MODE_ENV_VAR: "sqlite"}))
