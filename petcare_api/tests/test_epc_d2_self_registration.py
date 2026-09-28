"""MVC-EPC-D-001 D2 — owner self-registration behind PETCARE_OWNER_SELF_REGISTRATION (Sponsor ruling 1, production
default OFF), email verification through the governed email adapter, password reset. Served app; both switch states."""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import account_tokens  # noqa: E402
import main as api  # noqa: E402
from adapters.email import EmailUnavailable, FakeEmailAdapter, UnconfiguredEmailAdapter, build_email_adapter  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-d2-self"
PW = "Owner-passw0rd"


@pytest.fixture
def enabled(monkeypatch):
    ensure_tenant(T)
    fake = FakeEmailAdapter()
    monkeypatch.setenv(auth.SELF_REGISTRATION_SWITCH, "on")
    monkeypatch.setenv(auth.SELF_REGISTRATION_TENANT, T)
    monkeypatch.setattr(auth, "EMAIL_ADAPTER", fake)
    return fake


def _email():
    return f"owner.{uuid.uuid4().hex[:8]}@example.test"


def _token(fake, template):
    return fake.outbox[-1].params["link"].split("token=", 1)[1] if fake.outbox[-1].template == template else None


def test_switch_off_is_the_default_and_self_registration_fails_closed_with_no_bypass(monkeypatch):
    monkeypatch.delenv(auth.SELF_REGISTRATION_SWITCH, raising=False)
    c = TestClient(api.app)
    assert c.get("/api/auth/registration-options").json() == {"owner_self_registration": False}
    email = _email()
    r = c.post("/api/auth/self-register", json={"email": email, "password": PW, "name": "x", "privacy_notice_accepted": True})
    assert r.status_code == 404 and r.json()["detail"]["error"] == "SELF_REGISTRATION_DISABLED"
    assert auth.IDENTITY_REPO.get_by_email(email) is None
    # the invite-only pilot path is unchanged and still refuses without an invite
    assert c.post("/api/auth/register", json={"email": email, "password": PW, "invite_code": "none", "role": "owner",
                                              "name": "x"}).status_code == 400


def test_switch_on_register_verify_then_sign_in(enabled):
    c = TestClient(api.app)
    assert c.get("/api/auth/registration-options").json() == {"owner_self_registration": True}
    email = _email()
    assert c.post("/api/auth/self-register", json={"email": email, "password": "short", "name": "x", "privacy_notice_accepted": True}).status_code == 400
    r = c.post("/api/auth/self-register", json={"email": email.upper(), "password": PW, "name": "مالك", "locale": "ar", "privacy_notice_accepted": True})
    assert r.status_code == 201 and r.json()["verification_required"] is True
    ident = auth.IDENTITY_REPO.get_by_email(email)
    assert ident.role == "owner" and ident.tenant_id == T                       # tenant from SERVER config
    assert c.post("/api/auth/self-register", json={"email": email, "password": PW, "name": "x", "privacy_notice_accepted": True}).status_code == 409
    r = c.post("/api/auth/sign-in", json={"email": email, "password": PW})
    assert r.status_code == 403 and r.json()["detail"]["error"] == "EMAIL_NOT_VERIFIED"
    msg = enabled.outbox[-1]
    assert msg.to == email and msg.template == "EMAIL_VERIFICATION" and msg.locale == "ar"
    token = _token(enabled, "EMAIL_VERIFICATION")
    assert token not in str(api.PERSISTENCE.account_tokens._tokens)            # stored as sha256 only
    assert c.post("/api/auth/verify-email", json={"token": token}).json() == {"verified": True}
    assert c.post("/api/auth/verify-email", json={"token": token}).status_code == 400     # single use
    assert c.post("/api/auth/sign-in", json={"email": email, "password": PW}).status_code == 200


def test_switch_on_fails_closed_without_an_email_provider_or_a_tenant(monkeypatch):
    ensure_tenant(T)
    monkeypatch.setenv(auth.SELF_REGISTRATION_SWITCH, "on")
    monkeypatch.setenv(auth.SELF_REGISTRATION_TENANT, T)
    monkeypatch.setattr(auth, "EMAIL_ADAPTER", UnconfiguredEmailAdapter())
    c = TestClient(api.app)
    email = _email()
    r = c.post("/api/auth/self-register", json={"email": email, "password": PW, "name": "x", "privacy_notice_accepted": True})
    assert r.status_code == 503 and auth.IDENTITY_REPO.get_by_email(email) is None
    monkeypatch.setenv(auth.SELF_REGISTRATION_TENANT, "t-does-not-exist")
    monkeypatch.setattr(auth, "EMAIL_ADAPTER", FakeEmailAdapter())
    r = c.post("/api/auth/self-register", json={"email": email, "password": PW, "name": "x", "privacy_notice_accepted": True})
    assert r.status_code == 503 and r.json()["detail"]["error"] == "SELF_REGISTRATION_TENANT_UNAVAILABLE"


def test_password_reset_does_not_enumerate_is_single_use_and_revokes_sessions(enabled):
    c = TestClient(api.app)
    email = _email()
    c.post("/api/auth/self-register", json={"email": email, "password": PW, "name": "x", "privacy_notice_accepted": True})
    c.post("/api/auth/verify-email", json={"token": _token(enabled, "EMAIL_VERIFICATION")})
    s = TestClient(api.app)
    r = s.post("/api/auth/sign-in", json={"email": email, "password": PW})
    s.cookies.set("petcare_session", r.cookies["petcare_session"])
    assert s.get("/api/auth/me").status_code == 200
    sent = len(enabled.outbox)
    assert c.post("/api/auth/password-reset/request", json={"email": "nobody@example.test"}).status_code == 202
    assert len(enabled.outbox) == sent                                           # nothing sent, same answer
    assert c.post("/api/auth/password-reset/request", json={"email": email}).status_code == 202
    token = _token(enabled, "PASSWORD_RESET")
    assert c.post("/api/auth/password-reset/confirm", json={"token": token, "password": "short"}).status_code == 400
    r = c.post("/api/auth/password-reset/confirm", json={"token": token, "password": "New-passw0rd-2"})
    assert r.status_code == 200 and r.json()["sessions_revoked"] >= 1
    assert s.get("/api/auth/me").status_code == 401                              # every session ended
    assert c.post("/api/auth/password-reset/confirm", json={"token": token, "password": "Other-passw0rd"}).status_code == 400
    assert c.post("/api/auth/sign-in", json={"email": email, "password": PW}).status_code == 401
    assert c.post("/api/auth/sign-in", json={"email": email, "password": "New-passw0rd-2"}).status_code == 200


def test_tokens_expire_and_the_fake_adapter_is_refused_in_production():
    repo = account_tokens.InMemoryAccountTokenRepository()
    now = datetime(2031, 1, 1, tzinfo=timezone.utc)
    raw = repo.issue("u-x", "PASSWORD_RESET", now=now)
    assert repo.consume(raw, "EMAIL_VERIFICATION", now=now) is None             # wrong purpose
    assert repo.consume(raw, "PASSWORD_RESET", now=now + timedelta(minutes=30)) is None   # expired at 30 minutes
    assert isinstance(build_email_adapter({}), UnconfiguredEmailAdapter)       # default: unconfigured, fails closed
    with pytest.raises(EmailUnavailable):
        build_email_adapter({"PETCARE_EMAIL_ADAPTER": "fake", "PETCARE_DEPLOYMENT_ENV": "production"})
    assert FakeEmailAdapter.LABEL.startswith("FAKE")
