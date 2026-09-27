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


# ---------------------------------------------------------------- default-off proof (v1.3 U29 hardening)
# CONFIGURATION AUTHORITY: the switch has exactly one reader, `video.capability_enabled(env)`, which the served app calls
# with the PROCESS ENVIRONMENT (main.py). Nothing else resolves it — no settings file, no registry of sources. So a
# repository-defined profile is any tracked file that can put the variable into a process environment, whatever its
# name or format (Dockerfile ENV, CLI --set-env-vars, .env, YAML/JSON/k8s env blocks, shell exports, source code).
# The proof is therefore: (1) the loader itself resolves OFF for the default runtime profile (a fresh interpreter) and
# for every profile a tracked file defines; (2) discovery covers EVERY tracked file, not a list of filename patterns.
# Excluded, by rule and not by name: test code (it may switch the capability on for itself), the module that DEFINES the
# switch, and record trees that no deployment loads (evidence/, requirements/, governance/).
_RECORD_ROOTS = ("evidence/", "requirements/", "governance/")
_ASSIGN = (re.compile(r"""^["']?\s*[:=]\s*["']?([^"'\s,;}\]]*)"""),            # KEY=v, KEY: v, "KEY": "v", --x=KEY=v
           re.compile(r"""^["']?[ \t]+["']?([^"'\s,;}\]]+)"""),                # Dockerfile `ENV KEY v`
           re.compile(r"""^["']?\s*\n\s*value:\s*["']?([^"'\s]*)"""))        # k8s `- name: KEY` / `value: v`


def _is_test_path(path: str) -> bool:
    parts = path.split("/")
    return "tests" in parts or "__tests__" in parts or parts[-1].startswith("test_") or ".test." in parts[-1]


def _scanned_sources() -> list:
    names = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.decode().split("\0")
    definer = Path(vid.__file__).resolve().relative_to(ROOT).as_posix()
    return [n for n in names if n and not _is_test_path(n) and n != definer and not n.startswith(_RECORD_ROOTS)]


def _mentions(text: str, name: str) -> list:
    """Every mention of `name` in `text` with the value it assigns there, or None when no value can be read."""
    out = []
    for m in re.finditer(re.escape(name) + r"(?![A-Z0-9_])", text):
        rest = text[m.end():m.end() + 200]
        value = next((a.match(rest).group(1) for a in _ASSIGN if a.match(rest)), None)
        out.append(value)
    return out


def _profile(text: str) -> dict:
    """The PETCARE_* environment a tracked source defines (its non-test profile), as the loader would receive it."""
    env = {}
    for key in set(re.findall(r"PETCARE_[A-Z0-9_]+", text)):
        vals = [v for v in _mentions(text, key) if v is not None]
        if vals:
            env[key] = vals[-1]
    return env


def test_the_video_switch_defaults_off_in_every_non_test_configuration(monkeypatch):
    monkeypatch.delenv(vid.SWITCH_ENV, raising=False)
    assert vid.SWITCH_DEFAULT is False
    assert vid.capability_enabled({}) is False and vid.capability_enabled({vid.SWITCH_ENV: ""}) is False
    assert vid.capability_enabled({vid.SWITCH_ENV: "yes-please"}) is False      # only an explicit true/1 is ON
    assert vid.capability_enabled({vid.SWITCH_ENV: "true"}) is True
    # (1a) the default runtime profile: a fresh interpreter, no test configuration loaded, resolves OFF.
    env = {k: v for k, v in os.environ.items() if k != vid.SWITCH_ENV}
    env["PYTHONPATH"] = str(ROOT / "petcare_api")
    out = subprocess.run([sys.executable, "-c", "import os, video; print(video.capability_enabled(os.environ))"],
                         cwd=ROOT / "petcare_api", env=env, capture_output=True, text=True, timeout=60)
    assert out.stdout.strip() == "False", out.stderr[-1000:]
    # (1b)+(2) every profile any tracked source defines resolves OFF through the loader; every mention is readable.
    sources = _scanned_sources()
    assert len(sources) > 1000, len(sources)                                  # the sweep is the whole tracked tree
    profiles = offenders = 0
    unreadable = []
    for path in sources:
        try:
            text = (ROOT / path).read_bytes().decode("utf-8")
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            continue
        profile = _profile(text)
        profiles += bool(profile)
        if vid.capability_enabled(profile):
            offenders += 1
            unreadable.append((path, "resolves ON"))
        unreadable += [(path, "mention without a readable value") for v in _mentions(text, vid.SWITCH_ENV) if v is None]
    assert unreadable == [] and offenders == 0
    assert profiles >= 5                                                      # real profiles were resolved
    assert vid.SWITCH_ENV not in (ROOT / "conftest.py").read_text(encoding="utf-8")
