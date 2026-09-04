"""PORT-07 — governance register integrity, retargeted to canonical authorities.

The port source asserts its BRD->build register (`mvc_requirements.py`) against
the filesystem. That register does not exist here, and copying the test would
assert nothing: this repository's authorities are different artefacts making
different claims. What ports is the *discipline* — a register is only worth the
citations underneath it, so each one is checked against the filesystem, against
git, and against the other registers, rather than against itself.

Four canonical authorities are under assertion:

  SEAL      `CANONICAL_REPOSITORY_AUTHORITY_SEAL.json`   — MVC-GOV-CANON-001
  CUSTODY   `EVIDENCE_CUSTODY_INDEX.json`                — MVC-EVIDENCE-CUSTODY-INDEX-001
  MANIFEST  `petcare_execution/EVIDENCE/MANIFEST.json`   — petcare-evidence-manifest-v1
  PORT      `PORT_REGISTER.json`                         — MVC-PORT-REGISTER-001

They can drift into false assurance in ways that all read as PASS:

  1. a register cites a path that is not on disk;
  2. a register binds a hash the bytes no longer produce;
  3. cited evidence is on disk but untracked, so it is protected by one working copy;
  4. a register declares an exception OPEN that another authority has already closed,
     or DONE for work that left no trace;
  5. two registers describing the same thing disagree;
  6. the register is empty, and every "nothing was wrong" assertion is vacuous.

Every check below is an armed guard: it fails on the forbidden state rather than
observing its absence. The comparators are exercised against deliberately
perturbed *copies* so that a matcher which always returned True cannot look
identical to a clean register, and the vacuity guards at the end pin the
denominators so an empty register cannot pass by evaluating nothing.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY"

SEAL_PATH = AUTHORITY / "CANONICAL_REPOSITORY_AUTHORITY_SEAL.json"
CUSTODY_PATH = AUTHORITY / "EVIDENCE_CUSTODY_INDEX.json"
PORT_PATH = AUTHORITY / "PORT_REGISTER.json"
PROSE_PLAN_PATH = AUTHORITY / "CANONICAL_PORT_DIFFERENTIAL_AND_PLAN.md"
MANIFEST_PATH = ROOT / "petcare_execution/EVIDENCE/MANIFEST.json"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


SEAL = _load(SEAL_PATH)
CUSTODY = _load(CUSTODY_PATH)
PORT = _load(PORT_PATH)
MANIFEST = _load(MANIFEST_PATH)


# ---------------------------------------------------------------------------
# Hashing — one definition, used by the tests and by their positive controls
# ---------------------------------------------------------------------------

def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dir_manifest_sha(directory: Path) -> str:
    """Hash a directory over its members' sorted `relpath  sha256` lines.

    A directory has no bytes of its own. This mirrors the method the custody
    index used to bind its four directory citations, so it is re-derivable and
    sensitive to any member changing. Reimplementing it differently here would
    make every directory citation fail for a reason that is not drift.
    """
    rows = [
        f"{f.relative_to(directory).as_posix()}  {_file_sha(f)}"
        for f in sorted(directory.rglob("*"))
        if f.is_file()
    ]
    return hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest()


def _bound_sha(target: Path, kind: str) -> str:
    return _dir_manifest_sha(target) if kind == "directory" else _file_sha(target)


def _prose_status(cell: str) -> str:
    """The status token from a prose plan status cell.

    The cell may carry a qualifier after an em dash — `OPEN - must consume,
    never re-own` — which is commentary on the status, not a different status.
    Taking the whole cell makes every qualified row look like an unknown status
    and the cross-artefact comparison then fails for a formatting reason rather
    than a governance one.
    """
    return re.split(r"[\u2014-]", cell.strip("*").strip(), maxsplit=1)[0].strip().strip("*").strip()


def _parse_prose_statuses(markdown: str) -> dict[str, str]:
    """Read `PORT-nn -> status` out of the prose plan's port table."""
    rows: dict[str, str] = {}
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("*").strip().strip("`") for c in line.strip("|").split("|")]
        if cells and re.fullmatch(r"PORT-\d{2}", cells[0]):
            rows[cells[0]] = _prose_status(cells[-1])
    return rows


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


# ---------------------------------------------------------------------------
# SEAL — the decision that makes this repository canonical
# ---------------------------------------------------------------------------

def test_seal_decision_document_exists_and_still_produces_its_bound_hash():
    """The seal binds the decision by hash, which is the only thing that stops
    the decision text being edited underneath a still-ACTIVE seal."""
    document = ROOT / SEAL["decision_document"]
    assert document.exists(), f"seal cites a decision document that is absent: {document}"
    assert _file_sha(document) == SEAL["decision_sha256"], (
        "the decision document no longer produces the hash the seal binds; "
        "either the text changed or the seal was not re-issued"
    )


def test_seal_cited_locations_exist_on_disk():
    marketplace = ROOT / SEAL["marketplace_canonical_location"]
    assert marketplace.is_dir(), (
        f"seal names a canonical marketplace location that is not a directory: {marketplace}"
    )


def test_seal_referenced_commits_are_real_objects():
    """`ep07_seal_status: PRESERVED` is a claim about a commit. A seal that
    named a commit which did not exist would preserve nothing."""
    sha = SEAL["ep07_seal_commit"]
    proc = _git("cat-file", "-t", sha)
    assert proc.stdout.strip() == "commit", (
        f"ep07_seal_commit {sha} is not a commit in this repository: "
        f"{proc.stdout.strip() or proc.stderr.strip()}"
    )


def test_no_seal_exception_is_open_while_a_closure_record_exists():
    """Defect class 4, in the direction that inflates risk.

    A closure record and a seal that still lists the same id as OPEN cannot
    both be right. The stale one is normally the seal, because closing work
    writes a closure document and nobody re-opens the seal to amend it. Left
    alone it makes the programme look more blocked than it is, and it teaches
    readers that the seal's exception list is decorative.
    """
    still_open = [
        e["id"] for e in SEAL["open_exceptions"] if "OPEN" in e["status"].upper()
    ]
    contradicted = [
        i for i in still_open
        if any((AUTHORITY / f"{i}{suffix}").exists()
               for suffix in ("_CLOSURE.md", "_RECONCILIATION.md"))
    ]
    assert contradicted == [], (
        "seal lists exceptions as OPEN for which a closure record exists: "
        f"{contradicted}"
    )


def test_every_seal_exception_closure_reference_resolves():
    """The opposite direction: an exception may only claim it was closed by
    naming an artefact that is actually there."""
    dangling = [
        (e["id"], e["closure_record"])
        for e in SEAL["open_exceptions"]
        if e.get("closure_record") and not (ROOT / e["closure_record"]).exists()
    ]
    assert dangling == [], f"closure records cited but absent: {dangling}"


# ---------------------------------------------------------------------------
# CUSTODY — cited evidence is versioned and hash-bound
# ---------------------------------------------------------------------------

def test_every_cited_evidence_path_exists():
    missing = sorted(p for p in CUSTODY["cited_paths"] if not (ROOT / p).exists())
    assert missing == [], f"cited evidence with no artefact on disk: {missing}"


def test_every_cited_evidence_path_still_matches_its_bound_hash():
    drifted = []
    for path, entry in CUSTODY["cited_paths"].items():
        target = ROOT / path
        if not target.exists():
            continue  # already reported above
        actual = _bound_sha(target, entry["kind"])
        if actual != entry["sha256"]:
            drifted.append((path, f"{entry['sha256'][:12]}!={actual[:12]}"))
    assert drifted == [], f"evidence bytes no longer match the bound hash: {drifted}"


def test_every_cited_evidence_path_is_tracked_by_git():
    """The defect the custody closure was written to fix: evidence underwriting
    a CLOSED_EVIDENCED status living only in one working copy."""
    untracked = []
    for path in sorted(CUSTODY["cited_paths"]):
        if _git("ls-files", "--error-unmatch", path).returncode == 0:
            continue
        # A directory citation is tracked through its members, not itself.
        if not _git("ls-files", path).stdout.strip():
            untracked.append(path)
    assert untracked == [], f"cited evidence not versioned: {untracked}"


def test_custody_index_still_admits_its_hashes_are_retrospective():
    """A hash that implied it had always been present would be a worse artefact
    than no hash at all, because it would backdate the closure it supports."""
    assert CUSTODY["hash_binding_date"], "custody index does not date its binding"
    assert "retrospectively" in CUSTODY["note"], (
        "custody index no longer states that its hashes were bound after the fact"
    )


def test_custody_totals_reconcile_with_their_own_tables():
    assert CUSTODY["cited_paths_total"] == len(CUSTODY["cited_paths"])
    assert CUSTODY["evidence_files_total"] == len(CUSTODY["all_evidence_files"])


# ---------------------------------------------------------------------------
# MANIFEST — the petcare_execution evidence snapshot
# ---------------------------------------------------------------------------

def test_manifest_count_matches_its_own_file_list():
    """A declared count that exceeds the list is how a published total becomes
    arithmetic fiction."""
    assert MANIFEST["file_count"] == len(MANIFEST["files"])


def test_manifest_paths_are_unique_and_hashes_well_formed():
    paths = [f["path"] for f in MANIFEST["files"]]
    duplicates = sorted({p for p in paths if paths.count(p) > 1})
    assert duplicates == [], f"manifest lists the same path twice: {duplicates}"
    malformed = [f["path"] for f in MANIFEST["files"] if not _SHA256_RE.match(f["sha256"])]
    assert malformed == [], f"manifest entries without a well-formed sha256: {malformed}"


def test_every_manifest_path_exists():
    missing = [f["path"] for f in MANIFEST["files"] if not (ROOT / f["path"]).exists()]
    assert missing == [], f"manifest cites {len(missing)} files not on disk: {missing[:10]}"


def test_every_manifest_file_still_produces_its_recorded_hash():
    drifted = []
    for entry in MANIFEST["files"]:
        target = ROOT / entry["path"]
        if not target.is_file():
            continue
        actual = _file_sha(target)
        if actual != entry["sha256"]:
            drifted.append((entry["path"], f"{entry['sha256'][:12]}!={actual[:12]}"))
    assert drifted == [], f"manifest bytes drifted: {drifted[:10]}"


# ---------------------------------------------------------------------------
# PORT — the port register against git and the filesystem
# ---------------------------------------------------------------------------

_PORT_STATUSES = {"OPEN", "DONE"}


def test_port_ids_are_unique_contiguous_and_match_the_declared_denominator():
    ids = [p["id"] for p in PORT["ports"]]
    assert len(set(ids)) == len(ids), f"duplicate PORT ids: {ids}"
    assert len(ids) == PORT["denominator"], (
        f"register declares {PORT['denominator']} ports and lists {len(ids)}"
    )
    expected = [f"PORT-{n:02d}" for n in range(1, PORT["denominator"] + 1)]
    assert sorted(ids) == expected, f"PORT ids are not contiguous: {sorted(ids)}"


def test_every_port_status_is_a_known_status():
    unknown = sorted({p["status"] for p in PORT["ports"]} - _PORT_STATUSES)
    assert unknown == [], f"unrecognised PORT statuses: {unknown}"


def test_every_done_port_names_a_target_that_exists():
    """DONE is a claim that a behaviour landed somewhere. A DONE row whose
    target is absent is the port-plan equivalent of a dangling citation."""
    dangling = [
        (p["id"], t)
        for p in PORT["ports"]
        if p["status"] == "DONE"
        for t in p["targets"]
        if not (ROOT / t).exists()
    ]
    assert dangling == [], f"DONE ports whose target is not on disk: {dangling}"


def test_every_done_port_cites_a_closing_commit_that_is_a_real_object():
    missing = [p["id"] for p in PORT["ports"] if p["status"] == "DONE" and not p.get("closing_commit")]
    assert missing == [], f"DONE ports with no closing commit: {missing}"

    unresolved = [
        (p["id"], p["closing_commit"])
        for p in PORT["ports"]
        if p["status"] == "DONE"
        and _git("cat-file", "-t", p["closing_commit"]).stdout.strip() != "commit"
    ]
    assert unresolved == [], f"closing commits that are not commits here: {unresolved}"


def test_open_ports_do_not_carry_a_closing_commit():
    """The inverse guard. An OPEN row with a closing commit is either a status
    that was never advanced or a commit reference that means nothing."""
    contradictory = [
        p["id"] for p in PORT["ports"] if p["status"] == "OPEN" and p.get("closing_commit")
    ]
    assert contradictory == [], f"OPEN ports carrying a closing commit: {contradictory}"


def test_port_register_and_prose_plan_agree_on_every_status():
    """Defect class 5. Two artefacts describe the same ten ports; the prose
    carries the reasoning and the JSON carries the falsifiable claims. When they
    disagree, a reader gets whichever one they happened to open."""
    rows = _parse_prose_statuses(PROSE_PLAN_PATH.read_text(encoding="utf-8"))

    assert rows, "no PORT rows parsed from the prose plan; the parser is broken"

    register = {p["id"]: p["status"] for p in PORT["ports"]}
    assert set(rows) == set(register), (
        f"prose plan and register list different ports: "
        f"prose-only={sorted(set(rows) - set(register))} "
        f"register-only={sorted(set(register) - set(rows))}"
    )
    disagreements = {i: (rows[i], register[i]) for i in rows if rows[i] != register[i]}
    assert disagreements == {}, (
        f"prose plan and PORT register disagree (prose, register): {disagreements}"
    )


def test_the_retired_role_is_not_reintroduced_by_any_port():
    """W0-D retires `pharmacy_operator` and fails dispensing closed to the
    veterinarian. The port source still carries it as a first-class role, so the
    register is asserted to keep saying so — a prohibition that quietly vanished
    from the register would stop being a prohibition."""
    assert "pharmacy_operator_role" in PORT["must_not_port"], (
        "the pharmacy_operator prohibition has disappeared from the port register"
    )


# ---------------------------------------------------------------------------
# Positive controls — the comparators must fail on a known-bad input
# ---------------------------------------------------------------------------
#
# Every assertion above passes by finding nothing wrong, which is exactly what a
# broken comparator returns. These perturb a COPY in a temporary directory, so
# the proof that the guard is armed never touches the evidence it guards.

def test_file_hash_comparator_rejects_a_perturbed_copy():
    source = SEAL_PATH
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / source.name
        shutil.copy2(source, copy)
        assert _file_sha(copy) == _file_sha(source), "copy was not byte-identical"

        copy.write_bytes(copy.read_bytes() + b"\n")
        assert _file_sha(copy) != _file_sha(source), (
            "the file hash comparator did not notice an appended byte"
        )


def test_directory_manifest_comparator_rejects_a_perturbed_member():
    """Directory citations are the weaker half of the custody index: the
    directory's own bytes cannot change, so only a member can drift. This proves
    a member change is visible."""
    directories = [
        p for p, e in CUSTODY["cited_paths"].items()
        if e["kind"] == "directory" and (ROOT / p).is_dir()
    ]
    assert directories, "no directory citations to control against"

    source = ROOT / directories[0]
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / source.name
        shutil.copytree(source, copy)
        assert _dir_manifest_sha(copy) == _dir_manifest_sha(source), (
            "the directory copy did not reproduce the source manifest hash"
        )

        member = next(f for f in sorted(copy.rglob("*")) if f.is_file())
        member.write_bytes(member.read_bytes() + b"x")
        assert _dir_manifest_sha(copy) != _dir_manifest_sha(source), (
            "the directory manifest hash did not notice a member changing"
        )


def test_git_tracking_check_rejects_a_path_that_is_not_tracked():
    """`git ls-files` returns success and empty output for an unknown path, so
    a check that only looked at the return code would pass on everything."""
    assert _git("ls-files", "--error-unmatch", "petcare_execution").returncode == 0
    assert _git("ls-files", "--error-unmatch", "this/path/is/not/tracked").returncode != 0
    assert _git("ls-files", "this/path/is/not/tracked").stdout.strip() == ""


def test_prose_status_parser_is_not_matching_everything():
    """The cross-artefact test compares parsed prose against the register. A
    parser that returned an empty mapping, or that mapped every id to the same
    status, would agree with anything."""
    rows = _parse_prose_statuses(PROSE_PLAN_PATH.read_text(encoding="utf-8"))

    assert len(rows) == PORT["denominator"], (
        f"parser found {len(rows)} PORT rows in the prose plan, expected "
        f"{PORT['denominator']}"
    )
    assert set(rows.values()) <= _PORT_STATUSES, (
        f"parser produced statuses outside the known set: {set(rows.values())}"
    )

    # The real control, run against synthetic rows rather than the live plan.
    # Asserting that the live statuses differ from each other only worked while
    # some port was still open; once every row reached DONE it would have
    # started failing for a reason that is not a defect. A synthetic table
    # proves the parser reads the status column, discriminates between values,
    # strips emphasis, and drops a trailing qualifier -- and keeps proving it
    # whatever the register happens to say.
    synthetic = "\n".join([
        "| ID | Capability | Target | Risk | Status |",
        "|---|---|---|---|---|",
        "| PORT-01 | a | `x` | low | OPEN |",
        "| **PORT-02** | b | `y` | low | **DONE** |",
        "| PORT-03 | c | `z` | low | OPEN \u2014 must consume, never re-own |",
        "| NOT-A-PORT | d | `w` | low | DONE |",
    ])
    parsed = _parse_prose_statuses(synthetic)
    assert parsed == {"PORT-01": "OPEN", "PORT-02": "DONE", "PORT-03": "OPEN"}, parsed


# ---------------------------------------------------------------------------
# Vacuity guards — pin the denominators
# ---------------------------------------------------------------------------

def test_the_registers_under_assertion_are_populated():
    """Every check above compares against an empty list, so empty registers
    would satisfy all of them while checking nothing."""
    assert len(CUSTODY["cited_paths"]) >= 10, "custody index citation set collapsed"
    assert len(CUSTODY["all_evidence_files"]) >= 40, "custody evidence set collapsed"
    assert MANIFEST["file_count"] >= 300, "evidence manifest collapsed"
    assert len(PORT["ports"]) == 10, "port register collapsed"
    assert len(SEAL["open_exceptions"]) >= 1, (
        "seal declares no exceptions at all; the closure guards became vacuous"
    )


def test_the_hash_assertion_set_is_not_empty():
    """The two hash tests iterate; an iteration over nothing is a green test
    that verified nothing. This pins how many hashes were actually recomputed."""
    hashed_citations = [
        p for p, e in CUSTODY["cited_paths"].items()
        if (ROOT / p).exists() and e["kind"] in {"file", "directory"}
    ]
    assert len(hashed_citations) >= 10, (
        f"only {len(hashed_citations)} custody hashes were recomputed"
    )

    manifest_files = [f for f in MANIFEST["files"] if (ROOT / f["path"]).is_file()]
    assert len(manifest_files) >= 300, (
        f"only {len(manifest_files)} manifest hashes were recomputed"
    )
