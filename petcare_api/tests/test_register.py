"""
Tests for POST /api/auth/register — invite-gated pilot registration.
MVC-UX-WO-001 WI-1 backend acceptance:
  - valid invite registers + reaches portal (here: cookies set + /me works)
  - invalid / used / expired / role-mismatch codes rejected
  - auth.user_registered audit event emitted
"""
import sys
import os
import logging
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app  # noqa: E402
from routers.auth import seed_invite_code, _invite_codes, _users  # noqa: E402


def _new_client():
    return TestClient(app, base_url="https://testserver")


def _unique(prefix: str) -> str:
    """Per-test unique string to avoid shared in-memory state collisions."""
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def test_register_with_valid_invite_returns_201_and_sets_cookies(caplog):
    code = _unique("OWNER")
    email = f"{_unique('new')}@test.com"
    seed_invite_code(code, "owner")

    with caplog.at_level(logging.INFO, logger="petcare.api.auth"):
        r = _new_client().post("/api/auth/register", json={
            "email": email, "password": "Pilot2026!",
            "invite_code": code, "role": "owner",
            "name": "Pilot Owner",
        })

    assert r.status_code == 201
    body = r.json()
    assert body["user"]["email"] == email
    assert body["user"]["role"] == "owner"
    assert "petcare_session" in r.cookies
    assert "petcare_role" in r.cookies
    assert r.cookies["petcare_role"] == "owner"
    assert _invite_codes[code]["used_at"] is not None
    assert _invite_codes[code]["assigned_email"] == email
    assert any("auth.user_registered" in m for m in caplog.messages)


def test_register_then_me_returns_authenticated_user():
    code = _unique("OWNER")
    email = f"{_unique('flow')}@test.com"
    seed_invite_code(code, "owner")

    c = _new_client()
    r = c.post("/api/auth/register", json={
        "email": email, "password": "Pilot2026!",
        "invite_code": code, "role": "owner",
        "name": "Flow Owner",
    })
    assert r.status_code == 201

    me = c.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == email
    assert me.json()["role"] == "owner"


def test_register_with_unknown_invite_returns_400():
    r = _new_client().post("/api/auth/register", json={
        "email": f"{_unique('x')}@test.com", "password": "x",
        "invite_code": "DOES-NOT-EXIST", "role": "owner",
        "name": "X",
    })
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "INVALID_INVITE"


def test_register_with_used_invite_returns_400():
    code = _unique("OWNER")
    seed_invite_code(code, "owner")
    first = _new_client().post("/api/auth/register", json={
        "email": f"{_unique('first')}@test.com", "password": "x",
        "invite_code": code, "role": "owner", "name": "First",
    })
    assert first.status_code == 201

    second = _new_client().post("/api/auth/register", json={
        "email": f"{_unique('second')}@test.com", "password": "x",
        "invite_code": code, "role": "owner", "name": "Second",
    })
    assert second.status_code == 400
    assert second.json()["detail"]["error"] == "INVALID_INVITE"


def test_register_with_expired_invite_returns_400():
    code = _unique("OWNER")
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    seed_invite_code(code, "owner", expires_at=past)

    r = _new_client().post("/api/auth/register", json={
        "email": f"{_unique('x')}@test.com", "password": "x",
        "invite_code": code, "role": "owner", "name": "X",
    })
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "INVITE_EXPIRED"


def test_register_with_role_mismatch_returns_400():
    code = _unique("OWNER")
    seed_invite_code(code, "owner")
    r = _new_client().post("/api/auth/register", json={
        "email": f"{_unique('x')}@test.com", "password": "x",
        "invite_code": code, "role": "veterinarian", "name": "X",
    })
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "ROLE_MISMATCH"


def test_register_with_existing_email_returns_409():
    code1 = _unique("OWNER")
    code2 = _unique("OWNER")
    email = f"{_unique('dup')}@test.com"
    seed_invite_code(code1, "owner")
    seed_invite_code(code2, "owner")

    r1 = _new_client().post("/api/auth/register", json={
        "email": email, "password": "x",
        "invite_code": code1, "role": "owner", "name": "D",
    })
    assert r1.status_code == 201

    r2 = _new_client().post("/api/auth/register", json={
        "email": email, "password": "x",
        "invite_code": code2, "role": "owner", "name": "D",
    })
    assert r2.status_code == 409
    assert r2.json()["detail"]["error"] == "EMAIL_EXISTS"
