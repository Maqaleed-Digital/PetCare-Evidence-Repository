"""MVC-EPC-D-001 D2 — PostgreSQL (0056): account tokens are sha256 only, consumed exactly once under concurrency,
refused when expired; email verification is pending until marked."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

NOW = datetime(2031, 3, 1, 9, 0, tzinfo=timezone.utc)


def test_tokens_are_hashed_single_use_and_expire(clean_postgres):
    p = build_persistence({SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES},
                          connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id="t-d2pg", display_name="t"))
    p.identities.create(UserIdentity(user_id="u-o", email="o@t", password_hash="x", role="owner", full_name="o",
                                     tenant_id="t-d2pg"))
    repo = p.account_tokens
    repo.require_verification("u-o", now=NOW)
    assert repo.verification_pending("u-o") is True
    raw = repo.issue("u-o", "EMAIL_VERIFICATION", now=NOW)
    with psycopg.connect(clean_postgres) as conn:
        stored = conn.execute("SELECT token_sha256 FROM account_token").fetchall()
    assert raw not in str(stored) and len(stored) == 1
    with ThreadPoolExecutor(max_workers=8) as ex:
        winners = list(ex.map(lambda _: repo.consume(raw, "EMAIL_VERIFICATION", now=NOW), range(8)))
    assert winners.count("u-o") == 1 and winners.count(None) == 7
    repo.mark_verified("u-o", now=NOW)
    assert repo.verification_pending("u-o") is False
    reset = repo.issue("u-o", "PASSWORD_RESET", now=NOW)
    assert repo.consume(reset, "PASSWORD_RESET", now=NOW + timedelta(minutes=31)) is None
    assert repo.verification_pending("u-unknown") is False
    p.pool.close()
