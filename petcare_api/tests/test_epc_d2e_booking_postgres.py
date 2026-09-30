"""MVC-EPC-D-001 D2e — PostgreSQL (0058): consultation bookings persist, are tenant-scoped, and the DATABASE itself refuses
a second live booking of one veterinarian at one instant (partial unique index), while a cancelled booking frees it."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import bookings as bk  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetProfile as Pet  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

NOW = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)
T = "t-d2e-pg"


def _persistence(url):
    p = build_persistence({SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES},
                          connection_url=url)
    p.tenants.create(Tenant(tenant_id=T, display_name="t"))
    for uid, role in (("u-o", "owner"), ("u-o2", "owner"), ("u-v", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid,
                                         tenant_id=T))
    for pid, owner in (("pet-1", "u-o"), ("pet-2", "u-o2")):
        p.pets.create(Pet(pet_id=pid, tenant_id=T, owner_id=owner, name=pid, species="cat", breed=None,
                          birth_date=None, weight_kg=None, medical_conditions=None, allergies=None, preferences=None,
                          created_by_actor_id=owner, created_at=NOW, updated_at=NOW))
    return p


def _b(i, owner, pet, at):
    return bk.Booking(f"bk-{i}", T, owner, pet, "u-v", bk.IN_CLINIC, at, bk.BOOKED, "", owner, NOW, NOW)


def test_one_live_booking_per_veterinarian_slot_is_enforced_by_the_database(clean_postgres):
    p = _persistence(clean_postgres)
    repo = p.bookings
    slot, later = NOW + timedelta(days=1), NOW + timedelta(days=1, minutes=30)
    repo.create(_b(1, "u-o", "pet-1", slot))
    with pytest.raises(bk.SlotTaken):
        repo.create(_b(2, "u-o2", "pet-2", slot))
    with psycopg.connect(clean_postgres) as conn:                    # the index, not the repository, refuses
        with pytest.raises(psycopg.errors.UniqueViolation):
            conn.execute("INSERT INTO consultation_booking VALUES ('bk-raw','t-d2e-pg','u-o2','pet-2','u-v','IN_CLINIC',"
                         "%s,'BOOKED','','u-o2',now(),now())", (slot.replace(tzinfo=None),))
    repo.create(_b(3, "u-o2", "pet-2", later))
    with pytest.raises(bk.SlotTaken):
        repo.reschedule("bk-3", slot, tenant_id=T, at=NOW)
    repo.cancel("bk-1", tenant_id=T, at=NOW)
    assert repo.reschedule("bk-3", slot, tenant_id=T, at=NOW).starts_at == slot
    assert repo.taken_starts("u-v", tenant_id=T) == {slot}
    assert [b.booking_id for b in repo.list_for_owner("u-o", tenant_id=T)] == ["bk-1"]
    assert repo.get("bk-1", tenant_id=T).status == bk.CANCELLED
    assert repo.get("bk-1", tenant_id="t-other") is None
    assert repo.list_for_owner("u-o", tenant_id="t-other") == []
    with pytest.raises(bk.RepositoryDenied):
        repo.cancel("bk-1", tenant_id=T, at=NOW)                        # a cancelled booking is not live
    p.pool.close()
