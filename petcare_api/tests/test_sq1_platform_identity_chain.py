"""SQ-1 — Sponsor act MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001 (sha256 639c82bf3cebc9cd0347b9683b853a6085362b467d5ccc7dd99ebdd59af20c43)
applied to AC-FR-01-03 through the SERVED app (MVC-BUILD-RUNNER-001 v1.2 U26).

Registration and failed sign-in are account actions on the PLATFORM identity chain — never a tenant chain, no sentinel
tenant — including a failed sign-in against an identity that has a tenant. The tenant chain's tenant-required
invariant is untouched (PostgreSQL assertion in test_sq1_platform_identity_chain_postgres.py).
"""
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from platform_identity_audit import email_ref  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-sq1"


def _admin():
    ensure_tenant(T)
    auth.seed_user("u-sq1-admin", "u-sq1-admin@sq1.test", "pw", "platform_admin", tenant_id=T)
    c = TestClient(api.app)
    c.cookies.set("petcare_session", c.post("/api/auth/sign-in", json={"email": "u-sq1-admin@sq1.test",
                                                                       "password": "pw"}).cookies["petcare_session"])
    return c


def _platform_since(admin, seq):
    body = admin.get("/api/admin/platform-identity-audit", params={"limit": 5000}).json()
    assert body["verify"]["ok"] is True
    return [e for e in body["events"] if e["chain_seq"] > seq]


def _head(admin):
    ev = admin.get("/api/admin/platform-identity-audit", params={"limit": 1}).json()["events"]
    return ev[-1]["chain_seq"] if ev else 0


def _tenant_names(admin):
    return {e["event_name"] for e in admin.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]}


def test_registration_success_and_failure_are_on_the_platform_chain_only():
    admin = _admin()
    seq = _head(admin)
    code = f"SQ1-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, "owner")
    email = f"new-{uuid.uuid4().hex[:6]}@sq1.test"
    c = TestClient(api.app)
    assert c.post("/api/auth/register", json={"email": email, "password": "Pw-long-enough-1", "invite_code": "NOPE",
                                              "role": "owner", "name": "x"}).status_code == 400
    assert c.post("/api/auth/register", json={"email": email, "password": "Pw-long-enough-1", "invite_code": code,
                                              "role": "owner", "name": "x"}).status_code == 201
    new = _platform_since(admin, seq)
    kinds = [(e["event_name"], e["outcome"], e["subject_kind"]) for e in new]
    assert ("auth.register_failed", "denied", "UNKNOWN_IDENTITY") in kinds
    assert ("auth.user_registered", "success", "IDENTITY") in kinds
    assert all("tenant_id" not in e for e in new)
    assert email not in str(new) and email_ref(email) in [e["subject_ref"] for e in new]
    assert not {n for n in _tenant_names(admin) if n.startswith("auth.")}


def test_every_failed_sign_in_is_on_the_platform_chain_even_for_an_identity_with_a_tenant():
    admin = _admin()
    auth.seed_user("u-sq1-owner", "u-sq1-owner@sq1.test", "pw", "owner", tenant_id=T)
    seq = _head(admin)
    c = TestClient(api.app)
    unknown = c.post("/api/auth/sign-in", json={"email": "ghost@sq1.test", "password": "pw"})
    known = c.post("/api/auth/sign-in", json={"email": "u-sq1-owner@sq1.test", "password": "wrong"})
    assert (unknown.status_code, unknown.json()) == (known.status_code, known.json()) == (401, {"detail": {"error": "INVALID_CREDENTIALS"}})
    failed = [e for e in _platform_since(admin, seq) if e["event_name"] == "auth.sign_in_failed"]
    assert {(e["subject_kind"], e["subject_ref"]) for e in failed} == {("UNKNOWN_IDENTITY", email_ref("ghost@sq1.test")),
                                                                      ("IDENTITY", "u-sq1-owner")}
    assert all(e["outcome"] == "denied" for e in failed)
    assert "auth.sign_in_failed" not in _tenant_names(admin)                  # never on the owner's tenant chain
