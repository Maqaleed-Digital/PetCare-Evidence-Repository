import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from main import app
from roles import ROLE_PLATFORM_ADMIN
from routers import auth

client = TestClient(app, base_url="https://testserver")

#: Created BY THIS TEST, not by the application.
#:
#: PRE1_RULING=1-B discarded the three seeded identities and removed the startup
#: path that created them. These tests previously signed in as
#: `admin@myveticare.com` with a password that was a literal in `main.py` — in a
#: PUBLIC repository. A suite that depends on application startup creating a
#: known-credential administrator is a suite that will fail the moment that
#: backdoor is closed, which is exactly what happened here.
#:
#: The password below is a test fixture value and exists only in this file. It
#: is never read by any application path (SEED-02, SEED-05).
FIXTURE_EMAIL = "fixture-admin@test.invalid"
FIXTURE_PASSWORD = "fixture-only-not-a-deployed-credential"


@pytest.fixture(autouse=True)
def fixture_identity():
    """Provision the identity this file signs in as, explicitly."""
    auth.seed_user("u-fixture-admin", FIXTURE_EMAIL, FIXTURE_PASSWORD,
                   ROLE_PLATFORM_ADMIN, "Fixture Admin", tenant_id=None)
    yield


def test_sign_in_wrong_password_returns_401():
    r = client.post("/api/auth/sign-in",
                    json={"email": FIXTURE_EMAIL, "password": "wrong"})
    assert r.status_code == 401


def test_sign_in_unknown_email_returns_401():
    r = client.post("/api/auth/sign-in",
                    json={"email": "nobody@test.com",
                          "password": "anything"})
    assert r.status_code == 401


def test_me_without_cookie_returns_401():
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_sign_out_clears_cookies():
    r = client.post("/api/auth/sign-out")
    assert r.status_code == 200
    assert r.json()["signed_out"] is True


def test_sign_in_valid_sets_cookies():
    r = client.post("/api/auth/sign-in",
                    json={"email": FIXTURE_EMAIL, "password": FIXTURE_PASSWORD})
    assert r.status_code == 200
    assert "petcare_session" in r.cookies
    assert "petcare_role" in r.cookies
    # The CANONICAL machine id, exactly. The previous assertion accepted any of
    # five spellings including `admin`, `vet` and `pharmacy` — none of which the
    # serving layer has ever minted, and one of which is a retired role. An
    # assertion that broad could not have failed on a wrong vocabulary, which is
    # part of why CONF-01 survived so long.
    assert r.json()["user"]["role"] == ROLE_PLATFORM_ADMIN


def test_me_with_valid_session_returns_user():
    c = TestClient(app, base_url="https://testserver", cookies={})
    signin = c.post("/api/auth/sign-in",
                    json={"email": FIXTURE_EMAIL, "password": FIXTURE_PASSWORD})
    assert signin.status_code == 200
    # TestClient persists cookies from the response automatically
    me = c.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == FIXTURE_EMAIL
