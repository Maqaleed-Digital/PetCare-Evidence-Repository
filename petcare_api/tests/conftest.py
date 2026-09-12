"""Test bootstrap.

W0-A removed the literal `SECRET_KEY` fallback, so `routers.auth` now refuses to
import without one. That is the intended fail-closed behaviour in every
environment — including CI, which must supply a real key from governed secret
storage rather than relying on a default.

A deterministic non-secret value is set here ONLY if the environment has not
already provided one, so the suite documents the requirement instead of failing
at collection with an unexplained import error. This value is never used by any
deployed process: `_require_secret_key()` is exercised directly, with
monkeypatched environments, in test_secret_key_required.py.
"""
import os
import sys

import pytest

# SECRET_KEY, PETCARE_SECRET_MODE and PETCARE_PERSISTENCE_MODE are set by the
# REPOSITORY-ROOT conftest.py, not here. They were here, and that placement was
# a defect: `tests/governance/test_retired_key_absence.py` imports
# `routers.auth`, so `pytest tests` failed while the combined command CI runs
# passed — the API conftest was loaded in one and not the other. One bootstrap,
# at the root, is what makes every invocation behave the same way.

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pg_harness import (  # noqa: E402
    create_database,
    drop_database,
    replay_migrations,
    reset_w0f_tables,
    start_ephemeral_cluster,
)


# ---------------------------------------------------------------------------
# Ephemeral PostgreSQL
# ---------------------------------------------------------------------------
#
# The adapter is proven against real PostgreSQL, not against SQLite standing in
# for it. The substitution would be invisible and wrong in exactly the places
# that matter: `IS NOT DISTINCT FROM`, `ON CONFLICT`, the rowcount of a
# conditional UPDATE, and the CHECK constraints migration 0031 relies on all
# behave differently or do not exist.
#
# UNAVAILABILITY IS A FAILURE, NOT A SKIP. A suite that silently skips its only
# integration coverage reports green having evaluated nothing, and that green is
# indistinguishable from having run. `PETCARE_POSTGRES_TESTS=skip` opts out
# deliberately; nothing opts out on your behalf.

@pytest.fixture(scope="session")
def postgres_admin_url() -> str:
    """A connection URL with rights to create databases."""
    if os.environ.get("PETCARE_POSTGRES_TESTS") == "skip":
        pytest.skip("PETCARE_POSTGRES_TESTS=skip — integration coverage opted out")
    url = (os.environ.get("PETCARE_TEST_PG_URL") or "").strip()
    if url:
        return url
    try:
        return start_ephemeral_cluster()
    except Exception as exc:  # noqa: BLE001 — reported, never swallowed
        raise RuntimeError(
            "PostgreSQL is required by the W0-F integration suite and no server "
            f"could be reached or started ({type(exc).__name__}: {exc}). Set "
            "PETCARE_TEST_PG_URL to an ephemeral server, or install PostgreSQL. "
            "This is a failure and not a skip on purpose: a skipped integration "
            "suite reports green having proved nothing."
        ) from None


@pytest.fixture(scope="session")
def migrated_postgres_url(postgres_admin_url: str):
    """One database with the whole chain replayed, shared by the suite."""
    name = "petcare_w0f_suite"
    url = create_database(postgres_admin_url, name)
    replay_migrations(url)
    yield url
    drop_database(postgres_admin_url, name)


@pytest.fixture()
def clean_postgres(migrated_postgres_url: str) -> str:
    """The migrated database with the W0-F tables emptied."""
    reset_w0f_tables(migrated_postgres_url)
    return migrated_postgres_url
