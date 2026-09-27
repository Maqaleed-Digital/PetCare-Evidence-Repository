"""NFR-08 MFA MECHANISM — through the SERVED app (MVC-BUILD-RUNNER-001 v1.2 U25; updated v1.3 U28).

The TOTP factor itself: RFC 6238 vectors, enrolment, single-use codes, ciphertext-only storage, nothing in the logs.
U25's environment-configured policy tests are superseded by Sponsor act SQ-3 (the operations and the 15-minute window
are fixed by the act, not by configuration) — see test_nfr08_sq3.py, which carries the NFR-08 evidence.
"""
import base64
import logging
import os
import sys
import time
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import mfa  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-nfr08"


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
    secret = _secret(c.post("/api/me/mfa/enrol", json={"password": "pw"}).json()["otpauth_uri"])
    assert c.post("/api/me/mfa/confirm", json={"code": mfa.totp(secret, time.time())}).status_code == 200
    return secret


def test_totp_matches_the_rfc_6238_vectors():
    k = b"12345678901234567890"
    for t, want in ((59, "94287082"), (1111111109, "07081804"), (1234567890, "89005924"), (2000000000, "69279037")):
        assert mfa.totp(k, t, digits=8) == want


def test_enrolment_confirmation_single_use_codes_and_no_secret_in_logs(caplog):
    c = _client("u-nfr08-owner", "owner")
    with caplog.at_level(logging.DEBUG):
        secret = _secret(c.post("/api/me/mfa/enrol", json={"password": "pw"}).json()["otpauth_uri"])
        assert c.post("/api/me/mfa/confirm", json={"code": "000000" if mfa.totp(secret, time.time()) != "000000"
                                                  else "111111"}).status_code == 401
        code = mfa.totp(secret, time.time())
        assert c.post("/api/me/mfa/confirm", json={"code": code}).status_code == 200
        assert c.post("/api/me/mfa/step-up", json={"code": code}).status_code == 401      # a code is single-use
    b32 = base64.b32encode(secret).decode().rstrip("=")
    assert b32 not in caplog.text and secret.hex() not in caplog.text
    stored = api.MFA_REPO.factor("u-nfr08-owner")
    assert secret not in stored.ciphertext and stored.confirmed_at is not None
