"""AC-FR-06-01/02 under SQ-2 — video capability demonstrated NON_PROD through the SERVED app (MVC-BUILD-RUNNER-001 U27).

Authority: governance/sponsor_acts/MVC-SQ2-VIDEO-CAPABILITY-ACCEPTANCE-001.md (sha256 7b698f11…6219): AC-01/02 may be
satisfied in a controlled non-production/test environment with the feature switch enabled. The switch is turned on
HERE, in test configuration only (monkeypatch), and the REG-02 determination is substituted in-process as in
test_fr06_video.py (test setup, NOT counsel evidence — AC-FR-06-05 is untouched). AC-FR-06-03 remains the production
proof. No production activation.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import video as vid  # noqa: E402
from test_fr06_video import T_A, T_B, _book, _client, _open_gate  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.served_app
def test_ac_fr_06_01_a_booked_video_consultation_connects_both_parties_with_screen_sharing(monkeypatch):
    _open_gate(monkeypatch)
    vet = _client("u-sq2-vet", T_A, "veterinarian")
    owner = _client("u-sq2-owner", T_A, "owner")
    outsider = _client("u-sq2-vet-b", T_B, "veterinarian")
    assert owner.get("/api/consultations/remote/availability").json()["video_capability"] is True
    sid = _book(vet, "u-sq2-owner", "u-sq2-vet", "REMOTE_VIDEO")
    sig = f"/api/consultations/{sid}/video/signal"
    # Camera: offer (owner) -> answer (vet) -> ICE both ways.
    assert owner.post(sig, json={"kind": "OFFER", "payload": {"type": "offer", "sdp": "v=0 cam-o"}}).status_code == 200
    assert [(s["kind"], s["from"]) for s in vet.get(sig).json()] == [("OFFER", "u-sq2-owner")]
    assert vet.post(sig, json={"kind": "ANSWER", "payload": {"type": "answer", "sdp": "v=0 cam-a"}}).status_code == 200
    assert owner.post(sig, json={"kind": "ICE", "payload": {"candidate": "o"}}).status_code == 200
    assert vet.post(sig, json={"kind": "ICE", "payload": {"candidate": "v"}}).status_code == 200
    # In-session screen share: renegotiation offer (vet) -> answer (owner).
    assert vet.post(sig, json={"kind": "SCREEN_OFFER", "payload": {"type": "offer", "sdp": "screen"}}).status_code == 200
    assert owner.post(sig, json={"kind": "SCREEN_ANSWER", "payload": {"type": "answer", "sdp": "s"}}).status_code == 200
    assert [s["kind"] for s in owner.get(sig).json()] == ["ANSWER", "ICE", "SCREEN_OFFER"]
    assert [s["kind"] for s in vet.get(sig).json()] == ["OFFER", "ICE", "SCREEN_ANSWER"]
    assert outsider.get(sig).status_code == 404


@pytest.mark.served_app
def test_ac_fr_06_02_below_720p_needs_an_adaptive_bitrate_step_down_record(monkeypatch):
    _open_gate(monkeypatch)
    vet = _client("u-sq2-vet2", T_A, "veterinarian")
    _client("u-sq2-owner2", T_A, "owner")
    sid = _book(vet, "u-sq2-owner2", "u-sq2-vet2", "REMOTE_VIDEO")
    q = f"/api/consultations/{sid}/video/quality"
    assert vet.post(q, json={"frame_width": 1280, "frame_height": 720, "bitrate_kbps": 2500}).json()["compliant"] is True
    assert vet.post(q, json={"frame_width": 854, "frame_height": 480, "bitrate_kbps": 900,
                             "quality_limitation_reason": "bandwidth"}).json() == {
        "hd": False, "step_down": True, "compliant": True}
    assert vet.post(q, json={"frame_width": 854, "frame_height": 480, "bitrate_kbps": 900}).json()["compliant"] is False
    s = vet.get(q).json()
    assert (s["samples"], s["hd"], s["step_downs"], s["non_compliant"], s["min_height_hd"]) == (3, 1, 1, 1, 720)
    below = [e for e in vet.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
             if e["event_name"] == "consultation.video.below_hd" and e["resource_id"] == sid]
    assert [e["reason_code"] for e in below] == ["854x480:no-step-down"]


@pytest.mark.served_app
def test_the_video_path_is_refused_while_the_switch_is_off_even_with_the_gate_open(monkeypatch):
    _open_gate(monkeypatch)
    vet = _client("u-sq2-vet3", T_A, "veterinarian")
    _client("u-sq2-owner3", T_A, "owner")
    sid = _book(vet, "u-sq2-owner3", "u-sq2-vet3", "REMOTE_VIDEO")
    monkeypatch.delenv(vid.SWITCH_ENV)
    assert vet.get("/api/consultations/remote/availability").json()["video_capability"] is False
    for path, body in (("signal", {"kind": "OFFER", "payload": {}}),
                       ("quality", {"frame_width": 1280, "frame_height": 720, "bitrate_kbps": 1})):
        r = vet.post(f"/api/consultations/{sid}/video/{path}", json=body)
        assert r.status_code == 403 and r.json()["detail"]["error"] == "VIDEO_CAPABILITY_DISABLED", r.text


def _non_test_configurations() -> list:
    """Every tracked deployment / runtime configuration file (never a test file)."""
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    pat = re.compile(r"(^|/)(Dockerfile[^/]*|[^/]*\.env[^/]*|cloudbuild[^/]*\.ya?ml|docker-compose[^/]*\.ya?ml|"
                     r"compose[^/]*\.ya?ml|next\.config\.[mc]?[jt]s|\.github/workflows/[^/]+\.ya?ml|[^/]*\.tf|"
                     r"[^/]*\.tfvars|app\.ya?ml|Procfile)$")
    return [n for n in names if pat.search(n) and "/tests/" not in n and "__tests__" not in n
            and not n.startswith("tests/")]


def test_the_video_switch_defaults_off_in_every_non_test_configuration(monkeypatch):
    monkeypatch.delenv(vid.SWITCH_ENV, raising=False)
    assert vid.SWITCH_DEFAULT is False
    assert vid.capability_enabled({}) is False and vid.capability_enabled(dict(os.environ)) is False
    assert vid.capability_enabled({vid.SWITCH_ENV: ""}) is False
    assert vid.capability_enabled({vid.SWITCH_ENV: "yes-please"}) is False      # only an explicit true/1 is ON
    assert vid.capability_enabled({vid.SWITCH_ENV: "true"}) is True
    configs = _non_test_configurations()
    assert len(configs) >= 5, configs                                         # the sweep actually found files
    on = re.compile(re.escape(vid.SWITCH_ENV) + r"""["']?\s*[:=]\s*["']?(true|1)\b""", re.I)
    offenders = [c for c in configs if on.search((ROOT / c).read_text(encoding="utf-8", errors="replace"))]
    assert offenders == []
    # The root conftest (the shared test configuration) does not turn it on globally either.
    assert vid.SWITCH_ENV not in (ROOT / "conftest.py").read_text(encoding="utf-8")
