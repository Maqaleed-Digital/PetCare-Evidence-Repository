"""MVC-EPC-D-001 D2q — CO-10 visit summary and care plan (R21.4). The consultation's veterinarian records ONE care plan after the
outcome; the owner reads the summary of their OWN completed consultation: outcome, the prescriptions issued under THIS session
for THIS pet, and the care plan. Nothing from another session, pet, owner or tenant appears; an incomplete visit is 409."""
import os
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import care_plan as cpl  # noqa: E402
import main as api  # noqa: E402
from ksa_calendar import ksa_date  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role, full_name=None):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@co10.test", "pw", role, full_name=full_name or user_id, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@co10.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2q-co10-{tag}"
    w = {"t": t, "owner_id": f"u-q-own-{tag}", "other_id": f"u-q-oth-{tag}", "vet_id": f"u-q-vet-{tag}",
         "vet2_id": f"u-q-vet2-{tag}"}
    w["owner"] = _client(w["owner_id"], t, "owner")
    w["other"] = _client(w["other_id"], t, "owner")
    w["vet"] = _client(w["vet_id"], t, "veterinarian", full_name="Dr Salma")
    w["vet2"] = _client(w["vet2_id"], t, "veterinarian")
    w["stranger"] = _client(f"u-q-str-{tag}", f"{t}-b", "owner")
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    w["pet_b"] = w["owner"].post("/api/pets", json={"name": "Milo", "species": "cat"}).json()["pet_id"]
    return w


def _visit(w, pet=None, *, outcome="Mild sprain; rest and anti-inflammatory."):
    r = w["vet"].post("/api/consultations", json={"pet_id": pet or w["pet"], "owner_id": w["owner_id"],
                                                  "veterinarian_id": w["vet_id"]})
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]
    if outcome:
        assert w["vet"].post(f"/api/consultations/{sid}/outcome", json={"outcome": outcome}).status_code == 200
    return sid


def _rx(w, sid, pet, med):
    r = w["vet"].post("/api/prescriptions", json={"pet_id": pet, "session_id": sid, "medication_name": med,
                                                 "dosage": "0.5 mg", "instructions": "once daily with food"})
    assert r.status_code == 200, r.text
    return r.json()["prescription_id"]


def _plan(c, sid, **body):
    return c.post(f"/api/consultations/{sid}/care-plan", json={"instructions": "Rest for 7 days; no jumping.", **body})


def test_the_owner_reads_outcome_session_prescriptions_and_care_plan(w):
    sid = _visit(w)
    mine = _rx(w, sid, w["pet"], "Meloxicam")
    _rx(w, _visit(w), w["pet"], "Other-session drug")              # another session of the same pet
    _rx(w, sid, w["pet_b"], "Other-pet drug")                       # same session id, another pet (unchecked link)
    follow = (ksa_date(datetime.now(timezone.utc)) + timedelta(days=14)).isoformat()
    assert _plan(w["vet"], sid, follow_up_on=follow).status_code == 201
    s = w["owner"].get(f"/api/owner/consultations/{sid}/summary")
    assert s.status_code == 200, s.text
    s = s.json()
    assert s["outcome"]["text"] == "Mild sprain; rest and anti-inflammatory."
    assert s["veterinarian"]["name"] == "Dr Salma" and s["pet"]["name"] == "Luna"
    assert [(p["prescription_id"], p["medication_name"], p["instructions"]) for p in s["prescriptions"]] == [
        (mine, "Meloxicam", "once daily with food")]
    assert s["care_plan"]["instructions"] == "Rest for 7 days; no jumping." and s["care_plan"]["follow_up_on"] == follow


def test_a_summary_without_a_care_plan_says_so_and_an_incomplete_visit_is_409(w):
    sid = _visit(w)
    assert w["owner"].get(f"/api/owner/consultations/{sid}/summary").json()["care_plan"] is None
    open_visit = _visit(w, outcome=None)
    r = w["owner"].get(f"/api/owner/consultations/{open_visit}/summary")
    assert r.status_code == 409 and r.json()["detail"]["error"] == "VISIT_NOT_COMPLETED"


def test_only_the_consultations_veterinarian_records_one_care_plan_after_the_outcome(w):
    open_visit = _visit(w, outcome=None)
    r = _plan(w["vet"], open_visit)
    assert r.status_code == 409 and r.json()["detail"]["error"] == "VISIT_NOT_COMPLETED"
    sid = _visit(w)
    assert _plan(w["vet2"], sid).status_code == 403                 # another veterinarian of the clinic
    assert _plan(w["owner"], sid).status_code == 403
    assert _plan(w["vet"], sid).status_code == 201
    again = _plan(w["vet"], sid, instructions="Changed my mind")
    assert again.status_code == 409 and again.json()["detail"]["error"] == "CARE_PLAN_ALREADY_RECORDED"
    assert w["owner"].get(f"/api/owner/consultations/{sid}/summary").json()["care_plan"]["instructions"] == \
        "Rest for 7 days; no jumping."


def test_care_plan_fields_are_validated(w):
    sid = _visit(w)
    yesterday = (ksa_date(datetime.now(timezone.utc)) - timedelta(days=1)).isoformat()
    assert _plan(w["vet"], sid, instructions="   ").status_code == 400
    assert _plan(w["vet"], sid, follow_up_on=yesterday).status_code == 400
    bad = _plan(w["vet"], sid, follow_up_on="next week")
    assert bad.status_code == 400 and bad.json()["detail"]["error"] == "FOLLOW_UP_INVALID"
    assert _plan(w["vet"], sid).status_code == 201                  # nothing was stored by the refusals


def test_another_owner_or_tenant_never_learns_the_visit_exists(w):
    sid = _visit(w)
    assert w["other"].get(f"/api/owner/consultations/{sid}/summary").status_code == 404
    assert w["stranger"].get(f"/api/owner/consultations/{sid}/summary").status_code == 404
    assert w["owner"].get("/api/owner/consultations/not-a-session/summary").status_code == 404
    assert w["vet"].get(f"/api/owner/consultations/{sid}/summary").status_code == 403   # the owner's screen


def test_a_follow_up_is_compared_on_the_riyadh_calendar():
    """Recorded at 22:30 UTC = the next day in Riyadh: a follow-up on the UTC date is already in the past."""
    at = datetime(2031, 3, 1, 22, 30, tzinfo=timezone.utc)
    mk = lambda d: cpl.CarePlan(session_id="s", tenant_id="t", instructions="x", follow_up_on=d, recorded_by_actor_id="v",
                                recorded_at=at)
    cpl.validate_care_plan(mk(date(2031, 3, 2)))
    with pytest.raises(Exception):
        cpl.validate_care_plan(mk(date(2031, 3, 1)))
