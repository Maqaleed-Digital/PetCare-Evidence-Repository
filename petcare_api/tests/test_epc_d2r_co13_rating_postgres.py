"""MVC-EPC-D-001 D2r — PostgreSQL: the CO-13 rating is durable, one per consultation and tenant-scoped. A second instance reads
back the score, comment, owner, veterinarian and time; a second rating of the same consultation is RatingExists; the table's
own CHECK refuses a score outside 1..5 even past application validation."""
import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import consultations as consult  # noqa: E402
import visit_rating as vr  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d2r-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
T0 = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)


def test_the_rating_is_durable_one_per_consultation_and_bounded(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    for uid, role in (("u-own", "owner"), ("u-vet", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid,
                                         tenant_id=T))
    for sid in ("s-1", "s-2"):
        p.consultations.create(consult.Consultation(session_id=sid, tenant_id=T, pet_id="pet-1", owner_id="u-own",
                                                    veterinarian_id="u-vet", requested_by_actor_id="u-vet",
                                                    mode=consult.MODE_IN_PERSON, created_at=T0))
    mk = lambda sid, score: vr.VisitRating(session_id=sid, tenant_id=T, owner_id="u-own", veterinarian_id="u-vet", score=score,
                                           comment="Very kind", rated_at=T0)
    p.visit_ratings.create(mk("s-1", 4))
    q = build_persistence(ENV, connection_url=clean_postgres)
    got = q.visit_ratings.for_session("s-1", tenant_id=T)
    assert (got.score, got.comment, got.owner_id, got.veterinarian_id, got.rated_at) == (4, "Very kind", "u-own", "u-vet", T0)
    assert q.visit_ratings.for_session("s-1", tenant_id="t-other") is None
    with pytest.raises(vr.RatingExists):
        q.visit_ratings.create(mk("s-1", 1))
    assert q.visit_ratings.for_session("s-1", tenant_id=T).score == 4
    with q.pool.connection() as conn:                                  # the database refuses an out-of-range score itself
        with pytest.raises(Exception):
            conn.execute("INSERT INTO consultation_rating (session_id, tenant_id, owner_id, veterinarian_id, score, comment, "
                         "rated_at) VALUES ('s-2', %s, 'u-own', 'u-vet', 6, '', %s)", (T, T0.replace(tzinfo=None)))
    p.pool.close(); q.pool.close()
