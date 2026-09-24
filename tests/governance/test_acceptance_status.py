"""MVC-ACCEPT-CHECK-001 standing controls: ACCEPTED only from complete ratified-criterion evidence.

These controls read the committed outputs (status.json, evidence.json, the
ratified pack) and recompute the acceptance rule independently of the checker,
so a checker that emits ACCEPTED on incomplete evidence, or a hand-edited
status.json that claims it, fails here.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
ACC = ROOT / "requirements" / "acceptance"
STATUS = ROOT / "requirements" / "status.json"
EVIDENCE_TYPES = {"SERVED_APP_E2E", "PERSISTENCE", "TENANT_ISOLATION", "AUDIT", "ARABIC_RTL", "UI",
                  "DEPENDENCY", "NFR_EVIDENCE"}
EVIDENCE_KINDS = {"TEST", "ARTEFACT"}


def _j(p):
    return json.loads(p.read_text(encoding="utf-8"))


def _pack():
    return _j(ACC / "phase1_high_pack.ratified.json")


def _evidence():
    return _j(ACC / "evidence.json")


def _status():
    return _j(STATUS)


def _need(c):
    return set(c["evidence"]) | ({"DEPENDENCY"} if c["dependency"] != "NONE" else set())


def test_evidence_registry_is_well_formed():
    pack = _pack()
    keys = {c["id"] for e in pack["fr"].values() for c in e["criteria"]} | set(pack["nfr"])
    for key, items in _evidence().items():
        assert key in keys, key
        assert isinstance(items, list) and items, key
        for it in items:
            assert it["type"] in EVIDENCE_TYPES, (key, it)
            assert it["kind"] in EVIDENCE_KINDS, (key, it)
            assert isinstance(it["ref"], str) and it["ref"], (key, it)
            if it["kind"] == "ARTEFACT":
                f = ROOT / it["ref"]
                assert f.is_file(), (key, it["ref"])
                assert hashlib.sha256(f.read_bytes()).hexdigest() == it["sha256"], (key, it["ref"])


def test_accepted_only_for_ratified_frs():
    ratified = set(_pack()["fr"])
    for r in _status()["requirements"]:
        if r["id"] not in ratified:
            assert r["acceptance_state"] == "CRITERIA_NOT_RATIFIED", r["id"]
            assert r["status"] != "ACCEPTED", r["id"]


def test_accepted_requires_complete_evidence():
    pack, ev = _pack(), _evidence()
    for r in _status()["requirements"]:
        if r["status"] != "ACCEPTED" and r["acceptance_state"] != "ACCEPTED":
            continue
        assert r["id"] in pack["fr"], r["id"]
        assert r["engineering_status"] == "REACHABLE_TESTED", r["id"]
        for c in pack["fr"][r["id"]]["criteria"]:
            registered = {it["type"] for it in ev.get(c["id"], [])}
            missing = _need(c) - registered
            assert not missing, (r["id"], c["id"], sorted(missing))
            assert not r["criteria_gaps"].get(c["id"]), (r["id"], c["id"])


def test_nfr_states_follow_relevance():
    pack = _pack()
    states = _status()["nfr"]
    assert set(states) == set(pack["nfr"])
    for n, e in pack["nfr"].items():
        if not e["phase1_relevant"]:
            assert states[n]["state"] == "NOT_PHASE1_RELEVANT", n
        else:
            assert states[n]["state"] in {"EVIDENCED", "EVIDENCE_INCOMPLETE"}, n
            if states[n]["state"] == "EVIDENCED":
                assert any(it["type"] == "NFR_EVIDENCE" for it in _evidence().get(n, [])), n


def test_empty_evidence_registry_yields_no_acceptance():
    if _evidence():
        return
    accepted = [r["id"] for r in _status()["requirements"]
                if r["status"] == "ACCEPTED" or r["acceptance_state"] == "ACCEPTED"]
    assert not accepted, accepted
    assert not [n for n, v in _status()["nfr"].items() if v["state"] == "EVIDENCED"]


def test_no_client_acceptance_is_emitted():
    text = STATUS.read_text(encoding="utf-8")
    assert "CLIENT_ACCEPTED" not in text.replace("CLIENT_ACCEPTED is never emitted", "")
