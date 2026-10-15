"""MVC-EPC-D-001 D3b — J-V2 (R21.4): a veterinarian publishes a weekly schedule; owners can book only its slots; the
veterinarian's queue holds their OWN upcoming bookings and open consultations. Never published -> clinic default hours
(D2E-DEFAULT-HOURS, recorded assumption). A new plan never moves an existing booking. Plans are validated (grid, overlap)."""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
RIYADH = ZoneInfo("Asia/Riyadh")


def _client(user_id, tenant, role, name=None):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@jv2.test", "pw", role, full_name=name or user_id, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@jv2.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d3b-jv2-{tag}"
    w = {"vet_id": f"u-v2-vet-{tag}", "vet2_id": f"u-v2-vet2-{tag}", "owner_id": f"u-v2-own-{tag}"}
    w["vet"] = _client(w["vet_id"], t, "veterinarian")
    w["vet2"] = _client(w["vet2_id"], t, "veterinarian")
    w["owner"] = _client(w["owner_id"], t, "owner", name="Huda")
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    w["day"] = (datetime.now(RIYADH) + timedelta(days=3)).date()              # inside the 14-day horizon, in the future
    return w


def _slots(w, vet_id, day=None):
    r = w["owner"].get("/api/booking/slots", params={"veterinarian_id": vet_id, "day": (day or w["day"]).isoformat()})
    assert r.status_code == 200, r.text
    return [datetime.fromisoformat(s).astimezone(RIYADH).strftime("%H:%M") for s in r.json()]


def _publish(c, windows):
    return c.put("/api/vet/availability", json={"windows": windows})


def _book(w, vet_id, hhmm, day=None):
    at = datetime.combine(day or w["day"], datetime.strptime(hhmm, "%H:%M").time(), tzinfo=RIYADH)
    return w["owner"].post("/api/bookings", json={"pet_id": w["pet"], "veterinarian_id": vet_id, "starts_at": at.isoformat()})


def test_never_published_keeps_the_clinic_default_hours(w):
    slots = _slots(w, w["vet_id"])
    assert slots[0] == "09:00" and slots[-1] == "16:30" and len(slots) == 16
    body = w["vet"].get("/api/vet/availability").json()
    assert body["default_hours"] is True and body["plan_id"] is None


def test_published_windows_are_the_only_bookable_slots(w):
    wd = w["day"].weekday()
    r = _publish(w["vet"], [{"weekday": wd, "opens": "10:00", "closes": "11:30"}, {"weekday": wd, "opens": "14:00", "closes": "15:00"}])
    assert r.status_code == 200, r.text
    assert _slots(w, w["vet_id"]) == ["10:00", "10:30", "11:00", "14:00", "14:30"]
    assert _slots(w, w["vet_id"], w["day"] + timedelta(days=1)) == []           # no window that weekday
    assert _slots(w, w["vet2_id"])[0] == "09:00"                                 # another veterinarian is unaffected
    assert _book(w, w["vet_id"], "09:00").json()["detail"]["error"] == "SLOT_NOT_BOOKABLE"
    assert _book(w, w["vet_id"], "10:30").status_code == 201
    assert _slots(w, w["vet_id"]) == ["10:00", "11:00", "14:00", "14:30"]        # the booked slot is taken


def test_a_new_plan_never_moves_an_existing_booking_and_the_latest_plan_wins(w):
    wd = w["day"].weekday()
    assert _publish(w["vet"], [{"weekday": wd, "opens": "10:00", "closes": "11:00"}]).status_code == 200
    booking = _book(w, w["vet_id"], "10:00").json()["booking_id"]
    assert _publish(w["vet"], [{"weekday": wd, "opens": "15:00", "closes": "16:00"}]).status_code == 200
    assert _slots(w, w["vet_id"]) == ["15:00", "15:30"]
    q = w["vet"].get("/api/vet/queue").json()
    assert [a["booking_id"] for a in q["appointments"]] == [booking]           # still booked, still in the queue
    assert w["vet"].get("/api/vet/availability").json()["windows"] == [{"weekday": wd, "opens": "15:00", "closes": "16:00"}]
    assert _publish(w["vet"], []).status_code == 200                           # an empty plan: no slots at all
    assert _slots(w, w["vet_id"]) == []


@pytest.mark.parametrize("windows", [
    [{"weekday": 7, "opens": "10:00", "closes": "11:00"}],
    [{"weekday": 1, "opens": "10:15", "closes": "11:00"}],
    [{"weekday": 1, "opens": "11:00", "closes": "10:00"}],
    [{"weekday": 1, "opens": "10:00", "closes": "12:00"}, {"weekday": 1, "opens": "11:30", "closes": "13:00"}],
    [{"weekday": 1, "opens": "ten", "closes": "11:00"}],
])
def test_an_invalid_schedule_is_refused_and_changes_nothing(w, windows):
    assert _publish(w["vet"], windows).status_code == 400
    assert w["vet"].get("/api/vet/availability").json()["default_hours"] is True


def test_the_queue_is_the_veterinarians_own_upcoming_bookings_and_open_consultations(w):
    mine = _book(w, w["vet_id"], "11:00").json()["booking_id"]
    _book(w, w["vet2_id"], "11:00")                                            # another veterinarian's booking
    cancelled = _book(w, w["vet_id"], "12:00").json()["booking_id"]
    assert w["owner"].post(f"/api/bookings/{cancelled}/cancel").status_code == 200
    w["owner"].post(f"/api/bookings/{mine}/intake", data={"reason": "Limping", "eating_normally": "YES"})
    open_c = w["vet"].post("/api/consultations", json={"pet_id": w["pet"], "owner_id": w["owner_id"],
                                                       "veterinarian_id": w["vet_id"]}).json()["session_id"]
    done = w["vet"].post("/api/consultations", json={"pet_id": w["pet"], "owner_id": w["owner_id"],
                                                     "veterinarian_id": w["vet_id"]}).json()["session_id"]
    assert w["vet"].post(f"/api/consultations/{done}/outcome", json={"outcome": "Healthy"}).status_code == 200
    q = w["vet"].get("/api/vet/queue").json()
    assert [(a["booking_id"], a["pet"]["name"], a["owner_name"], a["intake_submitted"]) for a in q["appointments"]] == [
        (mine, "Luna", "Huda", True)]
    assert [c["session_id"] for c in q["open_consultations"]] == [open_c]
    assert w["vet2"].get("/api/vet/queue").json()["open_consultations"] == []


def test_only_a_veterinarian_has_a_schedule_and_a_queue(w):
    assert w["owner"].get("/api/vet/queue").status_code == 403
    assert _publish(w["owner"], []).status_code == 403
