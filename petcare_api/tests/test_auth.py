import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, base_url="https://testserver")


def test_sign_in_wrong_password_returns_401():
    r = client.post("/api/auth/sign-in",
                    json={"email": "admin@myveticare.com",
                          "password": "wrong"})
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
                    json={"email": "admin@myveticare.com",
                          "password": "PetCare2026!"})
    assert r.status_code == 200
    assert "petcare_session" in r.cookies
    assert "petcare_role" in r.cookies
    assert r.json()["user"]["role"] in ["platform_admin", "admin", "owner", "vet", "pharmacy"]


def test_me_with_valid_session_returns_user():
    c = TestClient(app, base_url="https://testserver", cookies={})
    signin = c.post("/api/auth/sign-in",
                    json={"email": "admin@myveticare.com",
                          "password": "PetCare2026!"})
    assert signin.status_code == 200
    # TestClient persists cookies from the response automatically
    me = c.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "admin@myveticare.com"
