"""NFR-15 (v1.2 U24) — the rate-limit count is shared across processes: two independent connection pools (two
"workers") increment one PostgreSQL row atomically."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import ratelimit as rl  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def test_two_workers_share_one_count_and_the_101st_is_refused(clean_postgres):
    w1, w2 = build_persistence(_ENV, connection_url=clean_postgres), build_persistence(_ENV, connection_url=clean_postgres)
    limiters = [rl.Limiter(repo=p.ratelimits, policy=rl.Policy.from_env({})) for p in (w1, w2)]
    now = 1_900_000_040.0
    with ThreadPoolExecutor(max_workers=8) as ex:
        decisions = list(ex.map(lambda i: limiters[i % 2].hit(principal="u-shared", peer=None, forwarded_for=None, now=now),
                                range(101)))
    assert sorted(d.count for d in decisions) == list(range(1, 102))     # no lost update across the two workers
    assert sum(d.allowed for d in decisions) == 100
    with psycopg.connect(clean_postgres) as conn:
        assert conn.execute("SELECT count FROM rate_limit_counter WHERE bucket = 'principal:u-shared'").fetchone()[0] == 101
    for p in (w1, w2):
        p.pool.close()
