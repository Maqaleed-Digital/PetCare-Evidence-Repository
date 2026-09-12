"""W0-F architecture contracts — hosting location is configuration, not semantics.

The Sponsor's D.21 ruling makes migration to KSA a **scheduled certainty**, not a
contingency:

> "Portfolio precedent may establish the temporary operating location, but not the
> final residency destination. MyVetiCare may remain out of Kingdom until the
> approved KSA hosting site is ready, at which point migration to KSA becomes
> mandatory."

That changes what correct code looks like. A region literal in application code
is not merely untidy — it is a line that will have to be found and changed under
time pressure during a mandatory migration, and the ones that are missed become
silent writes to the wrong jurisdiction.

So the contract is: **the application behaves identically in either location, and
the only difference is where configuration points it.**

Each guard here has a meta-test that plants the violation and proves the guard
fires. A guard that has never failed is indistinguishable from one whose matcher
is broken.

Authority: MVC-W0F-ADDENDUM-001 · MVC-W0F-DATA-STORE-DECISION-001 ·
MVC-W0F-SECRET-SOURCE-DECISION-001.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: Trees where a hosting location must never appear as a literal.
#:
#: `scripts` was added by W0-F's persistence work. It was not an oversight when
#: the list was written — `scripts/` held only verification scanners, which do
#: not connect anywhere. It holds an operational tool now:
#: `apply_migrations.py` applies the schema to a database, and
#: `identity_migration_dryrun.py` can write identities to one. A region or
#: endpoint literal in either would pin the mandatory KSA migration to a
#: location exactly as effectively as one in the application, and would be
#: outside every guard that exists to prevent that.
APPLICATION_TREES = [
    "petcare_api",
    "petcare_runtime/src",
    "petcare_runtime/migrations",
    "scripts",
]

#: An AWS region identifier in any partition. Deliberately broad: the guard must
#: catch a region nobody has thought of yet, not just the two in current use.
_AWS_REGION = re.compile(
    r"\b(?:us|eu|ap|me|sa|ca|af|il|cn)-(?:north|south|east|west|central|"
    r"northeast|northwest|southeast|southwest)-\d\b",
    re.IGNORECASE,
)

#: A provider endpoint hostname — the other way a location gets pinned.
_PROVIDER_ENDPOINT = re.compile(
    r"\b[\w.-]+\.(?:rds|amazonaws|run\.app|azure)\.[\w.]+\b", re.IGNORECASE
)

#: KSA target identifiers. These must stay placeholders until the site is
#: approved; inventing a value for one is how an unapproved destination becomes
#: load-bearing.
KSA_PLACEHOLDERS = [
    "TARGET_KSA_HOSTING_AUTHORITY",
    "TARGET_KSA_REGION_OR_SITE",
    "TARGET_KSA_DATABASE_ENDPOINT",
]

#: A placeholder assigned a concrete value, e.g. TARGET_KSA_REGION_OR_SITE = "me-south-1".
_PLACEHOLDER_ASSIGNED = re.compile(
    r"(" + "|".join(KSA_PLACEHOLDERS) + r")\s*[:=]\s*[\"'](?!<|TBD|TBC|PENDING|\s*$)[^\"']+[\"']"
)

#: A branch on jurisdiction.
_RESIDENCY_BRANCH = re.compile(
    r"\bif\b[^\n]{0,60}\b(is_ksa|in_kingdom|residency|is_saudi|ksa_mode)\w*",
    re.IGNORECASE,
)


def _source_files() -> list[Path]:
    files: list[Path] = []
    for tree in APPLICATION_TREES:
        base = ROOT / tree
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix not in {".py", ".sql"}:
                continue
            if "__pycache__" in str(p) or "/tests/" in str(p):
                continue
            files.append(p)
    return files


def _strip_comments(path: Path, text: str) -> str:
    """Comments may discuss a region; code may not contain one.

    The distinction matters: a docstring explaining why the region is not
    hardcoded would otherwise be flagged by the guard forbidding hardcoded
    regions, which trains readers to widen the exclusion list until it means
    nothing.
    """
    if path.suffix == ".py":
        return re.sub(r"#.*$", "", text, flags=re.M)
    return re.sub(r"--.*$", "", text, flags=re.M)


def _scan_one(path: Path, rx: re.Pattern) -> bool:
    return bool(rx.search(_strip_comments(path, path.read_text(encoding="utf-8"))))


def test_source_scan_is_not_vacuous():
    files = _source_files()
    assert len(files) > 40, f"application scan collapsed to {len(files)} files"


def test_no_hosting_region_is_hardcoded_in_application_code():
    """D.21 portability rule 1. A region literal makes the mandatory KSA
    migration an application change instead of a configuration change."""
    offenders = []
    for f in _source_files():
        m = _AWS_REGION.search(_strip_comments(f, f.read_text(encoding="utf-8")))
        if m:
            offenders.append(f"{f.relative_to(ROOT)} -> {m.group(0)}")
    assert offenders == [], (
        f"hosting region hardcoded in application code (D.21 portability): {offenders}"
    )


def test_no_provider_endpoint_is_hardcoded_in_application_code():
    """The same defect wearing a hostname instead of a region code."""
    offenders = []
    for f in _source_files():
        m = _PROVIDER_ENDPOINT.search(_strip_comments(f, f.read_text(encoding="utf-8")))
        if m:
            offenders.append(f"{f.relative_to(ROOT)} -> {m.group(0)}")
    assert offenders == [], f"provider endpoint hardcoded in application code: {offenders}"


def test_ksa_target_placeholders_are_never_given_a_value():
    """D.21 portability rule 4.

    The KSA site is not approved. A placeholder that acquires a concrete value
    before approval is an unapproved destination becoming load-bearing — and by
    the time anyone looked it would be indistinguishable from an approved one.
    """
    offenders = []
    for f in ROOT.rglob("*"):
        if not f.is_file() or f.suffix not in {".py", ".sql", ".yaml", ".yml", ".json", ".ts"}:
            continue
        s = str(f)
        if ".git/" in s or "node_modules" in s or "__pycache__" in s:
            continue
        # This guard file must name the placeholders in order to forbid them,
        # and its meta-test plants an assigned one on purpose. Excluding the
        # guard itself is the same narrow exemption the retired-role guard uses;
        # it is the ONLY file exempted, and the exemption is one path, not a
        # pattern that could hide application code.
        if f.resolve() == Path(__file__).resolve():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        m = _PLACEHOLDER_ASSIGNED.search(text)
        if m:
            offenders.append(f"{f.relative_to(ROOT)} -> {m.group(0)[:60]}")
    assert offenders == [], (
        f"KSA target placeholder assigned a value before site approval: {offenders}"
    )


def test_no_residency_branch_exists_in_application_code():
    """D.21 portability rule 2.

    The application must not know which jurisdiction it is running in. A branch
    on residency is how "temporary" quietly becomes a supported permanent mode
    with its own behaviour, which is the outcome the ruling forbids.
    """
    offenders = []
    for f in _source_files():
        m = _RESIDENCY_BRANCH.search(_strip_comments(f, f.read_text(encoding="utf-8")))
        if m:
            offenders.append(f"{f.relative_to(ROOT)} -> {m.group(0).strip()[:50]}")
    assert offenders == [], f"application branches on residency: {offenders}"


# ---------------------------------------------------------------------------
# Meta-tests — each guard must be shown to fire
# ---------------------------------------------------------------------------

def test_region_guard_detects_a_planted_region(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('DB = "petcare.me-central-1.rds.amazonaws.com"\n', encoding="utf-8")
    assert _scan_one(planted, _AWS_REGION), "region guard missed a planted region"

    clean = tmp_path / "clean.py"
    clean.write_text('DB = os.environ["PETCARE_DB_URL"]\n', encoding="utf-8")
    assert not _scan_one(clean, _AWS_REGION), "region guard fired on config-driven code"


def test_region_guard_ignores_a_region_named_in_a_comment(tmp_path):
    """Prose must not trip it. The data-store decision discusses me-central-1 by
    name while forbidding it in code; a guard that could not tell those apart
    would be widened until it meant nothing."""
    commented = tmp_path / "commented.py"
    commented.write_text(
        "# siblings run in me-central-1; this service must not know that\n"
        'DB = os.environ["PETCARE_DB_URL"]\n',
        encoding="utf-8",
    )
    assert not _scan_one(commented, _AWS_REGION), "region guard fired on a comment"


def test_region_guard_is_not_limited_to_regions_in_current_use(tmp_path):
    """me-central-1 and eu-central-1 are today's regions. The guard must catch a
    region no one has used yet, or it only prevents repeating a known mistake."""
    for region in ("ap-southeast-2", "sa-east-1", "af-south-1", "il-central-1"):
        f = tmp_path / f"r_{region}.py"
        f.write_text(f'ENDPOINT = "svc.{region}.example.com"\n', encoding="utf-8")
        assert _scan_one(f, _AWS_REGION), f"region guard missed {region}"


def test_endpoint_guard_detects_a_planted_endpoint(tmp_path):
    planted = tmp_path / "ep.py"
    planted.write_text('HOST = "petcare-prod.abc123.rds.example.com"\n', encoding="utf-8")
    assert _scan_one(planted, _PROVIDER_ENDPOINT), "endpoint guard missed a planted host"


def test_placeholder_guard_detects_an_assigned_target(tmp_path):
    planted = tmp_path / "ksa.py"
    planted.write_text('TARGET_KSA_REGION_OR_SITE = "me-south-1"\n', encoding="utf-8")
    assert _PLACEHOLDER_ASSIGNED.search(planted.read_text()), (
        "placeholder guard missed an assigned KSA target"
    )

    for unresolved in ('"<TBD>"', '"TBD"', '"PENDING"'):
        f = tmp_path / "u.py"
        f.write_text(f"TARGET_KSA_REGION_OR_SITE = {unresolved}\n", encoding="utf-8")
        assert not _PLACEHOLDER_ASSIGNED.search(f.read_text()), (
            f"placeholder guard fired on an explicitly unresolved value {unresolved}"
        )


def test_residency_branch_guard_detects_a_planted_branch(tmp_path):
    planted = tmp_path / "resid.py"
    planted.write_text(
        "def route():\n    if is_ksa_region():\n        return 1\n    return 2\n",
        encoding="utf-8",
    )
    assert _scan_one(planted, _RESIDENCY_BRANCH), (
        "residency-branch guard missed a planted branch"
    )
