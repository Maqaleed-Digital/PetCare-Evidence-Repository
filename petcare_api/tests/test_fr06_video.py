"""FR-06 video consultation capability behind the REG-02 gate — through the SERVED app (MVC-BUILD-RUNNER-001 U22).

The REG-02 determination has no served write path; to exercise the capability the determination list is substituted
IN-PROCESS (test setup, not counsel evidence — as in test_fr06_consultation.py). AC-FR-06-01/02 are NOT registered:
SPONSOR_QUEUE SQ-2 decides how they are accepted, and a real media path (two browsers, TURN) is not proven here.
"""
import os
import sys
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import consultations as consult  # noqa: E402
import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr06v-alpha", "t-fr06v-beta"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr06v.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr06v.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _open_gate(monkeypatch):
    monkeypatch.setattr(api.CONSULTATION_REPO, "_determinations", [consult.RegulatoryDetermination(
        "d-v", consult.REG02_TELEMEDICINE, consult.LAWFUL, "video, licensed vet", "test setup", "counsel",
        datetime.now(timezone.utc))])


def _book(vet, owner_id, vet_id, mode):
    r = vet.post("/api/consultations", json={"pet_id": "p", "owner_id": owner_id, "veterinarian_id": vet_id, "mode": mode})
    assert r.status_code == 200, r.text
    return r.json()["session_id"]


def test_the_video_path_is_closed_while_remote_consultation_is_not_offered():
    vet = _client("u-v-vet0", T_A, "veterinarian")
    _client("u-v-owner0", T_A, "owner")
    sid = _book(vet, "u-v-owner0", "u-v-vet0", "IN_PERSON")
    r = vet.post(f"/api/consultations/{sid}/video/signal", json={"kind": "OFFER", "payload": {"sdp": "x"}})
    assert r.status_code == 403 and r.json()["detail"]["error"] == "REMOTE_CONSULTATION_NOT_OFFERED"


def test_both_participants_exchange_the_session_and_the_screen_share_renegotiation(monkeypatch):
    _open_gate(monkeypatch)
    vet = _client("u-v-vet", T_A, "veterinarian")
    owner = _client("u-v-owner", T_A, "owner")
    stranger = _client("u-v-vet-x", T_A, "veterinarian")
    other = _client("u-v-vet-b", T_B, "veterinarian")
    sid = _book(vet, "u-v-owner", "u-v-vet", "REMOTE_VIDEO")
    base = f"/api/consultations/{sid}/video/signal"
    assert owner.post(base, json={"kind": "OFFER", "payload": {"type": "offer", "sdp": "v=0 owner"}}).status_code == 200
    got = vet.get(base).json()
    assert [(s["kind"], s["from"], s["payload"]["sdp"]) for s in got] == [("OFFER", "u-v-owner", "v=0 owner")]
    assert vet.post(base, json={"kind": "ANSWER", "payload": {"type": "answer", "sdp": "v=0 vet"}}).status_code == 200
    for who in (owner, vet):
        who.post(base, json={"kind": "ICE", "payload": {"candidate": "c", "sdpMid": "0"}})
    assert owner.post(base, json={"kind": "SCREEN_OFFER", "payload": {"type": "offer", "sdp": "screen"}}).status_code == 200
    seen_by_vet = [s["kind"] for s in vet.get(base, params={"after": got[-1]["seq"]}).json()]
    assert seen_by_vet == ["ICE", "SCREEN_OFFER"]
    assert [s["kind"] for s in owner.get(base).json()] == ["ANSWER", "ICE"]          # never its own messages
    assert owner.post(base, json={"kind": "BOGUS", "payload": {}}).status_code == 400
    assert stranger.get(base).status_code == 404 and other.get(base).status_code == 404
    in_person = _book(vet, "u-v-owner", "u-v-vet", "IN_PERSON")
    assert vet.post(f"/api/consultations/{in_person}/video/signal",
                    json={"kind": "OFFER", "payload": {}}).status_code == 409


def test_quality_below_720p_is_compliant_only_with_an_adaptive_bitrate_step_down(monkeypatch):
    _open_gate(monkeypatch)
    vet = _client("u-v-vet2", T_A, "veterinarian")
    _client("u-v-owner2", T_A, "owner")
    sid = _book(vet, "u-v-owner2", "u-v-vet2", "REMOTE_VIDEO")
    q = f"/api/consultations/{sid}/video/quality"
    assert vet.post(q, json={"frame_width": 1280, "frame_height": 720, "bitrate_kbps": 2500}).json() == {
        "hd": True, "step_down": False, "compliant": True}
    assert vet.post(q, json={"frame_width": 640, "frame_height": 360, "bitrate_kbps": 600,
                             "quality_limitation_reason": "bandwidth"}).json() == {"hd": False, "step_down": True,
                                                                                 "compliant": True}
    bad = vet.post(q, json={"frame_width": 640, "frame_height": 360, "bitrate_kbps": 600}).json()
    assert bad["compliant"] is False
    summary = vet.get(q).json()
    assert (summary["samples"], summary["hd"], summary["step_downs"], summary["non_compliant"]) == (3, 1, 1, 1)
    audited = [e for e in vet.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
               if e["event_name"] == "consultation.video.below_hd" and e["resource_id"] == sid]
    assert len(audited) == 1 and audited[0]["reason_code"] == "640x360:no-step-down"
