"""FR-09 — a stored language choice outlives the process (U3). Second-instance read-back
against REAL PostgreSQL through the repository the serving path uses."""
import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T_A = "t-lang-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _p(url):
    return build_persistence(_ENV, connection_url=url)


@pytest.fixture()
def pg(clean_postgres):
    p = _p(clean_postgres)
    p.tenants.create(Tenant(tenant_id=T_A, display_name=T_A))
    p.identities.create(UserIdentity(user_id="u-lang-pg", email="u-lang-pg@lang.test",
                                     password_hash="x", role="owner", full_name="L", tenant_id=T_A))
    yield clean_postgres
    p.pool.close()


def test_language_choice_survives_a_second_instance(pg):
    w = _p(pg)
    w.preferences.set_language("u-lang-pg", tenant_id=T_A, language="en", at=datetime.now(timezone.utc))
    r = _p(pg)
    assert r.preferences.get_language("u-lang-pg") == "en"
    r.preferences.set_language("u-lang-pg", tenant_id=T_A, language="ar", at=datetime.now(timezone.utc))
    assert _p(pg).preferences.get_language("u-lang-pg") == "ar"
    for p in (w, r):
        p.pool.close()


def test_unknown_language_and_unknown_identity_are_refused(pg):
    w = _p(pg)
    with pytest.raises(RepositoryDenied):
        w.preferences.set_language("u-lang-pg", tenant_id=T_A, language="fr", at=datetime.now(timezone.utc))
    with pytest.raises(RepositoryDenied):
        w.preferences.set_language("u-nobody", tenant_id=T_A, language="en", at=datetime.now(timezone.utc))
    w.pool.close()
