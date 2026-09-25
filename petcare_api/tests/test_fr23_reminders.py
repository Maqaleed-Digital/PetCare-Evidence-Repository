"""FR-23 vaccination and treatment reminders — ratified AC-FR-23-01/02 through the SERVED app
(MVC-BUILD-RUNNER-001 U15). Ratified defaults: 7 days before due; a second 24 hours before due if outstanding;
never suppressible. AC-FR-23-03/04 (EXTERNAL:SMS_GATEWAY) are not exercised: delivery is IN_APP."""
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr23-alpha", "t-fr23-beta"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr23.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr23.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _pet(owner, name="Luna"):
    return owner.post("/api/pets", json={"name": name, "species": "cat"}).json()["pet_id"]


def _due(vet, pet_id, *, in_hours, title="Rabies booster", kind="VACCINATION"):
    at = (datetime.now(timezone.utc) + timedelta(hours=in_hours)).isoformat()
    r = vet.post(f"/api/pets/{pet_id}/care-due", json={"kind": kind, "title": title, "due_at": at})
    assert r.status_code == 200, r.text
    return r.json()["due_id"]


def _mine(owner):
    return owner.get("/api/me/reminders").json()


def _later(monkeypatch, hours):
    real = datetime

    class _Clock(real):
        @classmethod
        def now(cls, tz=None):
            return real.now(tz) + timedelta(hours=hours)

    monkeypatch.setattr(api, "datetime", _Clock)


# --------------------------------------------------------------------------- AC-FR-23-01
def test_a_due_date_reminds_the_owner_seven_days_and_again_24_hours_before_if_outstanding(monkeypatch):
    vet = _client("u-fr23-vet", T_A, "veterinarian")
    owner = _client("u-fr23-owner", T_A, "owner")
    admin = _client("u-fr23-admin", T_A, "partner_clinic_admin")
    pet = _pet(owner)
    near = _due(vet, pet, in_hours=6 * 24)                          # inside the 7-day window
    given = _due(vet, pet, in_hours=6 * 24, title="Deworming", kind="TREATMENT")
    far = _due(vet, pet, in_hours=30 * 24)                          # not yet
    sent = admin.post("/api/reminders/run").json()["sent"]
    assert sorted((s["due_id"], s["kind"]) for s in sent) == sorted([(near, "REMIND_7D"), (given, "REMIND_7D")])
    assert admin.post("/api/reminders/run").json()["sent"] == []     # idempotent
    assert {r["due_id"] for r in _mine(owner)} == {near, given} and far not in {r["due_id"] for r in _mine(owner)}
    assert vet.post(f"/api/pets/{pet}/care-due/{given}/complete").status_code == 200
    _later(monkeypatch, 6 * 24 - 12)                                # now 12 hours before both are due
    second = admin.post("/api/reminders/run").json()["sent"]
    assert [(s["due_id"], s["kind"]) for s in second] == [(near, "REMIND_24H")]   # the completed one is not outstanding
    kinds = {(r["due_id"], r["kind"]) for r in _mine(owner)}
    assert (near, "REMIND_24H") in kinds and (given, "REMIND_24H") not in kinds


def test_reminders_never_reach_another_tenants_owner():
    vet_a, owner_a, admin_a = (_client("u-fr23-vet-a", T_A, "veterinarian"), _client("u-fr23-owner-a", T_A, "owner"),
                               _client("u-fr23-admin-a", T_A, "partner_clinic_admin"))
    vet_b, owner_b, admin_b = (_client("u-fr23-vet-b", T_B, "veterinarian"), _client("u-fr23-owner-b", T_B, "owner"),
                               _client("u-fr23-admin-b", T_B, "partner_clinic_admin"))
    pet_b = _pet(owner_b, "Max")
    assert vet_a.post(f"/api/pets/{pet_b}/care-due", json={"kind": "VACCINATION", "title": "x",
                                                            "due_at": datetime.now(timezone.utc).isoformat()}).status_code == 404
    due_b = _due(vet_b, pet_b, in_hours=48)
    assert all(s["owner_id"] != "u-fr23-owner-b" for s in admin_a.post("/api/reminders/run").json()["sent"])
    assert _mine(owner_b) == []
    assert {s["due_id"] for s in admin_b.post("/api/reminders/run").json()["sent"]} == {due_b}
    assert {r["due_id"] for r in _mine(owner_b)} == {due_b} and due_b not in {r["due_id"] for r in _mine(owner_a)}


# --------------------------------------------------------------------------- AC-FR-23-02
def test_reminders_are_in_the_owners_language_and_every_send_is_audited():
    vet = _client("u-fr23-vet3", T_A, "veterinarian")
    owner_ar = _client("u-fr23-owner-ar", T_A, "owner")
    owner_en = _client("u-fr23-owner-en", T_A, "owner")
    admin = _client("u-fr23-admin3", T_A, "partner_clinic_admin")
    assert owner_en.put("/api/me/preferences/language", json={"language": "en"}).status_code == 200
    d_ar = _due(vet, _pet(owner_ar, "Bella"), in_hours=72)
    d_en = _due(vet, _pet(owner_en, "Rex"), in_hours=72)
    admin.post("/api/reminders/run")
    ar = [r for r in _mine(owner_ar) if r["due_id"] == d_ar][0]
    en = [r for r in _mine(owner_en) if r["due_id"] == d_en][0]
    assert ar["language"] == "ar" and re.search(r"[؀-ۿ]", ar["body"]) and "Reminder" not in ar["body"]
    assert en["language"] == "en" and en["body"].startswith("Reminder")
    audited = {e["resource_id"]: e for e in admin.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
               if e["event_name"] == "reminder.sent"}
    assert audited[ar["reminder_id"]]["actor_id"] == "u-fr23-admin3" and ":ar:" in audited[ar["reminder_id"]]["reason_code"]
    assert ":en:" in audited[en["reminder_id"]]["reason_code"]
