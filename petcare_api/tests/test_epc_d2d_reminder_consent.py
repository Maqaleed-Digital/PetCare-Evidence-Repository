"""MVC-EPC-D-001 D2d — Sponsor ruling R10 / X-25: `care_reminders` consent is ENFORCED at the FR-23 dispatch boundary
(POST /api/reminders/run), read from the server ledger immediately before each send, and fails closed.

Every served-app test below proves dispatch through what the OWNER can read back (/api/me/reminders) and through the
audit trail — not through consent storage or UI state. No provider is reached: delivery is IN_APP."""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import owner_consent as oc  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@d2d.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@d2d.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _world():
    t = f"t-d2d-{uuid.uuid4().hex[:6]}"
    tag = uuid.uuid4().hex[:6]
    owner_id = f"u-d2d-o-{tag}"
    return (t, owner_id, _client(f"u-d2d-v-{tag}", t, "veterinarian"), _client(owner_id, t, "owner"),
            _client(f"u-d2d-a-{tag}", t, "partner_clinic_admin"))


def _due(vet, owner, *, in_hours=72):
    pet = owner.post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    at = (datetime.now(timezone.utc) + timedelta(hours=in_hours)).isoformat()
    r = vet.post(f"/api/pets/{pet}/care-due", json={"kind": "VACCINATION", "title": "Rabies", "due_at": at})
    assert r.status_code == 200, r.text
    return r.json()["due_id"]


def _consent(owner, action):
    r = owner.post("/api/me/consents/care_reminders", json={"action": action})
    assert r.status_code == 200 and r.json()["changed"] is True, r.text


def _audit(admin, name):
    return [e for e in admin.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
            if e["event_name"] == name]


# ------------------------------------------------------------------------------------------- 1. consent -> admitted
def test_with_effective_consent_the_reminder_is_dispatched_to_the_owner():
    _t, owner_id, vet, owner, admin = _world()
    _consent(owner, "GRANT")
    due = _due(vet, owner)
    run = admin.post("/api/reminders/run").json()
    assert [(s["due_id"], s["owner_id"]) for s in run["sent"]] == [(due, owner_id)] and run["withheld"] == []
    assert [r["due_id"] for r in owner.get("/api/me/reminders").json()] == [due]


# ------------------------------------------------------------------------------------------- 2. absent -> refused
def test_without_any_consent_event_nothing_is_dispatched_and_the_refusal_is_audited():
    _t, owner_id, vet, owner, admin = _world()
    due = _due(vet, owner)
    run = admin.post("/api/reminders/run").json()
    assert run["sent"] == [] and run["withheld"] == [{"due_id": due, "owner_id": owner_id, "reason": "CONSENT_ABSENT"}]
    assert owner.get("/api/me/reminders").json() == []
    (ev,) = [e for e in _audit(admin, "reminder.withheld") if e["resource_id"] == due]
    assert ev["action_result"] == "denied" and ev["reason_code"] == f"CONSENT_ABSENT:owner:{owner_id}"
    assert not [e for e in _audit(admin, "reminder.sent") if owner_id in (e.get("reason_code") or "")]


# ------------------------------------------------------------------------------------------- 3. revoked -> refused
def test_a_revoked_consent_refuses_dispatch():
    _t, owner_id, vet, owner, admin = _world()
    _consent(owner, "GRANT")
    _consent(owner, "REVOKE")
    due = _due(vet, owner)
    run = admin.post("/api/reminders/run").json()
    assert run["sent"] == [] and run["withheld"] == [{"due_id": due, "owner_id": owner_id, "reason": "CONSENT_REVOKED"}]
    assert owner.get("/api/me/reminders").json() == []


# ------------------------------------------------------------------------------------------- 4. indeterminate -> closed
def test_an_unreadable_ledger_fails_closed_at_the_dispatch_boundary(monkeypatch):
    _t, owner_id, vet, owner, admin = _world()
    _consent(owner, "GRANT")
    due = _due(vet, owner)

    def _broken(*_a, **_k):
        raise RuntimeError("ledger unavailable")

    monkeypatch.setattr(api.CONSENT_REPO, "latest", _broken)
    run = admin.post("/api/reminders/run").json()
    assert run["sent"] == [] and run["withheld"] == [{"due_id": due, "owner_id": owner_id, "reason": "CONSENT_UNREADABLE"}]
    assert owner.get("/api/me/reminders").json() == []


def test_a_malformed_ledger_record_fails_closed_at_the_dispatch_boundary(monkeypatch):
    _t, owner_id, vet, owner, admin = _world()
    _consent(owner, "GRANT")
    _due(vet, owner)
    monkeypatch.setattr(api.CONSENT_REPO, "latest", lambda *_a, **_k: {"purpose": "care_reminders", "action": "GRANT"})
    run = admin.post("/api/reminders/run").json()
    assert run["sent"] == [] and run["withheld"][0]["reason"] == "CONSENT_MALFORMED"
    assert owner.get("/api/me/reminders").json() == []


# ------------------------------------------------------------------------------------------- 5. revoke after consent
def test_revoking_after_an_earlier_consent_stops_every_later_dispatch(monkeypatch):
    _t, owner_id, vet, owner, admin = _world()
    _consent(owner, "GRANT")
    due = _due(vet, owner, in_hours=6 * 24)                              # inside the 7-day window
    first = admin.post("/api/reminders/run").json()
    assert [(s["due_id"], s["kind"]) for s in first["sent"]] == [(due, "REMIND_7D")]
    _consent(owner, "REVOKE")
    real = datetime

    class _Clock(real):
        @classmethod
        def now(cls, tz=None):
            return real.now(tz) + timedelta(hours=6 * 24 - 12)           # the 24-hour reminder is now due

    monkeypatch.setattr(api, "datetime", _Clock)
    later = admin.post("/api/reminders/run").json()
    assert later["sent"] == [] and later["withheld"] == [{"due_id": due, "owner_id": owner_id, "reason": "CONSENT_REVOKED"}]
    assert [(r["due_id"], r["kind"]) for r in owner.get("/api/me/reminders").json()] == [(due, "REMIND_7D")]


# ------------------------------------------------------------------------------------------- tenant scoping
def test_consent_given_in_another_tenant_does_not_admit_dispatch_here():
    _t, owner_id, vet, owner, admin = _world()
    other = f"t-d2d-other-{uuid.uuid4().hex[:6]}"
    api.CONSENT_REPO.append(oc.ConsentEvent(event_id=str(uuid.uuid4()), tenant_id=other, user_id=owner_id,
                                            purpose=oc.CARE_REMINDERS, action=oc.GRANT, origin="account_settings",
                                            policy_version=oc.POLICY_VERSION, at=datetime.now(timezone.utc)))
    due = _due(vet, owner)
    run = admin.post("/api/reminders/run").json()
    assert run["sent"] == [] and run["withheld"][0] == {"due_id": due, "owner_id": owner_id, "reason": "CONSENT_ABSENT"}


# ------------------------------------------------------------------------------------------- the decision itself
class _Repo:
    def __init__(self, latest=None, exc=None):
        self._latest, self._exc = latest, exc

    def latest(self, *_a, **_k):
        if self._exc:
            raise self._exc
        return self._latest


def _ev(**kw):
    base = dict(event_id="e", tenant_id="t", user_id="u", purpose=oc.CARE_REMINDERS, action=oc.GRANT,
                origin="account_settings", policy_version=oc.POLICY_VERSION, at=datetime.now(timezone.utc))
    return oc.ConsentEvent(**{**base, **kw})


@pytest.mark.parametrize("repo, expected", [
    (_Repo(_ev()), (True, oc.CONSENT_GRANTED)),
    (_Repo(None), (False, oc.CONSENT_ABSENT)),
    (_Repo(_ev(action=oc.REVOKE)), (False, oc.CONSENT_REVOKED)),
    (_Repo(exc=ConnectionError("db down")), (False, oc.CONSENT_UNREADABLE)),
    (_Repo(_ev(action="MAYBE")), (False, oc.CONSENT_MALFORMED)),
    (_Repo(_ev(purpose=oc.MARKETING)), (False, oc.CONSENT_MALFORMED)),
    (_Repo(_ev(user_id="someone-else")), (False, oc.CONSENT_MALFORMED)),
    (_Repo(_ev(tenant_id="another-tenant")), (False, oc.CONSENT_MALFORMED)),
    (_Repo("GRANT"), (False, oc.CONSENT_MALFORMED)),
])
def test_the_dispatch_decision_admits_only_a_well_formed_grant(repo, expected):
    assert oc.reminder_dispatch_decision(repo, "u", tenant_id="t") == expected


# ------------------------------------------------------------------------------------------- R13.3 onboarding capture
@pytest.fixture
def self_registration(monkeypatch):
    from adapters.email import FakeEmailAdapter
    t = f"t-d2d-self-{uuid.uuid4().hex[:6]}"
    ensure_tenant(t)
    monkeypatch.setenv(auth.SELF_REGISTRATION_SWITCH, "on")
    monkeypatch.setenv(auth.SELF_REGISTRATION_TENANT, t)
    monkeypatch.setattr(auth, "EMAIL_ADAPTER", FakeEmailAdapter())
    return t


def _register(**extra):
    body = {"email": f"owner.{uuid.uuid4().hex[:8]}@example.test", "password": "Owner-passw0rd", "name": "Owner",
            "privacy_notice_accepted": True, **extra}
    return TestClient(api.app).post("/api/auth/self-register", json=body)


def _purposes(user_id, tenant):
    return [(e.purpose, e.action, e.origin) for e in api.CONSENT_REPO.events_for(user_id, tenant_id=tenant)]


def test_an_owner_who_leaves_care_reminders_unticked_gives_no_reminder_consent(self_registration):
    r = _register()                                                     # the choice is optional; default is off
    assert r.status_code == 201, r.text
    uid = r.json()["user_id"]
    assert _purposes(uid, self_registration) == [("privacy_notice", "GRANT", "self_registration")]
    assert oc.reminder_dispatch_decision(api.CONSENT_REPO, uid, tenant_id=self_registration) == (False, oc.CONSENT_ABSENT)
    r = _register(care_reminders=False)
    assert r.status_code == 201 and _purposes(r.json()["user_id"], self_registration) == [
        ("privacy_notice", "GRANT", "self_registration")]


def test_an_owner_who_ticks_care_reminders_at_signup_is_recorded_server_side_and_admitted(self_registration):
    r = _register(care_reminders=True)
    assert r.status_code == 201, r.text
    uid = r.json()["user_id"]
    # both are written at the same instant; the ledger orders ties by event id, so compare as a set
    assert sorted(_purposes(uid, self_registration)) == [("care_reminders", "GRANT", "self_registration"),
                                                         ("privacy_notice", "GRANT", "self_registration")]
    assert oc.reminder_dispatch_decision(api.CONSENT_REPO, uid, tenant_id=self_registration) == (True, oc.CONSENT_GRANTED)


@pytest.mark.parametrize("value", ["yes", "true", 1])
def test_only_a_real_boolean_counts_as_a_care_reminders_choice(self_registration, value):
    r = _register(care_reminders=value)
    assert r.status_code == 422, r.text


def test_care_reminders_cannot_stand_in_for_the_privacy_notice(self_registration):
    r = _register(privacy_notice_accepted=False, care_reminders=True)
    assert r.status_code == 400 and r.json()["detail"]["error"] == "PRIVACY_NOTICE_REQUIRED"
