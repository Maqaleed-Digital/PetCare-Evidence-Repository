"""MVC-ACCEPT-PACK-P1 standing controls: DRAFT Phase-1 High acceptance pack."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
ACC = ROOT / "requirements" / "acceptance"
EVIDENCE = {"SERVED_APP_E2E", "PERSISTENCE", "TENANT_ISOLATION", "AUDIT", "ARABIC_RTL", "UI"}
DEP = re.compile(r"^(NONE|PRODUCTION|EXTERNAL:.+|COUNSEL:.+)$")
AC = re.compile(r"^AC-(FR-\d{2})-\d{2}$")


def _pack():
    return json.loads((ACC / "phase1_high_pack.draft.json").read_text(encoding="utf-8"))


def _spine():
    return (ROOT / "requirements" / "register.yaml").read_text(encoding="utf-8")


def test_pack_is_draft():
    assert _pack()["label"] == "DRAFT_NOT_RATIFIED"


def test_pack_bound_to_denominator():
    sha = re.search(r"^  sha256: (\S+)$", _spine(), re.M).group(1)
    assert _pack()["denominator"]["brd_sha256"] == sha


def test_pack_covers_exactly_phase1_high():
    listed = re.search(r"^  phase1_high_ids: \[(.*)\]$", _spine(), re.M).group(1)
    expected = {s.strip() for s in listed.split(",") if s.strip()}
    assert len(expected) == 16
    assert set(_pack()["fr"]) == expected


def test_every_criterion_is_well_formed():
    seen = set()
    for fr, e in _pack()["fr"].items():
        assert e["criteria"], fr
        for c in e["criteria"]:
            m = AC.match(c["id"])
            assert m and m.group(1) == fr, c["id"]
            assert c["id"] not in seen, c["id"]
            seen.add(c["id"])
            assert c["statement"].strip() and c["fails_if"].strip(), c["id"]
            assert c["evidence"] and set(c["evidence"]) <= EVIDENCE, c["id"]
            assert c["sources"], c["id"]
            assert DEP.match(c["dependency"]), c["id"]


def test_req_sources_are_ratified_candidate_mappings():
    cw = json.loads((ROOT / "requirements" / "authority" / "fr_req_crosswalk_candidate.json")
                    .read_text(encoding="utf-8"))
    for fr, e in _pack()["fr"].items():
        allowed = {c["req"] for c in cw["fr"][fr]["candidates"]}
        for c in e["criteria"]:
            for s in c["sources"]:
                if s["kind"] == "REQ":
                    assert s["ref"] in allowed, (c["id"], s["ref"])
                if s["kind"] == "BRD":
                    assert s["ref"] == fr, (c["id"], s["ref"])


def test_customer_facing_requirements_carry_ui_evidence():
    for fr, e in _pack()["fr"].items():
        if e["customer_facing"]:
            assert any("UI" in c["evidence"] for c in e["criteria"]), fr


def test_all_nfrs_present_and_relevant_ones_defined():
    nfr = _pack()["nfr"]
    assert set(nfr) == set(re.findall(r"^  - id: (NFR-\d{2})$", _spine(), re.M))
    for n, e in nfr.items():
        assert e["rationale"].strip(), n
        if e["phase1_relevant"]:
            d = e["evidence_definition"]
            for k in ("metric", "method", "threshold", "environment", "dependency"):
                assert str(d[k]).strip(), (n, k)
            assert d["environment"] in {"NON_PROD", "PRODUCTION"}, n


def test_review_document_is_current():
    out = subprocess.run([sys.executable, "tools/render_acceptance_pack.py"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    assert out == (ACC / "phase1_high_pack.draft.md").read_text(encoding="utf-8")
