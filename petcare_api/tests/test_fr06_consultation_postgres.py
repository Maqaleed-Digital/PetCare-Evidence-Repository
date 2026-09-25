"""FR-06 AC-FR-06-04 (U11) — consultations and outcomes are durable in PostgreSQL, tenant-scoped, and
the database refuses a second outcome or a participant who is not a stored identity."""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from consultations import Consultation, ConsultationOutcome  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T_A, T_B = "t-fr06-pg", "t-fr06-pg-b"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    for t in (T_A, T_B):
        p.tenants.create(Tenant(tenant_id=t, display_name=t))
    for uid, role in (("u-o", "owner"), ("u-v", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid,
                                         tenant_id=T_A))
    yield clean_postgres, p
    p.pool.close()


def _c(owner="u-o"):
    return Consultation(session_id=str(uuid4()), tenant_id=T_A, pet_id="pet", owner_id=owner, veterinarian_id="u-v",
                        requested_by_actor_id="u-v", mode="IN_PERSON", created_at=datetime.now(timezone.utc))


def test_consultation_and_outcome_survive_a_second_instance_within_the_tenant(pg):
    url, p = pg
    c = p.consultations.create(_c())
    p.consultations.record_outcome(ConsultationOutcome(session_id=c.session_id, tenant_id=T_A, outcome="healthy",
                                                       recorded_by_actor_id="u-v", recorded_at=datetime.now(timezone.utc)))
    r = build_persistence(_ENV, connection_url=url)
    got = r.consultations.get(c.session_id, tenant_id=T_A)
    assert (got.owner_id, got.veterinarian_id, got.requested_by_actor_id) == ("u-o", "u-v", "u-v")
    assert r.consultations.outcome_of(c.session_id, tenant_id=T_A).outcome == "healthy"
    assert r.consultations.get(c.session_id, tenant_id=T_B) is None
    assert r.consultations.outcome_of(c.session_id, tenant_id=T_B) is None
    assert r.consultations.for_tenant(T_B) == []
    r.pool.close()


def test_the_database_refuses_a_second_outcome_and_an_unknown_participant(pg):
    url, p = pg
    c = p.consultations.create(_c())
    o = ConsultationOutcome(session_id=c.session_id, tenant_id=T_A, outcome="ok", recorded_by_actor_id="u-v",
                            recorded_at=datetime.now(timezone.utc))
    p.consultations.record_outcome(o)
    with pytest.raises(RepositoryDenied):
        p.consultations.record_outcome(o)
    with pytest.raises(RepositoryDenied):
        p.consultations.create(_c(owner="u-ghost"))
