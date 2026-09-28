"""MVC-EPC-D-001 D2 — journeys J-O2 (server-side consent ledger) and J-O3 (profile + personal-data export), through the
SERVED app. Step-up is lifted here (conftest); #11 export under step-up is proven in test_epc_d1_sq3_completion."""
import os
import sys
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import owner_consent  # noqa: E402
from adapters.email import FakeEmailAdapter  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402
from test_nfr08_sq3 import _client  # noqa: E402

pytestmark = pytest.mark.served_app


def _purposes(body):
    return {p["purpose"]: p for p in body["purposes"]}


def _uid(prefix):
    return f"u-d2c-{prefix}-{uuid.uuid4().hex[:6]}"


def test_a_new_account_has_no_consent_until_given_and_every_change_is_an_appended_audited_event():
    t = f"t-d2c-{uuid.uuid4().hex[:6]}"
    owner = _client(_uid("o"), "owner", t)
    first = owner.get("/api/me/consents").json()
    assert [p["granted"] for p in first["purposes"]] == [False, False, False] and first["history"] == []
    assert _purposes(first)["privacy_notice"]["revocable"] is False and _purposes(first)["care_reminders"]["revocable"]
    g = owner.post("/api/me/consents/care_reminders", json={"action": "GRANT"}).json()
    assert g["changed"] is True and _purposes(g)["care_reminders"]["granted"] is True
    again = owner.post("/api/me/consents/care_reminders", json={"action": "GRANT"}).json()
    assert again["changed"] is False and len(again["history"]) == 1                 # a no-op writes nothing
    r = owner.post("/api/me/consents/care_reminders", json={"action": "REVOKE"}).json()
    assert r["changed"] is True and _purposes(r)["care_reminders"]["granted"] is False
    assert [h["action"] for h in r["history"]] == ["REVOKE", "GRANT"]              # newest first, nothing rewritten
    admin = _client(_uid("a"), "partner_clinic_admin", t)
    events = [(e["event_name"], e["reason_code"]) for e in admin.get("/audit/events/tenant", params={"limit": 5000}
                                                                          ).json()["events"]
              if e["event_name"].startswith("consent.")]
    assert events == [("consent.granted", "care_reminders"), ("consent.revoked", "care_reminders")]


def test_the_privacy_notice_cannot_be_withdrawn_by_toggle_and_unknown_purposes_or_actions_are_refused():
    owner = _client(_uid("o"), "owner", "t-d2c-consent")
    assert owner.post("/api/me/consents/privacy_notice", json={"action": "GRANT"}).json()["changed"] is True
    r = owner.post("/api/me/consents/privacy_notice", json={"action": "REVOKE"})
    assert r.status_code == 409 and r.json()["detail"]["error"] == "CONSENT_NOT_REVOCABLE"
    assert _purposes(owner.get("/api/me/consents").json())["privacy_notice"]["granted"] is True
    assert owner.post("/api/me/consents/sell_my_data", json={"action": "GRANT"}).status_code == 404
    assert owner.post("/api/me/consents/marketing_messages", json={"action": "MAYBE"}).status_code == 400
    assert owner.post("/api/me/consents/marketing_messages", json={"action": "GRANT", "user_id": "x"}).status_code == 422


def test_consent_is_the_callers_own_and_never_another_users():
    a = _client(_uid("a"), "owner", "t-d2c-iso")
    b = _client(_uid("b"), "owner", "t-d2c-iso")
    a.post("/api/me/consents/marketing_messages", json={"action": "GRANT"})
    mine = b.get("/api/me/consents").json()
    assert _purposes(mine)["marketing_messages"]["granted"] is False and mine["history"] == []
    assert TestClient(api.app).get("/api/me/consents").status_code == 401


def test_self_registration_requires_the_privacy_notice_and_records_it_server_side(monkeypatch):
    ensure_tenant("t-d2c-self")
    monkeypatch.setenv(auth.SELF_REGISTRATION_SWITCH, "on")
    monkeypatch.setenv(auth.SELF_REGISTRATION_TENANT, "t-d2c-self")
    monkeypatch.setattr(auth, "EMAIL_ADAPTER", FakeEmailAdapter())
    c = TestClient(api.app)
    email = f"owner.{uuid.uuid4().hex[:8]}@example.test"
    body = {"email": email, "password": "Owner-passw0rd", "name": "x"}
    r = c.post("/api/auth/self-register", json=body)
    assert r.status_code == 400 and r.json()["detail"]["error"] == "PRIVACY_NOTICE_REQUIRED"
    assert auth.IDENTITY_REPO.get_by_email(email) is None                          # refused before any identity exists
    uid = c.post("/api/auth/self-register", json={**body, "privacy_notice_accepted": True}).json()["user_id"]
    [ev] = api.CONSENT_REPO.events_for(uid, tenant_id="t-d2c-self")
    assert (ev.purpose, ev.action, ev.origin) == ("privacy_notice", "GRANT", "self_registration")


def test_a_profile_edit_changes_only_the_callers_display_name():
    uid = _uid("p")
    owner = _client(uid, "owner", "t-d2c-profile")
    before = auth.IDENTITY_REPO.get_by_user_id(uid)
    assert owner.get("/api/me/profile").json()["full_name"] == before.full_name
    r = owner.put("/api/me/profile", json={"full_name": "  نورة   العتيبي "})
    assert r.status_code == 200 and r.json()["full_name"] == "نورة العتيبي"
    after = auth.IDENTITY_REPO.get_by_user_id(uid)
    assert after.full_name == "نورة العتيبي"
    assert (after.role, after.tenant_id, after.email, after.password_hash) == \
        (before.role, before.tenant_id, before.email, before.password_hash)
    assert owner.put("/api/me/profile", json={"full_name": "   "}).json()["detail"]["error"] == "PROFILE_NAME_INVALID"
    assert owner.put("/api/me/profile", json={"full_name": "x" * 121}).status_code == 400
    assert owner.put("/api/me/profile", json={"full_name": "n", "role": "platform_admin"}).status_code == 422
    assert auth.IDENTITY_REPO.get_by_user_id(uid).role == "owner"


def test_the_personal_data_export_includes_the_consent_history():
    owner = _client(_uid("x"), "owner", "t-d2c-export")
    owner.post("/api/me/consents/care_reminders", json={"action": "GRANT"})
    body = owner.get("/api/me/export").json()
    assert [(c["purpose"], c["action"]) for c in body["consents"]] == [("care_reminders", "GRANT")]


def test_the_ledger_refuses_an_invalid_event():
    repo = owner_consent.InMemoryOwnerConsentRepository()
    with pytest.raises(ValueError):
        repo.append(owner_consent.ConsentEvent("e", "t", "u", "privacy_notice", "DELETE", "account_settings", "v",
                                               datetime.now(timezone.utc)))


@pytest.mark.mfa_enforced
def test_a_step_up_refusal_carries_cors_headers_so_the_web_origin_can_read_it():
    """D2C-REFUSALS-WITHOUT-CORS: the step-up middleware answered 403 OUTSIDE CORS, so a cross-origin browser saw a
    network error instead of MFA_STEP_UP_REQUIRED / MFA_ENROLMENT_REQUIRED and could never show the step-up dialog."""
    origin = api.ALLOWED_ORIGINS[0]
    owner = _client(_uid("cors"), "owner", "t-d2c-cors")
    r = owner.get("/api/me/export", headers={"Origin": origin})
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_ENROLMENT_REQUIRED"
    assert r.headers.get("access-control-allow-origin") == origin
    assert r.headers.get("access-control-allow-credentials") == "true"
    assert "content-disposition" in r.headers.get("access-control-expose-headers", "").lower()
