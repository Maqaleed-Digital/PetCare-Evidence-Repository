"""FR-07 — consultation messaging and file sharing through the SERVED app (MVC-BUILD-RUNNER-001 U7).

AC-FR-07-01 fails if "an image or lab-report file cannot be attached and retrieved by the
other party; or a message is visible to anyone outside the consultation". AC-FR-07-02:
every notification delivery attempt writes a record carrying the rendered body.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-msg-alpha", "t-msg-beta"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def _client(user_id: str, tenant: str, role: str) -> TestClient:
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@msg.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@msg.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _consultation(vet: TestClient, owner_id: str, vet_id: str, tenant: str = T_A) -> str:
    r = vet.post("/api/consultations", json={"pet_id": "p1", "owner_id": owner_id,
                                             "veterinarian_id": vet_id, "tenant_id": tenant})
    assert r.status_code == 200, r.text
    return r.json()["session_id"]


def test_owner_and_vet_exchange_messages_and_a_lab_report_file():
    owner, vet = _client("u-msg-owner1", T_A, "owner"), _client("u-msg-vet1", T_A, "veterinarian")
    cid = _consultation(vet, "u-msg-owner1", "u-msg-vet1")
    assert owner.post(f"/api/consultations/{cid}/messages", json={"body": "Luna is coughing"}).status_code == 200
    reply = vet.post(f"/api/consultations/{cid}/messages", json={"body": "Here is the lab report"}).json()
    att = vet.post(f"/api/consultations/{cid}/messages/{reply['message_id']}/attachments",
                   files={"file": ("cbc.png", PNG, "image/png")})
    assert att.status_code == 200, att.text
    listed = owner.get(f"/api/consultations/{cid}/messages").json()
    assert [m["body"] for m in listed] == ["Luna is coughing", "Here is the lab report"]
    aid = listed[1]["attachments"][0]["attachment_id"]
    got = owner.get(f"/api/consultations/{cid}/messages/{reply['message_id']}/attachments/{aid}")
    assert got.status_code == 200 and got.content == PNG


def test_messages_are_invisible_outside_the_consultation():
    owner, vet = _client("u-msg-owner2", T_A, "owner"), _client("u-msg-vet2", T_A, "veterinarian")
    cid = _consultation(vet, "u-msg-owner2", "u-msg-vet2")
    m = owner.post(f"/api/consultations/{cid}/messages", json={"body": "private"}).json()
    stranger = _client("u-msg-owner-x", T_A, "owner")
    other_vet = _client("u-msg-vet-x", T_A, "veterinarian")
    other_tenant = _client("u-msg-vet-b", T_B, "veterinarian")
    for c in (stranger, other_vet, other_tenant):
        assert c.get(f"/api/consultations/{cid}/messages").status_code == 404
        assert c.post(f"/api/consultations/{cid}/messages", json={"body": "x"}).status_code == 404
        assert c.post(f"/api/consultations/{cid}/messages/{m['message_id']}/attachments",
                      files={"file": ("a.png", PNG, "image/png")}).status_code == 404


def test_unsupported_file_type_is_refused():
    owner, vet = _client("u-msg-owner3", T_A, "owner"), _client("u-msg-vet3", T_A, "veterinarian")
    cid = _consultation(vet, "u-msg-owner3", "u-msg-vet3")
    m = vet.post(f"/api/consultations/{cid}/messages", json={"body": "file"}).json()
    r = vet.post(f"/api/consultations/{cid}/messages/{m['message_id']}/attachments",
                 files={"file": ("x.svg", b"<svg onload=alert(1)/>", "image/svg+xml")})
    assert r.status_code == 400


def test_each_delivery_attempt_is_recorded_with_the_rendered_body_and_audited():
    owner, vet = _client("u-msg-owner4", T_A, "owner"), _client("u-msg-vet4", T_A, "veterinarian")
    cid = _consultation(vet, "u-msg-owner4", "u-msg-vet4")
    m = owner.post(f"/api/consultations/{cid}/messages", json={"body": "hello doctor"},
                   headers={"X-Actor-Id": "u-spoof"}).json()
    assert m["sender_id"] == "u-msg-owner4"
    recs = api.MESSAGE_REPO.deliveries_for(m["message_id"], tenant_id=T_A)
    assert [(r.recipient_id, r.channel, r.attempt_no, r.status) for r in recs] == [
        ("u-msg-vet4", "IN_APP", 1, "DELIVERED")]
    assert "hello doctor" in recs[0].rendered_body
    ev = [e for e in owner.get("/audit/events/tenant", params={"limit": 2000}).json()["events"]
          if e["event_name"] == "consultation.message.sent" and e["resource_id"] == m["message_id"]]
    assert ev and ev[0]["actor_id"] == "u-msg-owner4"
