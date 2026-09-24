"""MVC-ACCEPT-PACK-P1 v1.2 standing controls: ratified pack integrity.

The ratified pack records acceptance AUTHORITY only. It asserts no
implementation evidence and moves no requirement to ACCEPTED; the last control
fails if either is ever claimed.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
ACC = ROOT / "requirements" / "acceptance"
DISPOSITIONS = {"ACCEPT", "ACCEPT_WITH_CLARIFICATION", "ACCEPT_WITH_LIMIT",
                "ACCEPT_WITH_SCOPE", "ACCEPT_WITH_THRESHOLD"}
FROZEN_FIELDS = ("id", "statement", "fails_if", "evidence", "sources", "dependency")


def _j(name):
    return json.loads((ACC / name).read_text(encoding="utf-8"))


def _criteria(pack):
    return {c["id"]: c for e in pack["fr"].values() for c in e["criteria"]}


def test_ratified_pack_is_bound_to_sponsor_act():
    pack = _j("phase1_high_pack.ratified.json")
    r = pack["ratification"]
    assert pack["label"] == "RATIFIED"
    assert r["decision"] == "MVC-ACCEPT-PACK-P1"
    act = ROOT / r["sponsor_act_path"]
    assert act.is_file(), r["sponsor_act_path"]
    assert hashlib.sha256(act.read_bytes()).hexdigest() == r["sponsor_act_sha256"]


def test_ratification_did_not_alter_criteria_text():
    d = _j("phase1_high_pack.draft.json")["fr"]
    r = _j("phase1_high_pack.ratified.json")["fr"]
    assert set(d) == set(r)
    for fr in d:
        dc = {c["id"]: c for c in d[fr]["criteria"]}
        rc = {c["id"]: c for c in r[fr]["criteria"]}
        assert set(dc) == set(rc), fr
        for cid in dc:
            for f in FROZEN_FIELDS:
                assert dc[cid][f] == rc[cid][f], (cid, f)


def test_every_criterion_has_a_disposition():
    for fr, e in _j("phase1_high_pack.ratified.json")["fr"].items():
        for c in e["criteria"]:
            assert c.get("disposition") in DISPOSITIONS, c["id"]
            assert isinstance(c["parameters"], dict), c["id"]
            assert isinstance(c["ratified_text"], str), c["id"]
            if c["disposition"] != "ACCEPT":
                assert c["ratified_text"].strip(), c["id"]


def test_all_68_criteria_present_and_known_failing_recorded():
    pack = _j("phase1_high_pack.ratified.json")
    assert len(pack["fr"]) == 16
    assert len(_criteria(pack)) == 68
    assert pack["known_failing"] == ["AC-FR-02-04"]


def test_relevant_nfrs_have_a_disposition():
    nfr = _j("phase1_high_pack.ratified.json")["nfr"]
    assert len(nfr) == 15
    assert sum(1 for e in nfr.values() if e["phase1_relevant"]) == 13
    for n, e in nfr.items():
        if e["phase1_relevant"]:
            assert e.get("disposition") in DISPOSITIONS, n
    assert nfr["NFR-13"]["phase1_relevant"] is False
    assert nfr["NFR-14"]["phase1_relevant"] is False


def test_sponsor_parameters_are_preserved():
    pack = _j("phase1_high_pack.ratified.json")
    c = _criteria(pack)
    for cid in ("AC-FR-13-01", "AC-FR-27-01"):
        assert c[cid]["disposition"] == "ACCEPT_WITH_THRESHOLD", cid
        assert c[cid]["parameters"].get("REAL_TIME_BOUND") == "5_SECONDS", cid
        assert "p95 <= 5 seconds" in c[cid]["ratified_text"], cid
        assert "at least 100 events" in c[cid]["ratified_text"], cid
    r23 = c["AC-FR-23-01"]
    assert r23["disposition"] == "ACCEPT_WITH_THRESHOLD"
    assert r23["parameters"].get("REMINDER_DEFAULT") == "7_DAYS_BEFORE_DUE"
    assert r23["parameters"].get("SECOND_REMINDER") == "24_HOURS_BEFORE_DUE_IF_OUTSTANDING"
    n09 = pack["nfr"]["NFR-09"]
    assert n09["disposition"] == "ACCEPT_WITH_THRESHOLD"
    assert "Saudi_PDPL" in n09["parameters"].get("STANDARD", "")
    assert n09["parameters"].get("PASS") == "100_PERCENT_APPLICABLE_CONTROLS_EVIDENCED"
    assert n09["parameters"].get("UNRESOLVED_CRITICAL_FINDINGS") == "0"
    assert n09["parameters"].get("UNRESOLVED_HIGH_FINDINGS") == "0"
    assert n09["parameters"].get("DEPENDENCY") == "COUNSEL:PDPL_COMPLIANCE_MATRIX"
    n15 = pack["nfr"]["NFR-15"]
    assert n15["disposition"] == "ACCEPT_WITH_THRESHOLD"
    assert n15["parameters"].get("AUTHENTICATED_DEFAULT") == "100_REQUESTS_PER_MINUTE_PER_PRINCIPAL"
    assert n15["parameters"].get("ANONYMOUS_DEFAULT") == "30_REQUESTS_PER_MINUTE_PER_CLIENT_IP"
    assert n15["parameters"].get("EXCESS_RESPONSE") == "HTTP_429"


def test_ratification_is_not_acceptance():
    status = json.loads((ROOT / "requirements" / "status.json").read_text(encoding="utf-8"))
    claimed = [r["id"] for r in status["requirements"]
               if r["status"] in ("ACCEPTED", "CLIENT_ACCEPTED")
               or r["acceptance_state"] in ("ACCEPTED", "CLIENT_ACCEPTED")]
    assert not claimed, claimed
    pack = _j("phase1_high_pack.ratified.json")
    for fr, e in pack["fr"].items():
        assert "status" not in e and "acceptance_state" not in e, fr
        for c in e["criteria"]:
            assert "evidence_result" not in c and "status" not in c, c["id"]
    assert set(pack["ratification"]) == {"decision", "date", "sponsor_act_path", "sponsor_act_sha256"}
