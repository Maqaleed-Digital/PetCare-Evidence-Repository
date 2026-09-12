"""The ruled first production tenant must not become a row without authorization.

Sponsor ruling of 12 September 2026 establishes the identity of the first
production tenant and draws the line explicitly:

> This ruling does not itself authorize creation of the tenant row, provisioning
> of production infrastructure, application of migrations, production credential
> entry, production identity creation, or cutover.
>
> P1_AUTHORIZED=NO

Naming authority is not creation authority. That distinction is easy to state
and easy to lose: the identifier is now written down in the governance record,
and the shortest path from "written down" to "created" is somebody adding one
`INSERT` to a migration during a cutover.

This guard closes that path. The identifier may appear in governance records and
in guards like this one; it may not appear in anything that would create it.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: The ruled identity. Named here because a guard must name what it forbids —
#: the same narrow exemption the retired-role and KSA-placeholder guards use.
RULED_TENANT_ID = "pharmacare_riyadh"

#: Trees that could CREATE a tenant. Governance records and evidence are where
#: the ruling legitimately lives and are deliberately excluded.
CREATION_TREES = [
    "petcare_runtime/migrations",
    "petcare_api",
    "petcare_runtime/src",
    "scripts",
]
_SUFFIXES = {".py", ".sql"}

_GUARD_FILES = {"tests/governance/test_production_tenant_not_created.py"}

#: Any statement that would put a row into the registry.
_TENANT_INSERT = re.compile(r"INSERT\s+INTO\s+tenant\b", re.IGNORECASE)


def _files() -> list[Path]:
    out = []
    for tree in CREATION_TREES:
        base = ROOT / tree
        if not base.exists():
            continue
        for p in base.rglob("*"):
            s = str(p)
            if not p.is_file() or p.suffix not in _SUFFIXES:
                continue
            if "__pycache__" in s:
                continue
            out.append(p)
    return out


def _code(path: Path) -> str:
    """Source with comment lines removed. Migration 0034 explains at length why
    it creates no rows; a guard that could not tell prose from a statement would
    flag the explanation."""
    lines = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        st = line.strip()
        if st.startswith("--") or st.startswith("#"):
            continue
        lines.append(re.sub(r"--.*$", "", line))
    return "\n".join(lines)


def test_the_scan_is_not_vacuous():
    files = _files()
    assert len(files) > 40, f"creation-tree scan collapsed to {len(files)} files"


def test_no_migration_creates_a_tenant_row():
    """The registry ships empty and stays empty until a governed act fills it.

    Scoped to MIGRATIONS. A migration's `INSERT` creates a row the moment the
    chain is applied, with no actor, no authorization and no audit event — which
    is precisely the act the ruling withholds.

    `PostgresTenantRepository.create` also contains an `INSERT INTO tenant`, and
    must: it is the governed MECHANISM a future authorized act will call. A guard
    that forbade the mechanism would forbid the registry from ever being used,
    and would be deleted the first time somebody needed it. The distinction is
    between code that CAN create a tenant and a row that IS created.

    Broader than the ruled identifier on purpose: an unnamed tenant baked into a
    migration is the same defect, and PRE-1's finding was that a tenant with no
    authority behind it is indistinguishable, once written, from one the Sponsor
    chose.
    """
    offenders = []
    for path in (ROOT / "petcare_runtime" / "migrations").glob("*.sql"):
        m = _TENANT_INSERT.search(_code(path))
        if m:
            offenders.append(f"{path.name} -> {m.group(0)}")
    assert offenders == [], (
        f"a migration would create a tenant row without authorization: {offenders}"
    )


def test_the_governed_creation_mechanism_still_exists():
    """The other side of the line above. A future authorized act needs
    something to call, and this guard must not have removed it."""
    repo = (ROOT / "petcare_api" / "postgres_repositories.py").read_text(encoding="utf-8")
    assert "class PostgresTenantRepository" in repo
    assert _TENANT_INSERT.search(repo), (
        "the governed tenant-creation mechanism is gone"
    )


def test_the_ruled_production_tenant_is_not_named_in_creating_code():
    """`pharmacare_riyadh` belongs in the governance record, not in a migration.

    Even outside an INSERT — a constant, a default, a fixture in serving code —
    the identifier's presence there is one edit away from creating it.
    """
    offenders = []
    for path in _files():
        rel = str(path.relative_to(ROOT))
        if rel in _GUARD_FILES or "/tests/" in rel:
            continue
        if RULED_TENANT_ID in _code(path):
            offenders.append(rel)
    assert offenders == [], (
        f"the ruled production tenant identifier appears in creating code: "
        f"{offenders}. Naming authority is not creation authority."
    )


def test_the_ruling_is_recorded_in_governance():
    """The other half. A guard that only forbade would be satisfied by the
    identifier existing nowhere at all — including in the record that ratifies
    it."""
    governance = ROOT / "petcare_execution" / "GOVERNANCE"
    recorded = [
        p for p in governance.rglob("*.md")
        if RULED_TENANT_ID in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert recorded, (
        "the ruled tenant identity is not recorded in any governance document"
    )


# ---------------------------------------------------------------------------
# Meta-tests — the guard must be shown to fire
# ---------------------------------------------------------------------------

def test_meta_a_planted_tenant_insert_is_detected(tmp_path):
    planted = tmp_path / "0099_planted.sql"
    planted.write_text(
        "INSERT INTO tenant (tenant_id, display_name)\n"
        "VALUES ('pharmacare_riyadh', 'Pharma Care Pharmacies');\n",
        encoding="utf-8",
    )
    assert _TENANT_INSERT.search(_code(planted))
    assert RULED_TENANT_ID in _code(planted)


def test_meta_a_commented_explanation_is_NOT_detected(tmp_path):
    """Migration 0034 says at length that it creates no rows, and names the
    identifiers it declines to invent. That must keep passing."""
    commented = tmp_path / "0034_like.sql"
    commented.write_text(
        "-- NO ROWS ARE CREATED. Not pharmacare_riyadh, not any other tenant.\n"
        "-- INSERT INTO tenant would be a live write and is gated.\n"
        "CREATE TABLE IF NOT EXISTS tenant (tenant_id TEXT PRIMARY KEY);\n",
        encoding="utf-8",
    )
    code = _code(commented)
    assert not _TENANT_INSERT.search(code)
    assert RULED_TENANT_ID not in code


def test_meta_the_real_migration_0034_still_passes(tmp_path):
    """The specific file this guard must never flag."""
    real = ROOT / "petcare_runtime/migrations/0034_pre1_tenant_registry.sql"
    code = _code(real)
    assert not _TENANT_INSERT.search(code), "0034 creates a tenant row"
    assert RULED_TENANT_ID not in code
