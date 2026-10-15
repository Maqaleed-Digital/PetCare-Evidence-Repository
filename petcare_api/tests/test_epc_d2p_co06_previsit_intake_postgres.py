"""MVC-EPC-D-001 D2p — PostgreSQL: the CO-06 pre-visit intake and its photo rows are durable, one per booking, and written
atomically. A second instance reads back the intake with both photos in order; a second intake for the same booking is
IntakeExists; an intake whose photo row fails (duplicate storage key) leaves NO intake row behind."""
import os
import sys
from datetime import date, datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import bookings as bk  # noqa: E402
import previsit_intake as pvi  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetProfile  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d2p-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
T0 = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)


def _photo(intake_id, n, key=None, *, pid=None):
    """Photos of one intake share ONE upload instant (as the served route writes them), so only `position` orders them."""
    return pvi.IntakePhoto(photo_id=pid or f"{intake_id}-p{n}", intake_id=intake_id, tenant_id=T, position=n - 1,
                           filename=f"{n}.png", content_type="image/png", byte_size=10 + n, content_sha256="ab" * 32,
                           storage_key=key or f"{T}/intake-{intake_id}-{n}", uploaded_at=T0)


def _intake(intake_id, booking_id, photos):
    return pvi.PreVisitIntake(intake_id=intake_id, tenant_id=T, booking_id=booking_id, owner_id="u-own", pet_id="pet-1",
                              reason="Limping", symptoms_since=date(2031, 2, 26), eating_normally="NO",
                              current_medications="Meloxicam", submitted_at=T0, photos=tuple(photos))


def _booking(p, booking_id, minutes):
    p.bookings.create(bk.Booking(booking_id=booking_id, tenant_id=T, owner_id="u-own", pet_id="pet-1", veterinarian_id="u-vet",
                                 mode=bk.IN_CLINIC, starts_at=T0 + timedelta(days=2, minutes=minutes), status=bk.BOOKED,
                                 reason="check-up", created_by_actor_id="u-own", created_at=T0, updated_at=T0))


def test_the_intake_is_durable_one_per_booking_and_atomic(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    for uid, role in (("u-own", "owner"), ("u-vet", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid,
                                         tenant_id=T))
    p.pets.create(PetProfile(pet_id="pet-1", tenant_id=T, owner_id="u-own", name="Luna", species="cat",
                             created_by_actor_id="u-own", created_at=T0, updated_at=T0))
    _booking(p, "b-1", 0)
    _booking(p, "b-2", 30)
    # ids that sort AGAINST the attachment order: z-first is attached first
    p.previsit_intakes.create(_intake("i-1", "b-1", [_photo("i-1", 1, pid="z-first"), _photo("i-1", 2, pid="a-second")]))

    q = build_persistence(ENV, connection_url=clean_postgres)
    got = q.previsit_intakes.for_booking("b-1", tenant_id=T)
    assert (got.intake_id, got.reason, got.symptoms_since, got.eating_normally, got.submitted_at) == (
        "i-1", "Limping", date(2031, 2, 26), "NO", T0)
    assert [(x.photo_id, x.position, x.byte_size, x.uploaded_at) for x in got.photos] == [
        ("z-first", 0, 11, T0), ("a-second", 1, 12, T0)]
    assert q.previsit_intakes.for_booking("b-1", tenant_id="t-other") is None
    with pytest.raises(pvi.IntakeExists):
        q.previsit_intakes.create(_intake("i-1b", "b-1", []))
    # atomic: the second photo row collides on storage_key -> nothing of intake i-2 remains
    with pytest.raises(RepositoryDenied):
        q.previsit_intakes.create(_intake("i-2", "b-2", [_photo("i-2", 1, key="dup"), _photo("i-2", 2, key="dup")]))
    assert q.previsit_intakes.for_booking("b-2", tenant_id=T) is None
    p.pool.close(); q.pool.close()
