"""MVC-EPC-D-001 D2e — J-O5 consultation booking and X-26 (Sponsor ruling R11): no client-supplied identity on
appointment routes. The owner, tenant and actor come from the session; the pet and veterinarian are selectors validated
against the session tenant; one live booking per veterinarian per slot."""
import os
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bookings as bk  # noqa: E402
import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@d2e-book.test", "pw", role, full_name=f"Name {user_id}", tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@d2e-book.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _world():
    tag = uuid.uuid4().hex[:6]
    t, other = f"t-d2e-book-{tag}", f"t-d2e-book-other-{tag}"
    ids = {k: f"u-d2e-{k}-{tag}" for k in ("owner", "owner2", "vet", "foreign_vet", "foreign_owner", "admin")}
    w = {"ids": ids, "t": t,
         "owner": _client(ids["owner"], t, "owner"), "owner2": _client(ids["owner2"], t, "owner"),
         "vet": _client(ids["vet"], t, "veterinarian"), "admin": _client(ids["admin"], t, "platform_admin"),
         "foreign_vet": _client(ids["foreign_vet"], other, "veterinarian"),
         "foreign_owner": _client(ids["foreign_owner"], other, "owner")}
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    w["pet2"] = w["owner2"].post("/api/pets", json={"name": "Max", "species": "dog"}).json()["pet_id"]
    return w


def _free_slots(c, vet, n=2):
    day = datetime.now(bk.CLINIC_ZONE).date()
    out = []
    for i in range(1, bk.HORIZON_DAYS):
        r = c.get("/api/booking/slots", params={"veterinarian_id": vet, "day": (day + timedelta(days=i)).isoformat()})
        assert r.status_code == 200, r.text
        out += r.json()
        if len(out) >= n:
            return out[:n]
    raise AssertionError("no free slots")


def _book(w, owner="owner", pet="pet", **over):
    s = _free_slots(w[owner], w["ids"]["vet"], 1)[0]
    body = {"pet_id": w[pet], "veterinarian_id": w["ids"]["vet"], "starts_at": s, **over}
    return w[owner].post("/api/bookings", json=body)


def _events(c, name, rid):
    return [e for e in c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
            if e["event_name"] == name and e["resource_id"] == rid]


def test_an_owner_books_views_reschedules_and_cancels_their_own_consultation():
    w = _world()
    vets = w["owner"].get("/api/booking/veterinarians").json()
    assert [v["user_id"] for v in vets] == [w["ids"]["vet"]]          # only the caller's clinic, only veterinarians
    first, second = _free_slots(w["owner"], w["ids"]["vet"], 2)
    r = w["owner"].post("/api/bookings", json={"pet_id": w["pet"], "veterinarian_id": w["ids"]["vet"],
                                               "starts_at": first, "reason": "  annual   check  "})
    assert r.status_code == 201, r.text
    b = r.json()
    assert (b["owner_id"], b["tenant_id"], b["status"], b["mode"], b["reason"]) == (
        w["ids"]["owner"], w["t"], "BOOKED", "IN_CLINIC", "annual check")
    assert first not in _free_slots(w["owner"], w["ids"]["vet"], 50)  # the slot is no longer offered
    assert [x["booking_id"] for x in w["owner"].get("/api/bookings").json()] == [b["booking_id"]]
    moved = w["owner"].post(f"/api/bookings/{b['booking_id']}/reschedule", json={"starts_at": second})
    assert moved.status_code == 200, moved.text
    assert moved.json()["starts_at"] == datetime.fromisoformat(second).astimezone(timezone.utc).isoformat()
    gone = w["owner"].post(f"/api/bookings/{b['booking_id']}/cancel")
    assert gone.status_code == 200 and gone.json()["status"] == "CANCELLED"
    assert w["owner"].post(f"/api/bookings/{b['booking_id']}/cancel").status_code == 409
    for ev in ("consultation.booking.created", "consultation.booking.rescheduled", "consultation.booking.cancelled"):
        assert [e["actor_id"] for e in _events(w["owner"], ev, b["booking_id"])] == [w["ids"]["owner"]], ev


def test_the_owner_and_tenant_come_from_the_session_never_the_body():
    w = _world()
    r = _book(w, owner_id=w["ids"]["owner2"], tenant_id="t-someone-else", created_by_actor_id="u-spoof")
    assert r.status_code == 201, r.text
    assert (r.json()["owner_id"], r.json()["tenant_id"]) == (w["ids"]["owner"], w["t"])


def test_an_owner_cannot_book_for_a_pet_that_is_not_theirs():
    w = _world()
    r = _book(w, pet="pet2")                                          # another owner's pet in the same tenant
    assert r.status_code == 404, r.text
    foreign_pet = w["foreign_owner"].post("/api/pets", json={"name": "Z", "species": "cat"}).json()["pet_id"]
    r = w["owner"].post("/api/bookings", json={"pet_id": foreign_pet, "veterinarian_id": w["ids"]["vet"],
                                               "starts_at": _free_slots(w["owner"], w["ids"]["vet"], 1)[0]})
    assert r.status_code == 404, r.text


def test_the_veterinarian_must_be_a_veterinarian_of_the_session_tenant():
    w = _world()
    s = _free_slots(w["owner"], w["ids"]["vet"], 1)[0]
    for bad in (w["ids"]["foreign_vet"], w["ids"]["owner2"], "u-does-not-exist"):
        r = w["owner"].post("/api/bookings", json={"pet_id": w["pet"], "veterinarian_id": bad, "starts_at": s})
        assert r.status_code == 400 and r.json()["detail"]["error"] == "VETERINARIAN_NOT_IN_TENANT", (bad, r.text)
        q = w["owner"].get("/api/booking/slots", params={"veterinarian_id": bad, "day": date.today().isoformat()})
        assert q.status_code == 400, bad


def test_a_slot_is_held_by_one_live_booking_and_freed_by_cancellation():
    w = _world()
    s = _free_slots(w["owner"], w["ids"]["vet"], 1)[0]
    a = w["owner"].post("/api/bookings", json={"pet_id": w["pet"], "veterinarian_id": w["ids"]["vet"], "starts_at": s})
    assert a.status_code == 201
    b = w["owner2"].post("/api/bookings", json={"pet_id": w["pet2"], "veterinarian_id": w["ids"]["vet"], "starts_at": s})
    assert b.status_code == 409 and b.json()["detail"]["error"] == "SLOT_TAKEN"
    w["owner"].post(f"/api/bookings/{a.json()['booking_id']}/cancel")
    c = w["owner2"].post("/api/bookings", json={"pet_id": w["pet2"], "veterinarian_id": w["ids"]["vet"], "starts_at": s})
    assert c.status_code == 201, c.text


def test_only_future_default_hour_slots_are_bookable():
    w = _world()
    tomorrow = datetime.now(bk.CLINIC_ZONE).date() + timedelta(days=1)
    bad = [datetime.combine(tomorrow - timedelta(days=2), bk.OPENS, tzinfo=bk.CLINIC_ZONE),   # past, on the grid
           datetime.combine(tomorrow, bk.OPENS, tzinfo=bk.CLINIC_ZONE) + timedelta(minutes=10),  # off the grid
           datetime.combine(tomorrow, bk.CLOSES, tzinfo=bk.CLINIC_ZONE),                        # after hours
           datetime.combine(tomorrow + timedelta(days=bk.HORIZON_DAYS + 1), bk.OPENS, tzinfo=bk.CLINIC_ZONE)]
    for at in bad:
        r = w["owner"].post("/api/bookings", json={"pet_id": w["pet"], "veterinarian_id": w["ids"]["vet"],
                                                   "starts_at": at.isoformat()})
        assert r.status_code == 400 and r.json()["detail"]["error"] == "SLOT_NOT_BOOKABLE", (at, r.text)
    naive = w["owner"].post("/api/bookings", json={"pet_id": w["pet"], "veterinarian_id": w["ids"]["vet"],
                                                   "starts_at": "2030-01-01T09:00:00"})
    assert naive.status_code == 400


def test_another_owner_can_neither_see_nor_change_a_booking():
    w = _world()
    b = _book(w).json()
    assert w["owner2"].get("/api/bookings").json() == []
    s = _free_slots(w["owner2"], w["ids"]["vet"], 1)[0]
    assert w["owner2"].post(f"/api/bookings/{b['booking_id']}/reschedule", json={"starts_at": s}).status_code == 404
    assert w["owner2"].post(f"/api/bookings/{b['booking_id']}/cancel").status_code == 404
    assert w["foreign_owner"].post(f"/api/bookings/{b['booking_id']}/cancel").status_code == 404
    assert w["owner"].get("/api/bookings").json()[0]["status"] == "BOOKED"


def test_booking_routes_are_for_owners_only():
    w = _world()
    for who in ("vet", "admin"):
        assert w[who].get("/api/bookings").status_code == 403, who
        assert w[who].get("/api/booking/veterinarians").status_code == 403, who


def test_video_mode_stays_behind_its_switch(monkeypatch):
    w = _world()
    monkeypatch.delenv("PETCARE_VIDEO_CAPABILITY_ENABLED", raising=False)
    r = _book(w, mode="VIDEO")
    assert r.status_code == 409 and r.json()["detail"]["error"] == "VIDEO_DISABLED"
    assert _book(w, mode="HOUSE_CALL").status_code == 400


def test_the_legacy_appointment_stub_stores_the_session_owner_not_the_body():
    """X-26 (R11): POST /api/appointments no longer stores a client-supplied owner_id."""
    w = _world()
    r = w["owner"].post("/api/appointments", json={"pet_id": w["pet"], "owner_id": w["ids"]["owner2"],
                                                   "clinic_id": "c1", "tenant_id": w["t"]})
    assert r.status_code == 200, r.text
    assert r.json()["owner_id"] == w["ids"]["owner"]
    a = w["admin"].post("/api/appointments", json={"pet_id": w["pet"], "owner_id": w["ids"]["owner2"],
                                                   "clinic_id": "c1", "tenant_id": w["t"]})
    assert a.status_code == 200 and a.json()["owner_id"] is None      # an admin session names no owner
    no_owner = w["owner"].post("/api/appointments", json={"pet_id": w["pet"], "clinic_id": "c1", "tenant_id": w["t"]})
    assert no_owner.status_code == 200 and no_owner.json()["owner_id"] == w["ids"]["owner"]
