"""Known-answer controls for the requirement-identifier inventory.

Every control exists because a specific defect was observed — three in the
historic run that produced the withdrawn `495`, and three more in this parser
while it was being written. A control whose defect was never real is
decoration; each of these fails on a fixture that reproduces its defect.

The governing rule: the parser reports what it finds. Nothing is tuned toward
500 or 499.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "petcare_execution" / "tools"))

from mvc_inventory import (  # noqa: E402
    CONTINUATION, ELISION, NAMESPACE_REF, build, classify, load, scan,
)

LINEAGE = ROOT / "petcare_execution" / "AUTHORITY" / "MVC-LINEAGE"
SOURCES = LINEAGE / "sources"
INVENTORY = LINEAGE / "inventory.json"

ANNEX_K = SOURCES / "MVC-SPEC-001_V3_1_Annex_K_Split_Taxpayer_Requirements.md"
V31 = SOURCES / "MVC-BRD-001_V3_1_CANDIDATE_MyVetiCare_Master_BRD.docx"
V32 = SOURCES / "MVC-BRD-001_V3_2_EXECUTION_BASELINE_CANDIDATE.md"
CLOSE_V11 = SOURCES / "MVC-CLOSE-001_V1_1_PhaseA_Execution_Boundary.docx"


def _inv() -> dict:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def _build_from_text(text: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "fixture.md"
        p.write_text(text, encoding="utf-8")
        return build([p])


# ---------------------------------------------------------------------------
# Custody
# ---------------------------------------------------------------------------

def test_the_declared_source_set_is_in_custody():
    manifest = json.loads((LINEAGE / "SOURCE_CUSTODY_MANIFEST.json").read_text(encoding="utf-8"))
    assert len(manifest["documents"]) == 6
    for entry in manifest["documents"]:
        assert (ROOT / entry["repository_path"]).is_file(), entry["repository_path"]
        assert entry["source_sha256"] == entry["repository_sha256"], (
            f"custody copy not byte-identical: {entry['document_id']}"
        )
        assert entry["ratified"] is False, "custody is not ratification"


def test_the_inventory_matches_the_sources_it_was_generated_from():
    for src in _inv()["generated_from"]:
        path = SOURCES / src["document"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == src["sha256"], (
            f"{src['document']} changed since the inventory was generated"
        )


def test_no_identifier_exists_that_no_document_produced():
    """The one rule, asserted."""
    inv = _inv()
    seen = set().union(*(set(v) for v in inv["per_doc"].values()))
    orphans = sorted(set(inv["union"]) - seen)
    assert orphans == [], f"union members no document produced: {orphans}"


# ---------------------------------------------------------------------------
# CONTROL A — Annex K, the one fully enumerated scope
# ---------------------------------------------------------------------------

def test_control_a_annex_k():
    inv = build([ANNEX_K])
    assert inv["counts"]["union"] == 11, inv["union"]
    assert inv["elisions_detected"] == [], "Annex K must contain no elision"
    assert {"REQ-UX-NTI-1", "REQ-UX-NTI-2", "REQ-UX-NTI-3"} <= set(inv["union"])
    assert set(inv["malformed_candidates"]) == {"REQ-FIN", "REQ-UX"}


# ---------------------------------------------------------------------------
# CONTROL B — the three historic defects
# ---------------------------------------------------------------------------

def test_control_b_defect_1_three_segment_ids_do_not_collapse():
    """D-A: the withdrawn two-segment regex truncated `REQ-UX-NTI-1`."""
    import re
    text = "REQ-UX-NTI-1 and REQ-UX-NTI-2 and REQ-UX-NTI-3 are distinct."
    defective = re.compile(r"\bREQ-[A-Z0-9]+-[A-Za-z0-9]+")
    assert set(defective.findall(text)) == {"REQ-UX-NTI"}, "defect fixture no longer reproduces"
    _, total, _ = scan(text)
    assert set(total) == {"REQ-UX-NTI-1", "REQ-UX-NTI-2", "REQ-UX-NTI-3"}


def test_control_b_defect_2_close_v11_present_and_load_bearing():
    """D-B: `MVC-CLOSE-001 V1.1` absent lost REQ-SAF-F2/F3."""
    assert CLOSE_V11.is_file()
    assert {"REQ-SAF-F2", "REQ-SAF-F3"} <= set(_inv()["union"])


def test_control_b_defect_3_v32_present_and_load_bearing():
    """D-C: `MVC-BRD-001 V3.2` absent lost REQ-DISP-AUTH-FAILCLOSED."""
    assert V32.is_file()
    assert "REQ-DISP-AUTH-FAILCLOSED" in set(_inv()["union"])


def test_the_495_era_corpus_reproduces_both_source_set_defects():
    """Asserting a document's presence proves nothing unless removing it
    demonstrably loses identifiers — so the 495-era corpus is reconstructed.

    A subtlety worth recording, because the naive form of this test FAILS.
    `REQ-SAF-F2/F3` now appear in **two** documents: `MVC-CLOSE-001 V1.1`,
    which originated them, and `MVC-BRD-001 V3.2`, which was authored *after*
    the 495 run and picked them up. Dropping CLOSE V1.1 from today's corpus
    therefore loses nothing.

    That does not falsify D-B; it dates it. The defect was real against the
    corpus that existed then — V3.1 plus Annex K, with neither CLOSE V1.1 nor
    V3.2 — and that is the corpus reconstructed here.
    """
    era_495 = set(build([V31, ANNEX_K])["union"])
    assert not ({"REQ-SAF-F2", "REQ-SAF-F3"} & era_495), (
        "the 495-era corpus already contains the identifiers D-B says it lost"
    )
    assert "REQ-DISP-AUTH-FAILCLOSED" not in era_495

    # D-B: adding CLOSE V1.1 to that corpus recovers them.
    assert {"REQ-SAF-F2", "REQ-SAF-F3"} <= set(build([V31, ANNEX_K, CLOSE_V11])["union"])
    # D-C: adding V3.2 recovers the fail-closed invariant, and only V3.2 carries it.
    assert "REQ-DISP-AUTH-FAILCLOSED" in set(build([V31, ANNEX_K, V32])["union"])

    full = set(build([V31, V32, CLOSE_V11, ANNEX_K])["union"])
    assert {"REQ-SAF-F2", "REQ-SAF-F3", "REQ-DISP-AUTH-FAILCLOSED"} <= full


# ---------------------------------------------------------------------------
# CONTROL C — elision must never be expanded
# ---------------------------------------------------------------------------

def test_control_c_elision_detected_and_never_generated():
    text = "| §5 | Surfaces | REQ-MVC-4.1, REQ-MVC-4.10, … (+114) | 120 |"
    assert ELISION.search(text), "elision fixture no longer reproduces"
    _, total, _ = scan(text)
    assert set(total) == {"REQ-MVC-4.1", "REQ-MVC-4.10"}, "parser invented elided members"


def test_control_c_the_corpus_carries_appendix_t_elisions():
    inv = _inv()
    assert len(inv["elisions_detected"]) == 33
    assert sum(e["hidden_count"] for e in inv["elisions_detected"]) > 1000


# ---------------------------------------------------------------------------
# CONTROL D — metavariable and prose suffix
# ---------------------------------------------------------------------------

def test_control_d_metavariable_is_found_before_it_is_excluded():
    """It must be FOUND first.

    An earlier grammar refused lowercase segments, so `REQ-MVC-n` tokenised as
    `REQ-MVC`: the metavariable was never seen, its exclusion was vacuous, and
    `REQ-MVC` entered the union as a phantom.
    """
    _, total, _ = scan("Identifiers are re-keyed to REQ-MVC-n throughout.")
    assert "REQ-MVC-n" in total, "the metavariable was not tokenised at all"
    assert classify("REQ-MVC-n") == "metavariable"
    inv = _inv()
    assert "REQ-MVC-n" not in inv["union"]
    assert "REQ-MVC-n" in [e["id"] for e in inv["excluded"]]
    assert "REQ-MVC" not in inv["union"], "metavariable truncated into a phantom"


def test_control_d_prose_suffix_excluded_but_the_real_id_survives():
    assert classify("REQ-UX-4-conformant") == "prose_suffix"
    inv = _inv()
    assert "REQ-UX-4-conformant" in [e["id"] for e in inv["excluded"]]
    assert "REQ-UX-4" in inv["union"]


def test_a_prefix_with_a_longer_sibling_survives_when_it_stands_alone():
    """`REQ-UX-4` has longer siblings and is real. A rule dropping every prefix
    would delete it; standalone occurrence is the discriminator."""
    inv = _build_from_text("REQ-UX-4 is ratified. See also REQ-UX-4-conformant surfaces.")
    assert "REQ-UX-4" in inv["union"]


# ---------------------------------------------------------------------------
# CONTROL E — REQ-MVC-1 prose evidence
# ---------------------------------------------------------------------------

def test_control_e_req_mvc_1_is_contested_so_it_is_not_excluded():
    """The 500 → 499 step rests on `REQ-MVC-1` being prose. The evidence is
    real but not unanimous, so this parser does not exclude it.

    `MVC-ACCEPTANCE-ANNEX-001` finds it occurs only as "the REQ-MVC-1
    precedent", and V3.1 confirms that phrasing. But `MVC-BRD-001 V3.2`
    Appendix T lists `REQ-MVC-1` as a traced identifier of §1. Two governed
    documents disagree. Excluding it would bake one side of an unresolved
    question into a measurement — and would move the number toward the historic
    figure, which is exactly the tuning this lane forbids.
    """
    inv = _inv()
    assert "REQ-MVC-1" in inv["union"], "REQ-MVC-1 excluded without a settled ruling"
    assert "REQ-MVC-1" not in [e["id"] for e in inv["excluded"]]
    assert "REQ-MVC-1 precedent" in load(V31), "prose evidence no longer reproduces"
    assert "REQ-MVC-1," in load(V32), "V3.2 no longer lists REQ-MVC-1 as an identifier"


# ---------------------------------------------------------------------------
# The measurement — recorded, never tuned
# ---------------------------------------------------------------------------

def test_the_measured_universe_is_pinned_as_measured():
    """511, not 500.

    Not a claim that 500 was wrong. A claim that THIS declared source set
    yields 511, and that 500 is not reproducible from the documents in custody.
    """
    inv = _inv()
    assert inv["counts"]["union"] == 511
    assert inv["counts"]["phantoms_removed"] == 3
    assert inv["counts"]["excluded"] == 2


def test_the_full_spec_v31_is_absent_which_is_why_500_is_unreachable():
    """V3.2 Appendix T derives its set from "the SPEC V3.1 / GAP V1.7
    namespaces". No full SPEC V3.1 exists in custody — only its Annex K."""
    candidates = sorted(SOURCES.glob("MVC-SPEC-001_V3_1*"))
    assert len(candidates) == 1
    assert "Annex_K" in candidates[0].name, (
        "a full SPEC V3.1 has appeared — re-run the reconstruction and revisit "
        "the denominator"
    )


def test_the_parser_is_deterministic():
    a, b = build([ANNEX_K, V32]), build([ANNEX_K, V32])
    assert a["union"] == b["union"] and a["counts"] == b["counts"]


def test_an_unreadable_source_aborts_rather_than_shrinking_the_corpus():
    """D-1 historically: `load()` swallowed exceptions, three of six documents
    vanished, and the tool produced a believable 18.4%."""
    with pytest.raises(SystemExit):
        build([SOURCES / "this-document-does-not-exist.md"])


def test_the_lookahead_matchers_discriminate():
    assert NAMESPACE_REF.match("-*")
    assert NAMESPACE_REF.match("-{3,4}")
    assert NAMESPACE_REF.match("-` namespace")
    assert not NAMESPACE_REF.match("-1")
    assert CONTINUATION.match("-NTI")
    assert CONTINUATION.match("-1")
    assert not CONTINUATION.match("-conformant")
    assert not CONTINUATION.match(" is ratified")


def test_dotted_alphabetic_families_are_not_truncated():
    """Found in THIS parser, not inherited: `REQ-A.5` tokenised as `REQ-A`,
    collapsing five families into five phantoms."""
    _, total, _ = scan("REQ-A.5 and REQ-D.22 and REQ-E.1 and REQ-F.12 and REQ-C.35")
    assert set(total) == {"REQ-A.5", "REQ-D.22", "REQ-E.1", "REQ-F.12", "REQ-C.35"}
    union = set(_inv()["union"])
    assert {"REQ-A.5", "REQ-D.22", "REQ-E.1"} <= union
    assert "REQ-A" not in union and "REQ-D" not in union
