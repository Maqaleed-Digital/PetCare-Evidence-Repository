"""The genesis authority must stay the narrow thing the ruling authorized.

Sponsor ruling of 12 September 2026, `MVC-GENESIS-PLATFORM-ADMIN-001`, §7:

> This ruling does not authorize:
>
> * creation of a second `platform_admin`;
> * elevation of another identity to `platform_admin`;
> * arbitrary role modification;
> * a reusable bootstrap endpoint;
> * direct database privilege writes as an operating procedure;
> * seed identities;
> * default administrator credentials.

The genesis mechanism is the only privilege-creation path in the estate. Every
guard below exists because the shortest route from "a single-use act" to "a
standing privilege facility" is one small edit nobody argued about — a role
parameter added for a test, a route mounted for convenience, a default
credential added to make a runbook shorter.

Each guard is paired with a meta-test that plants the violation, because a
guard asserting an absence passes just as happily when it has stopped looking.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GENESIS_MODULE = ROOT / "petcare_api" / "platform_admin_genesis.py"
GENESIS_SCRIPT = ROOT / "scripts" / "governance" / "platform_admin_genesis.py"
MIGRATION = ROOT / "petcare_runtime" / "migrations" / "0035_genesis_platform_admin.sql"
MAIN = ROOT / "petcare_api" / "main.py"

#: The one role the governed procedure may produce.
GENESIS_ROLE = "platform_admin"

#: Roles the genesis procedure must be incapable of producing.
OTHER_ROLES = ("owner", "veterinarian", "partner_clinic_admin")

_CREDENTIAL_LITERAL = re.compile(
    r"(password|passwd|secret|credential)\s*(=|:)\s*['\"][^'\"]{3,}['\"]",
    re.IGNORECASE,
)

_ELEVATION = re.compile(r"(UPDATE\s+user_identity|ON\s+CONFLICT|\.upsert\s*\()", re.I)

_IDENTITY_INSERT = re.compile(
    r"INSERT\s+INTO\s+(user_identity|platform_admin_genesis)", re.I
)


def _code(path: Path) -> str:
    """Source with comment lines removed — these files explain at length what
    they decline to do, and a guard that could not tell prose from a statement
    would flag the explanation. Same treatment as
    `test_production_tenant_not_created.py`."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        st = line.strip()
        if st.startswith("--") or st.startswith("#"):
            continue
        out.append(re.sub(r"\s+--\s.*$", "", line))
    return "\n".join(out)


def _execute_signature() -> ast.arguments:
    tree = ast.parse(GENESIS_MODULE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PlatformAdminGenesisService":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "execute":
                    return item.args
    raise AssertionError(
        "PlatformAdminGenesisService.execute is gone; the guards below would "
        "pass vacuously"
    )


# ---------------------------------------------------------------------------
# Non-vacuity
# ---------------------------------------------------------------------------

def test_the_genesis_mechanism_exists():
    """Everything after this asserts a property OF the mechanism. If it were
    deleted or renamed, every guard below would pass having checked nothing."""
    assert GENESIS_MODULE.is_file(), "the genesis module is gone"
    assert MIGRATION.is_file(), "the genesis migration is gone"
    assert GENESIS_SCRIPT.is_file(), "the genesis operator entry point is gone"
    _execute_signature()


# ---------------------------------------------------------------------------
# §2 — the procedure must not accept an arbitrary role parameter
# ---------------------------------------------------------------------------

def test_the_genesis_procedure_has_no_role_parameter():
    """§2: *"The procedure must not accept an arbitrary role parameter. Its
    resulting role is fixed by the governed procedure."*

    Checked on the signature rather than on behaviour, because the property the
    ruling asks for is that the parameter does not EXIST. A parameter that is
    validated is still a parameter, and validation is one edit from a denylist
    with a hole in it.
    """
    args = _execute_signature()
    names = [a.arg for a in (args.posonlyargs + args.args + args.kwonlyargs)]

    offenders = [n for n in names if "role" in n.lower()]
    assert offenders == [], (
        f"the genesis procedure accepts a role-shaped parameter {offenders}; "
        f"§2 requires the resulting role to be fixed by the procedure itself"
    )
    assert args.vararg is None and args.kwarg is None, (
        "the genesis procedure accepts *args/**kwargs, so a role could reach it "
        "without appearing in the signature"
    )


def test_the_genesis_procedure_cannot_produce_any_other_role():
    """§2: it *"must not be capable of creating any other privileged role or of
    elevating an existing identity to another role."*"""
    code = _code(GENESIS_MODULE)
    assert "ROLE_PLATFORM_ADMIN" in code, (
        "the genesis module no longer names the one role it may produce"
    )

    offenders = [r for r in OTHER_ROLES if re.search(rf"['\"]{r}['\"]", code)]
    assert offenders == [], (
        f"the genesis module names another role as a literal {offenders}"
    )


def test_the_genesis_procedure_never_updates_an_existing_identity():
    """§2: it must not elevate an existing identity. An `UPDATE` or an upsert
    against `user_identity` would reach one; an `INSERT` cannot."""
    offenders = _ELEVATION.findall(_code(GENESIS_MODULE))
    assert offenders == [], (
        f"the genesis module can rewrite an existing identity via {offenders}; "
        f"elevation is a separate authority the ruling withholds"
    )


# ---------------------------------------------------------------------------
# §7 — no reusable bootstrap endpoint
# ---------------------------------------------------------------------------

def test_no_http_route_exposes_the_genesis_path():
    """§7 withholds *"a reusable bootstrap endpoint"*.

    The act happens once in the lifetime of a deployment. An endpoint that
    survives it is a permanently reachable privilege-creation surface whose only
    guard is a database row — and the estate has already recorded what a
    convenience path to `platform_admin` costs (`main.py`: *"a startup path that
    creates a `platform_admin` from a source literal is a backdoor whether or
    not anyone intended one"*).
    """
    offenders = []
    for path in (ROOT / "petcare_api").rglob("*.py"):
        if "__pycache__" in str(path) or "/tests/" in str(path):
            continue
        code = _code(path)
        if "platform_admin_genesis" not in code and "GenesisService" not in code:
            continue
        for line_no, line in enumerate(code.splitlines(), 1):
            if re.search(r"@(app|router)\.(get|post|put|patch|delete)", line):
                offenders.append(f"{path.name}:{line_no}")
    assert offenders == [], (
        f"a module wiring the genesis path also declares HTTP routes, so the "
        f"act is reachable over the network: {offenders}"
    )


def test_the_serving_application_does_not_import_the_genesis_path():
    """The stronger form of the guard above: the genesis module must not be
    reachable from the running API at all, so no future route can call it by
    accident."""
    assert "platform_admin_genesis" not in _code(MAIN), (
        "main.py imports the genesis path; the serving application must not be "
        "able to create a platform_admin"
    )


def test_startup_creates_no_platform_admin():
    """§7 withholds *"seed identities"*. PRE1_RULING=1-B discarded three seeded
    identities, one of them holding the highest role, whose password was a
    literal in a PUBLIC repository. The genesis mechanism must not quietly
    reintroduce that shape."""
    offenders = [
        line.strip() for line in _code(MAIN).splitlines()
        if "seed_user" in line and GENESIS_ROLE in line
    ]
    assert offenders == [], f"startup seeds a platform_admin: {offenders}"


# ---------------------------------------------------------------------------
# §2 / §7 — no default administrator credential
# ---------------------------------------------------------------------------

def test_the_genesis_path_embeds_no_credential():
    """§2: *"This ruling does not authorize inventing, embedding, or storing a
    default credential."*

    The genesis identity holds the highest role in the system, and this
    repository is PUBLIC. A default here is worse than the seed password PRE-1
    discarded, because the seed identities at least had no authority to
    administer tenants.
    """
    offenders = []
    for path in (GENESIS_MODULE, GENESIS_SCRIPT):
        for line_no, line in enumerate(_code(path).splitlines(), 1):
            if _CREDENTIAL_LITERAL.search(line):
                offenders.append(f"{path.name}:{line_no}: {line.strip()}")
    assert offenders == [], (
        f"the genesis path embeds a credential literal: {offenders}"
    )


def test_the_genesis_procedure_takes_a_hash_and_never_defaults_it():
    """The credential arrives already hashed and has no default, so no
    plaintext production credential passes through the governed module and an
    omitted credential is a refusal rather than a fallback."""
    args = _execute_signature()
    named = [a.arg for a in (args.posonlyargs + args.args + args.kwonlyargs)]
    assert "password_hash" in named, (
        "the genesis procedure does not take a pre-hashed credential"
    )
    assert "password" not in named, (
        "the genesis procedure takes a plaintext credential"
    )
    assert all(d is None for d in args.kw_defaults), (
        "a genesis parameter has a default value; the credential and the "
        "identity must both be supplied deliberately"
    )
    assert args.defaults == [], "a genesis parameter has a default value"


# ---------------------------------------------------------------------------
# §5 — the single-use property lives in durable state
# ---------------------------------------------------------------------------

def test_the_single_use_property_is_enforced_by_the_schema():
    """§5: *"The single-use property must be enforced by durable production
    state, not by operator memory or documentation alone."*

    Asserted against the migration, not the service. A property enforced only
    by the function everybody is asked to use is not a property of the system;
    it is a convention, and the ruling explicitly declines to rely on one.
    """
    sql = _code(MIGRATION)
    assert re.search(r"CREATE TABLE[^;]*platform_admin_genesis", sql, re.I), (
        "the genesis consumption record is not created by a migration"
    )
    assert re.search(r"singleton\s+BOOLEAN\s+PRIMARY KEY", sql, re.I), (
        "the consumption record can hold more than one row, so the authority "
        "can be consumed more than once"
    )
    assert re.search(
        r"CHECK\s*\(\s*granted_role\s*=\s*'platform_admin'\s*\)", sql, re.I
    ), "the consumption record can describe a role the ruling does not authorize"
    assert re.search(
        r"CREATE UNIQUE INDEX[^;]*provenance\s*=\s*'GENESIS'", sql, re.I | re.S
    ), "more than one identity may carry GENESIS provenance"


def test_the_migration_creates_no_identity_and_consumes_nothing():
    """§8: PRODUCTION_GENESIS_EXECUTION=NOT_AUTHORIZED_BY_THIS_RULING.

    Applying the chain establishes the shape. It must not BE the act — a
    migration that inserted the administrator would execute the production
    genesis write the moment somebody ran the schema phase of the P1 runbook.
    """
    offenders = _IDENTITY_INSERT.findall(_code(MIGRATION))
    assert offenders == [], (
        f"the genesis migration performs the genesis act itself: {offenders}"
    )


def test_the_ruling_is_recorded_in_governance():
    """The counterpart to every prohibition above. A mechanism whose authority
    is cited only in source comments is a mechanism whose authority cannot be
    checked against the register."""
    governance = ROOT / "petcare_execution" / "GOVERNANCE"
    recorded = [
        p for p in governance.rglob("*.md")
        if "GENESIS_AUTHORITY=SINGLE_USE"
        in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert recorded, "the genesis ruling is not recorded in any governance document"


# ---------------------------------------------------------------------------
# Meta-tests — every guard above must be shown to fire
# ---------------------------------------------------------------------------

def test_meta_a_role_parameter_would_be_detected(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text(
        "class PlatformAdminGenesisService:\n"
        "    def execute(self, *, user_id: str, role: str) -> None: ...\n",
        encoding="utf-8",
    )
    tree = ast.parse(planted.read_text(encoding="utf-8"))
    args = [
        item.args for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
        for item in node.body
        if isinstance(item, ast.FunctionDef) and item.name == "execute"
    ][0]
    names = [a.arg for a in args.args + args.kwonlyargs]
    assert [n for n in names if "role" in n.lower()] == ["role"]


def test_meta_a_credential_literal_would_be_detected():
    assert _CREDENTIAL_LITERAL.search('password = "PetCare2026!"')
    assert _CREDENTIAL_LITERAL.search("DEFAULT_ADMIN_SECRET: 'changeme123'")
    # And must NOT fire on the parameter the procedure legitimately takes.
    assert not _CREDENTIAL_LITERAL.search(
        "def execute(self, *, password_hash: str) -> None:"
    )


def test_meta_an_identity_insert_in_the_migration_would_be_detected():
    planted = (
        "CREATE TABLE platform_admin_genesis (singleton BOOLEAN PRIMARY KEY);\n"
        "INSERT INTO user_identity (user_id, role) VALUES ('u-1', 'platform_admin');\n"
    )
    assert _IDENTITY_INSERT.findall(planted) == ["user_identity"]


def test_meta_an_elevation_statement_would_be_detected():
    for planted in ("UPDATE user_identity SET role = 'platform_admin'",
                    "ON CONFLICT (user_id) DO UPDATE",
                    "self._persistence.identities.upsert(identity)"):
        assert _ELEVATION.findall(planted), (
            f"the elevation guard is blind to {planted!r}"
        )


def test_meta_the_comment_stripper_keeps_statements(tmp_path):
    """The real files explain at length what they decline to do. The stripper
    must remove the explanation and keep the code — a stripper that removed
    both would make every guard above vacuous."""
    planted = tmp_path / "planted.sql"
    planted.write_text(
        "-- INSERT INTO user_identity would be the genesis act itself.\n"
        "CREATE TABLE platform_admin_genesis (singleton BOOLEAN PRIMARY KEY);\n",
        encoding="utf-8",
    )
    code = _code(planted)
    assert "INSERT INTO user_identity" not in code
    assert "CREATE TABLE platform_admin_genesis" in code
