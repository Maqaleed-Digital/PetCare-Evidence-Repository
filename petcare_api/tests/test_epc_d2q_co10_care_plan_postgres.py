"""MVC-EPC-D-001 D2q — PostgreSQL: the CO-10 care plan is durable and one per consultation. A second instance reads back the
instructions, the follow-up DATE and the recording time; a second plan for the same consultation is CarePlanExists; the plan is
tenant-scoped."""
import os
import sys
from datetime import date, datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import care_plan as cpl  # noqa: E402
import consultations as consult  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d2q-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
T0 = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)


def test_the_care_plan_is_durable_and_one_per_consultation(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    for uid, role in (("u-own", "owner"), ("u-vet", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid,
                                         tenant_id=T))
    p.consultations.create(consult.Consultation(session_id="s-1", tenant_id=T, pet_id="pet-1", owner_id="u-own",
                                                veterinarian_id="u-vet", requested_by_actor_id="u-vet",
                                                mode=consult.MODE_IN_PERSON, created_at=T0))
    p.care_plans.create(cpl.CarePlan(session_id="s-1", tenant_id=T, instructions="Rest 7 days", follow_up_on=date(2031, 3, 15),
                                     recorded_by_actor_id="u-vet", recorded_at=T0))
    q = build_persistence(ENV, connection_url=clean_postgres)
    got = q.care_plans.for_session("s-1", tenant_id=T)
    assert (got.instructions, got.follow_up_on, got.recorded_by_actor_id, got.recorded_at) == (
        "Rest 7 days", date(2031, 3, 15), "u-vet", T0)
    assert q.care_plans.for_session("s-1", tenant_id="t-other") is None
    with pytest.raises(cpl.CarePlanExists):
        q.care_plans.create(cpl.CarePlan(session_id="s-1", tenant_id=T, instructions="again", follow_up_on=None,
                                         recorded_by_actor_id="u-vet", recorded_at=T0))
    assert q.care_plans.for_session("s-1", tenant_id=T).instructions == "Rest 7 days"
    p.pool.close(); q.pool.close()
