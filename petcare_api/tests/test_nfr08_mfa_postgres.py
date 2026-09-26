"""NFR-08 (v1.2 U25) — PostgreSQL holds only ciphertext for the TOTP secret, and a code is single-use atomically."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import mfa  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def test_ciphertext_only_and_single_use_under_concurrency(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id="t-mfa", display_name="t"))
    p.identities.create(UserIdentity(user_id="u-mfa", email="m@t", password_hash="x", role="owner", full_name="m",
                                     tenant_id="t-mfa"))
    secret = os.urandom(20)
    nonce, ct = mfa.encrypt("k-test-material", secret)
    p.mfa.put_factor(mfa.Factor(user_id="u-mfa", nonce=nonce, ciphertext=ct, created_at=datetime.now(timezone.utc)))
    with psycopg.connect(clean_postgres) as conn:
        raw = bytes(conn.execute("SELECT ciphertext FROM mfa_factor WHERE user_id = 'u-mfa'").fetchone()[0])
    assert secret not in raw and mfa.decrypt("k-test-material", nonce, raw) == secret
    with ThreadPoolExecutor(max_workers=8) as ex:
        wins = list(ex.map(lambda _: p.mfa.use_step("u-mfa", 12345), range(8)))
    assert sum(wins) == 1                                                                 # exactly one use of a step
    assert p.mfa.use_step("u-mfa", 12344) is False and p.mfa.use_step("u-mfa", 12346) is True
    p.pool.close()
