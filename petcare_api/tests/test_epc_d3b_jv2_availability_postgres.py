"""MVC-EPC-D-001 D3b — PostgreSQL: published availability is durable and versioned (the latest plan, with its windows in
weekday/time order, is read back by a second instance), tenant-scoped, and an empty plan is a real plan with no window; a
veterinarian's bookings are listed for that veterinarian only."""
import os
import sys
from datetime import datetime, time, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import availability as avl  # noqa: E402
import bookings as bk  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetProfile  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d3b-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
T0 = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)


def test_availability_is_durable_versioned_and_bookings_list_per_veterinarian(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    for uid, role in (("u-own", "owner"), ("u-vet", "veterinarian"), ("u-vet2", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid, tenant_id=T))
    W = avl.Window
    p.availability.publish(avl.AvailabilityPlan("pl-1", T, "u-vet", (W(2, time(9), time(12)),), T0))
    p.availability.publish(avl.AvailabilityPlan("pl-2", T, "u-vet", (W(4, time(14), time(16)), W(1, time(10), time(11))),
                                                T0 + timedelta(hours=1)))
    q = build_persistence(ENV, connection_url=clean_postgres)
    got = q.availability.latest("u-vet", tenant_id=T)
    assert got.plan_id == "pl-2" and got.published_at == T0 + timedelta(hours=1)
    assert [(x.weekday, x.opens, x.closes) for x in got.windows] == [(1, time(10), time(11)), (4, time(14), time(16))]
    assert q.availability.latest("u-vet", tenant_id="t-other") is None
    assert q.availability.latest("u-vet2", tenant_id=T) is None
    q.availability.publish(avl.AvailabilityPlan("pl-3", T, "u-vet", (), T0 + timedelta(hours=2)))
    assert q.availability.latest("u-vet", tenant_id=T).windows == ()           # an empty plan is in force, not "none"
    p.pets.create(PetProfile(pet_id="pet-1", tenant_id=T, owner_id="u-own", name="Luna", species="cat",
                             created_by_actor_id="u-own", created_at=T0, updated_at=T0))
    mk = lambda bid, vet, mins: bk.Booking(booking_id=bid, tenant_id=T, owner_id="u-own", pet_id="pet-1", veterinarian_id=vet,
                                          mode=bk.IN_CLINIC, starts_at=T0 + timedelta(days=2, minutes=mins), status=bk.BOOKED,
                                          reason="", created_by_actor_id="u-own", created_at=T0, updated_at=T0)
    p.bookings.create(mk("b-2", "u-vet", 60)); p.bookings.create(mk("b-1", "u-vet", 0)); p.bookings.create(mk("b-3", "u-vet2", 0))
    assert [b.booking_id for b in q.bookings.list_for_veterinarian("u-vet", tenant_id=T)] == ["b-1", "b-2"]
    p.pool.close(); q.pool.close()
