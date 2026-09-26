"""NFR-08 MFA step-up MECHANISM — through the SERVED app (MVC-BUILD-RUNNER-001 v1.2 U25).

NOT registered as NFR-08 evidence: the ratified evidence_definition does not name the sensitive operations, the
step-up freshness window or recovery (SPONSOR_QUEUE SQ-3). The tests configure ONE operation and a window IN-PROCESS
(test configuration) to prove the mechanism; production configuration enforces nothing until the Sponsor decides.
"""
import base64
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import mfa  # noqa: E402
from repositories import RepositoryDenied  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-nfr08"
OP = "POST /api/admin/practitioners/{user_id}/authority"


def _client(user_id, role):
    ensure_tenant(T)
    auth.seed_user(user_id, f"{user_id}@nfr08.test", "pw", role, tenant_id=T)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@nfr08.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _secret(uri):
    b32 = parse_qs(urlparse(uri).query)["secret"][0]
    return base64.b32decode(b32 + "=" * (-len(b32) % 8))


def _enrol_and_confirm(c):
    secret = _secret(c.post("/api/me/mfa/enrol").json()["otpauth_uri"])
    assert c.post("/api/me/mfa/confirm", json={"code": mfa.totp(secret, time.time())}).status_code == 200
    return secret


def test_totp_matches_the_rfc_6238_vectors():
    k = b"12345678901234567890"
    for t, want in ((59, "94287082"), (1111111109, "07081804"), (1234567890, "89005924"), (2000000000, "69279037")):
        assert mfa.totp(k, t, digits=8) == want


def test_enrolment_confirmation_single_use_codes_and_no_secret_in_logs(caplog):
    c = _client("u-nfr08-owner", "owner")
    with caplog.at_level(logging.DEBUG):
        secret = _secret(c.post("/api/me/mfa/enrol").json()["otpauth_uri"])
        assert c.post("/api/me/mfa/confirm", json={"code": "000000" if mfa.totp(secret, time.time()) != "000000"
                                                  else "111111"}).status_code == 401
        code = mfa.totp(secret, time.time())
        assert c.post("/api/me/mfa/confirm", json={"code": code}).status_code == 200
        assert c.post("/api/me/mfa/step-up", json={"code": code}).status_code == 401      # a code is single-use
    b32 = base64.b32encode(secret).decode().rstrip("=")
    assert b32 not in caplog.text and secret.hex() not in caplog.text
    stored = api.MFA_REPO.factor("u-nfr08-owner")
    assert secret not in stored.ciphertext and stored.confirmed_at is not None


def test_a_configured_sensitive_operation_requires_a_fresh_session_bound_step_up(monkeypatch):
    monkeypatch.setattr(api, "MFA_POLICY", mfa.MfaPolicy(frozenset({OP}), 300))
    admin = _client("u-nfr08-admin", "platform_admin")
    ensure_tenant(T)
    auth.seed_user("u-nfr08-vet", "u-nfr08-vet@nfr08.test", "pw", "veterinarian", tenant_id=T)
    grant = lambda c: c.post("/api/admin/practitioners/u-nfr08-vet/authority", json={"licence_ref": "MEWA-1"})
    r = grant(admin)
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_ENROLMENT_REQUIRED"
    secret = _enrol_and_confirm(admin)
    r = grant(admin)
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    assert admin.post("/api/me/mfa/step-up", json={"code": mfa.totp(secret, time.time() + 30)}).status_code == 200
    assert grant(admin).status_code == 200
    other_session = _client("u-nfr08-admin", "platform_admin")                           # same person, new session
    assert grant(other_session).json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    assert admin.get("/api/admin/rate-limits").status_code == 200                           # other operations unaffected
    real = datetime

    class _Later(real):
        @classmethod
        def now(cls, tz=None):
            return real.now(tz) + timedelta(seconds=301)

    monkeypatch.setattr(api, "datetime", _Later)
    assert grant(admin).json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"                # freshness expired


def test_the_runner_chooses_no_parameters_the_ratified_text_does_not_fix():
    default = mfa.MfaPolicy.from_env({})
    assert default.sensitive_operations == frozenset() and default.max_age_seconds is None
    with pytest.raises(RepositoryDenied):
        mfa.MfaPolicy.from_env({mfa.ENV_OPERATIONS: OP})                                    # no default window
    assert mfa.MfaPolicy.from_env({mfa.ENV_OPERATIONS: OP, mfa.ENV_MAX_AGE: "120"}).max_age_seconds == 120
    assert api.MFA_POLICY.sensitive_operations == frozenset()                               # served default: none
