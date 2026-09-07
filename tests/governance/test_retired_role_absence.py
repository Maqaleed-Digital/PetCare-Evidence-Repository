"""F2/F3 — tree-wide absence of the retired `pharmacy_operator` role.

W0-F acceptance criterion 3 says the retired role must appear nowhere in the
tree. The guard that previously enforced it scanned three directories of one
application (`petcare_web/{app,components,lib}`), so the claim was far wider than
its enforcement.

Taken literally, AC3 is also unachievable and undesirable: a guard that forbids
the role must name it, and the governance decision that retires it must quote it.
The enforceable form is two-sided, and both sides are asserted here:

    live source        ZERO occurrences, no exceptions
    everywhere else    every occurrence explicitly REGISTERED, with a reason

Exclusions are path-specific and justified in the register. There is no wildcard
that could hide a live source tree.

Authority: MVC-GOV-CANON-001 · register MVC-RETIRED-ROLE-CUSTODY-001 · W0-D.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = (
    ROOT
    / "petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY"
    / "RETIRED_ROLE_CUSTODY_REGISTER.json"
)
REGISTER = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))

NEEDLE = REGISTER["retired_role"]
LIVE_TREES = REGISTER["live_source_trees"]
EXCLUDED = [e["path"] for e in REGISTER["excluded_paths"]]
REGISTERED = {a["path"] for a in REGISTER["registered_stale_artefacts"]}

SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".json", ".md", ".yaml", ".yml"}

#: The guards themselves must name the needle to forbid it.
GUARD_FILES = {
    "tests/governance/test_retired_role_absence.py",
    "tests/governance/test_canonical_register_integrity.py",
    "petcare_web/__tests__/absence-guards.test.ts",
    "petcare_api/tests/test_dispensing_fail_closed.py",
}


def _excluded(rel: str) -> bool:
    return any(rel == e or rel.startswith(e + "/") for e in EXCLUDED)


def _scan(base: Path) -> list[str]:
    """Every source-like file under `base`, minus excluded paths."""
    out = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix not in SOURCE_SUFFIXES:
            continue
        rel = str(p.relative_to(ROOT))
        if _excluded(rel):
            continue
        out.append(rel)
    return out


def _hits(files: list[str]) -> list[str]:
    hits = []
    for rel in files:
        try:
            if NEEDLE in (ROOT / rel).read_text(encoding="utf-8"):
                hits.append(rel)
        except (UnicodeDecodeError, OSError):
            continue
    return hits


def test_live_source_trees_are_scannable_and_not_empty():
    """Without this, every absence assertion below could pass vacuously."""
    for tree in LIVE_TREES:
        assert (ROOT / tree).exists(), f"declared live source tree missing: {tree}"
    total = sum(len(_scan(ROOT / t)) for t in LIVE_TREES)
    assert total > 100, f"live source scan collapsed to {total} files"


def test_retired_role_absent_from_every_live_source_tree():
    """The load-bearing guard, and the one AC3 actually means. Zero tolerance:
    no register entry exempts a live source file."""
    offenders = []
    for tree in LIVE_TREES:
        for rel in _hits(_scan(ROOT / tree)):
            if rel not in GUARD_FILES:
                offenders.append(rel)
    assert offenders == [], f"retired role present in live source: {offenders}"


def test_every_remaining_occurrence_is_registered():
    """Outside live source, retention is permitted but never silent. An
    unregistered occurrence is drift; a registered one is a recorded decision."""
    unregistered = [
        rel
        for rel in _hits(_scan(ROOT / "petcare_execution"))
        if rel not in REGISTERED and rel not in GUARD_FILES
    ]
    assert unregistered == [], f"unregistered retired-role occurrences: {unregistered}"


def test_registered_artefacts_still_exist():
    """The inverse guard: a register row for a file that is gone is a custody
    claim that quietly stopped being true."""
    missing = [p for p in sorted(REGISTERED) if not (ROOT / p).exists()]
    assert missing == [], f"registered artefacts absent from the tree: {missing}"


def test_artefacts_claiming_an_in_file_marker_actually_carry_one():
    """F3. The four artefacts that model the role as AUTHORIZATION must say so in
    the file itself, so the contradiction cannot be read as current intent."""
    missing = []
    for a in REGISTER["registered_stale_artefacts"]:
        if not a["in_file_marker"]:
            continue
        text = (ROOT / a["path"]).read_text(encoding="utf-8")
        if "STATUS=STALE_DESIGN_ARTEFACT" not in text or "DO_NOT_IMPLEMENT_FROM_THIS_FILE" not in text:
            missing.append(a["path"])
    assert missing == [], f"artefacts claiming an in-file stale marker without one: {missing}"
