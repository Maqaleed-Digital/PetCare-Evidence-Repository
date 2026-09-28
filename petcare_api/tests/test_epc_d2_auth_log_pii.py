"""X-23 (MVC-EPC-D-001 D2) — authentication logs carry no raw email address, and correlation survives.

Every auth log line is written by routers/auth.py `_log_auth_event` (the single sink). Driven through the SERVED app:
registration (success and each refusal), sign-in (success, wrong password, unknown identity), /me and sign-out.
"""
import logging
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


def test_no_auth_log_line_carries_a_raw_email_and_the_reference_correlates_with_the_platform_chain(caplog):
    ensure_tenant("t-x23")
    auth.seed_user("u-x23", "Person.X23@Example.test", "pw", "owner", tenant_id="t-x23")
    code = f"X23-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, "owner")
    new_email = f"new.{uuid.uuid4().hex[:6]}@example.test"
    unknown = "nobody.x23@example.test"
    with caplog.at_level(logging.DEBUG):
        c = TestClient(api.app)
        c.post("/api/auth/register", json={"email": new_email, "password": "Pw-long-enough-1", "invite_code": "NOPE",
                                           "role": "owner", "name": "x"})
        assert c.post("/api/auth/register", json={"email": new_email, "password": "Pw-long-enough-1", "invite_code": code,
                                                  "role": "owner", "name": "x"}).status_code == 201
        c.post("/api/auth/sign-in", json={"email": "Person.X23@Example.test", "password": "wrong"})
        c.post("/api/auth/sign-in", json={"email": unknown, "password": "wrong"})
        r = c.post("/api/auth/sign-in", json={"email": "Person.X23@Example.test", "password": "pw"})
        assert r.status_code == 200                                               # authentication still works
        c.cookies.set("petcare_session", r.cookies["petcare_session"])
        assert c.get("/api/auth/me").status_code == 200
        c.post("/api/auth/sign-out")
    auth_lines = [m for m in caplog.messages if m.startswith("AUTH_EVENT")]
    assert len(auth_lines) >= 6
    text = "\n".join(auth_lines).lower()
    for raw in (new_email, unknown, "person.x23@example.test"):
        assert raw.lower() not in text, raw
    assert "@" not in text                                                        # no address of any kind
    # correlation: the reference in the log is the platform identity chain's subject for the unknown identity
    ref = email_ref(unknown)
    assert ref in "\n".join(auth_lines)
    chain = [e for e in api.PERSISTENCE.platform_audit.events(limit=500) if e.get("subject_ref") == ref]
    assert chain and chain[-1]["event_name"] == "auth.sign_in_failed"
