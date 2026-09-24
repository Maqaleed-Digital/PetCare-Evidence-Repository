"""MVC-ACCEPT-AUTH-001 standing controls for the acceptance-authority candidate.

Everything these controls hold is CANDIDATE evidence. Nothing here ratifies the
V3.0 BRD, an FR -> REQ link, or an acceptance criterion; one control fails if
any output claims otherwise, and another fails if a criterion body appears that
is not a verbatim line of the inventoried source.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
AUTH = ROOT / "requirements" / "authority"
INVENTORY = AUTH / "req_inventory.json"
COMPARISON = AUTH / "v1_0_vs_v3_0.json"
CROSSWALK = AUTH / "fr_req_crosswalk_candidate.json"
REGISTER = ROOT / "requirements" / "register.yaml"

sys.path.insert(0, str(ROOT / "tools"))
import req_inventory  # noqa: E402

CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
FORBIDDEN = re.compile(r"\b(?:RATIFIED|ACCEPTED|CLIENT_ACCEPTED)\b")
ALLOWED_LABEL = "CANDIDATE_NOT_RATIFIED"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def _regen(tool):
    return subprocess.run([sys.executable, str(ROOT / "tools" / tool)], cwd=ROOT,
                          capture_output=True, text=True)


def test_req_inventory_is_current():
    r = _regen("req_inventory.py")
    assert r.returncode == 0, r.stderr
    assert r.stdout == INVENTORY.read_text(encoding="utf-8"), (
        "requirements/authority/req_inventory.json drifted from its tool or pinned sources")


def test_req_inventory_manifest_contains_authority_sources_only():
    """v1.2 (F-4/F-5): only requirement-authority instruments may be pinned.

    Uses the tool's OWN predicate, so the test and the tool cannot hold two
    classifications. The probes prove the predicate discriminates: it must
    refuse each prohibited class, or a green result here would mean nothing.
    """
    bad = {s["path"]: req_inventory.source_class(s["path"]) for s in req_inventory.MANIFEST
           if req_inventory.source_class(s["path"]) != "AUTHORITY"}
    assert not bad, bad
    assert sorted(s["path"] for s in req_inventory.MANIFEST) == sorted(req_inventory.SET_A)
    probes = {
        "petcare_api/main.py": "PRODUCT_RUNTIME",
        "petcare_runtime/src/petcare/uphr/service.py": "PRODUCT_RUNTIME",
        "petcare_web/app/pharmacy/page.tsx": "WEB_APP",
        "petcare-web/app/page.tsx": "WEB_APP",
        "petcare_runtime/migrations/0029_w0h_seller_identity.sql": "MIGRATION",
        "tests/governance/test_mvc_inventory.py": "TEST_FIXTURE",
        "petcare_api/tests/test_option_a_workflow.py": "TEST_FIXTURE",
        "petcare_web/__tests__/pharmacy-queue.test.tsx": "TEST_FIXTURE",
        "tools/req_inventory.py": "TOOL",
        "petcare_execution/tools/mvc_inventory.py": "TOOL",
        "requirements/bindings.json": "GENERATED_REQUIREMENTS",
        "requirements/authority/req_inventory.json": "GENERATED_REQUIREMENTS",
        "evidence/receipts/2026-09-24-mvc-accept-auth-001.md": "DERIVATIVE_EVIDENCE",
        req_inventory.AUTHORITY_ROOT + "x.json": "NON_DOCUMENT",
        req_inventory.SET_A[1]: "AUTHORITY",
    }
    for path, expected in probes.items():
        assert req_inventory.source_class(path) == expected, (path, req_inventory.source_class(path))


def test_register_comparison_is_current():
    r = _regen("compare_registers.py")
    assert r.returncode == 0, r.stderr
    assert r.stdout == COMPARISON.read_text(encoding="utf-8"), (
        "requirements/authority/v1_0_vs_v3_0.json drifted from the v1.0 register or V3.0 bytes")


def test_crosswalk_is_labelled_candidate():
    assert _load(CROSSWALK)["label"] == ALLOWED_LABEL


def test_crosswalk_covers_every_fr_and_cites_basis():
    cw = _load(CROSSWALK)
    inv = _load(INVENTORY)["req"]
    spine = re.findall(r"^  - id: (FR-\d{2})$", REGISTER.read_text(encoding="utf-8"), re.M)
    assert sorted(cw["fr"]) == sorted(spine) == [f"FR-{n:02d}" for n in range(1, 32)]
    for fr, entry in cw["fr"].items():
        for c in entry["candidates"]:
            assert c["req"] in inv, (fr, c["req"])
            assert c["confidence"] in CONFIDENCE, (fr, c)
            assert c["basis"] and all(re.match(r"^\S+:\d+ \S", b) for b in c["basis"]), (fr, c)
    mapped = {c["req"] for e in cw["fr"].values() for c in e["candidates"]}
    assert sorted(set(inv) - mapped) == cw["unmapped_req"]


def test_coverage_matches_inventory():
    cw = _load(CROSSWALK)
    inv = _load(INVENTORY)["req"]
    for fr, entry in cw["fr"].items():
        has = any(inv[c["req"]]["fails_if"] for c in entry["candidates"] if c["req"] in inv)
        expected = "HAS_CANDIDATE_CRITERIA" if has else "NO_CANDIDATE"
        assert entry["coverage"] == expected, (fr, entry["coverage"])


def test_no_ratification_or_authored_criteria():
    cw_text = CROSSWALK.read_text(encoding="utf-8")
    cw = json.loads(cw_text)
    assert not FORBIDDEN.search(cw_text.replace(ALLOWED_LABEL, "")), FORBIDDEN.findall(cw_text)
    comparison = COMPARISON.read_text(encoding="utf-8")
    assert not re.search(r'"(?:status|state|label)"\s*:\s*"(?:RATIFIED|ACCEPTED|CLIENT_ACCEPTED)"', comparison)
    # The crosswalk carries no criterion body: only req, confidence, basis.
    for e in cw["fr"].values():
        assert set(e) == {"candidates", "coverage"}
        for c in e["candidates"]:
            assert set(c) == {"req", "confidence", "basis"}, c
    # Every inventoried criterion is a verbatim line of its pinned source.
    lines = {}
    for req, body in _load(INVENTORY)["req"].items():
        for f in body["fails_if"]:
            src = lines.setdefault(f["path"], req_inventory.text_lines(ROOT / f["path"]))
            assert src[f["line"] - 1].strip() == f["text"], (req, f["path"], f["line"])
