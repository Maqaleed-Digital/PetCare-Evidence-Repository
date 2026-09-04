"""Authority residency — a citation is not the artefact.

`499` is the product requirement denominator and it derives from AUTH-01,
AUTH-02 and AUTH-03, none of which is in this repository. The subtle part is
that all three have a `source_path` in the authority table and it *resolves* —
to `PHASE1_SCOPE_GATES_ACCEPTANCE.md`, the Phase-1 pack that names them in a
reference list. A traceability check that asked only "does the cited path
resolve?" reports all three healthy and the hole closed.

So residency is defined structurally and checked structurally: an authority is
resident when `petcare_execution/AUTHORITY/<id>/` holds a conforming manifest
and the export it names, and the export's bytes still produce the recorded hash.
Nothing else counts, and the four things that most look like they should count
are asserted NOT to.

These tests fail closed in the useful direction. While AUTH-01 is non-resident
they assert it is non-resident and that `499` stays relayed; when it is ingested
they switch to verifying the ingestion. Neither state passes by accident.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))

from cross_repository_traceability import unmeasurable  # noqa: E402

AUTHORITY_ROOT = ROOT / "petcare_execution" / "AUTHORITY"
SCHEMA_PATH = AUTHORITY_ROOT / "AUTHORITY_INGESTION_SCHEMA.json"
SPEC_PATH = AUTHORITY_ROOT / "AUTHORITY_INGESTION_SPEC.md"

#: The authorities `499` derives from. Precedence 1, 2 and 3.
DERIVING_AUTHORITIES = ("AUTH-01", "AUTH-02", "AUTH-03")

#: Where all three currently appear, and the only place they do.
CITATION_ONLY = (
    ROOT / "petcare_execution" / "PHASE_1_EXECUTION_PACK" / "PHASE1_SCOPE_GATES_ACCEPTANCE.md"
)

_REQUIRED_MANIFEST_FIELDS = (
    "authority_id", "document", "version", "source_system", "source_identity",
    "source_last_edited_utc", "exported_utc", "exported_by", "export_filename",
    "content_sha256", "row_count", "id_field", "original_ids_preserved",
    "semantic_normalisation_applied", "excluded_rows",
)


def is_resident(authority_id: str) -> bool:
    """The structural definition. Deliberately strict."""
    directory = AUTHORITY_ROOT / authority_id
    manifest_path = directory / "MANIFEST.json"
    if not manifest_path.is_file():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if any(field not in manifest for field in _REQUIRED_MANIFEST_FIELDS):
        return False
    if manifest.get("original_ids_preserved") is not True:
        return False
    if manifest.get("semantic_normalisation_applied") is not False:
        return False
    export = directory / str(manifest["export_filename"])
    if not export.is_file():
        return False
    actual = hashlib.sha256(export.read_bytes()).hexdigest()
    return actual == manifest["content_sha256"]


# ---------------------------------------------------------------------------
# The contract exists and says what it must
# ---------------------------------------------------------------------------

def test_the_ingestion_schema_and_spec_exist():
    assert SCHEMA_PATH.is_file(), "no ingestion schema; residency would be undefined"
    assert SPEC_PATH.is_file(), "no ingestion spec"


def test_the_schema_names_what_does_not_count_as_residency():
    """The list of near-misses is the load-bearing half of the rule."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    insufficient = schema["residency_rule"]["explicitly_insufficient"]
    joined = " ".join(insufficient).lower()
    assert len(insufficient) >= 4
    assert "names the authority in prose" in joined
    assert "resolves to a document citing it" in joined


def test_the_schema_forbids_normalisation_and_renumbering():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["manifest"]["original_ids_preserved"]["const"] is True
    assert schema["manifest"]["semantic_normalisation_applied"]["const"] is False


def test_the_schema_requires_the_exclusion_to_be_itemised():
    """`499` is stated as '500 authored less REQ-MVC-1, which is prose'. Without
    the exclusion carried by id, that subtraction cannot be audited."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert "excluded_rows" in schema["manifest"]
    assert schema["manifest"]["excluded_rows"]["required"] is True
    assert "REQ-MVC-1" in schema["manifest"]["excluded_rows"]["note"]


# ---------------------------------------------------------------------------
# Current state: not resident, and provably so
# ---------------------------------------------------------------------------

def test_the_deriving_authorities_are_not_repository_resident():
    resident = [a for a in DERIVING_AUTHORITIES if is_resident(a)]
    assert resident == [], (
        f"{resident} now report as resident. If they were genuinely ingested, "
        "update mvc_authorities.py and the 499 status together with this test."
    )


def test_the_citation_document_exists_and_names_all_three():
    """Establishes that the near-miss is real: the reference list IS there, and
    it is what a naive residency check would find."""
    text = CITATION_ONLY.read_text(encoding="utf-8")
    assert "PetCare BRD v1.1" in text
    assert "AI-Native Technical Architecture" in text
    assert "Agentic AI Feature Layer" in text or "Vendor and SI Enablement" in text


def test_a_document_that_merely_cites_an_authority_does_not_make_it_resident():
    """The discriminator, stated as an assertion.

    `CITATION_ONLY` exists, names all three authorities, and is exactly what
    their `source_path` resolves to. Residency must still be False.
    """
    assert CITATION_ONLY.is_file()
    for authority in DERIVING_AUTHORITIES:
        assert not is_resident(authority), (
            f"{authority} counted as resident on the strength of a citation"
        )


def test_the_residency_check_is_not_simply_returning_false():
    """Positive control. A check that returned False for everything would give
    the same clean result on a genuinely ingested authority.

    A conforming fixture is built in a temp directory and must read as resident;
    then each requirement is broken in turn and must read as non-resident.
    """
    import tempfile

    global AUTHORITY_ROOT
    original = AUTHORITY_ROOT
    try:
        with tempfile.TemporaryDirectory() as tmp:
            AUTHORITY_ROOT = Path(tmp)
            directory = AUTHORITY_ROOT / "AUTH-99"
            directory.mkdir()
            payload = b"id,title\nREQ-1,alpha\nREQ-2,beta\n"
            (directory / "export.csv").write_bytes(payload)
            manifest = {
                "authority_id": "AUTH-99",
                "document": "Fixture",
                "version": "1.0",
                "source_system": "filesystem",
                "source_identity": {"id": "fixture", "title_at_export": "Fixture"},
                "source_last_edited_utc": "2026-09-04T00:00:00Z",
                "exported_utc": "2026-09-04T00:00:01Z",
                "exported_by": "positive-control",
                "export_filename": "export.csv",
                "content_sha256": hashlib.sha256(payload).hexdigest(),
                "row_count": 2,
                "id_field": "id",
                "original_ids_preserved": True,
                "semantic_normalisation_applied": False,
                "excluded_rows": [],
            }
            path = directory / "MANIFEST.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")

            assert is_resident("AUTH-99"), "conforming fixture did not read as resident"

            # 1. bytes drift
            (directory / "export.csv").write_bytes(payload + b"REQ-3,gamma\n")
            assert not is_resident("AUTH-99"), "hash mismatch was not detected"
            (directory / "export.csv").write_bytes(payload)

            # 2. normalisation admitted
            path.write_text(json.dumps({**manifest, "semantic_normalisation_applied": True}))
            assert not is_resident("AUTH-99"), "a normalised export read as resident"

            # 3. ids not preserved
            path.write_text(json.dumps({**manifest, "original_ids_preserved": False}))
            assert not is_resident("AUTH-99"), "a renumbered export read as resident"

            # 4. a required field dropped
            reduced = {k: v for k, v in manifest.items() if k != "source_identity"}
            path.write_text(json.dumps(reduced))
            assert not is_resident("AUTH-99"), "a manifest with no provenance read as resident"

            # 5. the export named but absent
            path.write_text(json.dumps(manifest))
            (directory / "export.csv").unlink()
            assert not is_resident("AUTH-99"), "a missing export read as resident"
    finally:
        AUTHORITY_ROOT = original


# ---------------------------------------------------------------------------
# The denominator follows residency, not the other way round
# ---------------------------------------------------------------------------

def test_499_stays_relayed_while_its_authorities_are_absent():
    record = unmeasurable()
    assert record["status"] == "RELAYED_NOT_REMEASURED"
    assert all(not is_resident(a) for a in DERIVING_AUTHORITIES)


def test_499_may_not_be_declared_measured_without_an_ingested_authority():
    """The rule stated as an assertion, so a future edit that flips the status
    without doing the ingestion fails here rather than shipping."""
    record = unmeasurable()
    claims_measured = record["status"] not in {"RELAYED_NOT_REMEASURED", "UNMEASURABLE"}
    if claims_measured:
        assert any(is_resident(a) for a in DERIVING_AUTHORITIES), (
            "499 claims a measured status while AUTH-01/02/03 are all non-resident"
        )


def test_the_smaller_denominators_are_not_offered_as_the_estate():
    """106, 27 and 315 have each been used as 'the denominator'. Only one figure
    is the product estate, and it is none of them."""
    backlog = ROOT / "petcare_execution" / "PHASE_1_EXECUTION_PACK" / "PHASE1_BACKLOG.csv"
    rows = [ln for ln in backlog.read_text(encoding="utf-8").splitlines() if ln.strip()]
    story_rows = len(rows) - 1  # header
    assert story_rows < 100, "the Phase-1 backlog is a slice, not the estate"
    assert unmeasurable()["value"] != story_rows

    spec = SPEC_PATH.read_text(encoding="utf-8")
    for figure in ("106", "315", "499"):
        assert figure in spec, f"the spec does not distinguish {figure} from the estate"


def test_no_authority_directory_holds_invented_rows():
    """Guards against the tempting shortcut: writing a plausible export to make
    the ratio presentable. Any directory present must be a real ingestion."""
    if not AUTHORITY_ROOT.is_dir():
        pytest.fail("the authority root should exist once the spec is written")
    for directory in sorted(p for p in AUTHORITY_ROOT.iterdir() if p.is_dir()):
        assert (directory / "MANIFEST.json").is_file(), (
            f"{directory.name} holds files with no ingestion manifest"
        )
        assert is_resident(directory.name), (
            f"{directory.name} has a manifest that does not verify"
        )
