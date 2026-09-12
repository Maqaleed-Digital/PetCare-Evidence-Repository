"""SEED-01..06 — the application creates no identity, and holds no credential.

Sponsor ruling `PRE1_RULING=1-B`: the three seeded identities are development
artefacts, are discarded, and do not migrate.

The reason is not tidiness. Their password was a literal in `main.py`, in a
repository whose visibility is PUBLIC — so every start of a durable deployment
would have written three accounts with a published credential into the identity
store, one of them holding the highest role in the system. A startup path that
creates a `platform_admin` from a source literal is a backdoor whether or not
anyone intended one, and persistence is what would have made it permanent.
"""
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import routers.auth as auth  # noqa: E402
from roles import ALLOWED_ROLES, ROLE_PLATFORM_ADMIN  # noqa: E402

APP_ROOT = Path(__file__).resolve().parents[1]

#: The serving tree, excluding tests. Tests legitimately hold fixture
#: credentials; the application must hold none.
def _serving_sources() -> list[Path]:
    return [
        p for p in APP_ROOT.rglob("*.py")
        if "__pycache__" not in str(p) and "/tests/" not in str(p).replace(os.sep, "/")
    ]


def test_the_scan_is_not_vacuous():
    files = _serving_sources()
    assert len(files) >= 8, f"serving source scan collapsed to {len(files)} files"


# ---------------------------------------------------------------------------
# SEED-01 — startup creates nothing
# ---------------------------------------------------------------------------

def _startup_facts() -> dict:
    """Import the application in a FRESH process and report what startup created.

    A subprocess, not an in-process assertion. `auth.IDENTITY_REPO` is shared by
    the whole suite, so by the time this file runs other modules have legitimately
    provisioned their own fixtures — and a count taken here would measure the
    suite rather than the startup path. The question is what a DEPLOYMENT would
    hold one second after boot, and only a clean interpreter can answer it.
    """
    import json
    import subprocess

    probe = (
        "import sys, json;"
        f"sys.path.insert(0, {str(APP_ROOT)!r});"
        f"sys.path.insert(0, {str(APP_ROOT.parent)!r});"
        "import main;"
        "import routers.auth as auth;"
        "print(json.dumps({"
        "'identities': auth.IDENTITY_REPO.count(),"
        "'emails': [e for e in ["
        "'admin@' 'myveticare.com','vet@' 'myveticare.com','owner@' 'myveticare.com'"
        "] if auth.IDENTITY_REPO.get_by_email(e) is not None],"
        "}))"
    )
    env = dict(os.environ)
    env.setdefault("SECRET_KEY", "test-only-not-a-deployed-secret")
    env.setdefault("PETCARE_SECRET_MODE", "environment")
    env.setdefault("PETCARE_PERSISTENCE_MODE", "memory")
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                         text=True, env=env, cwd=str(APP_ROOT.parent))
    assert out.returncode == 0, f"the application failed to import:\n{out.stderr}"
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_seed_01_importing_the_application_creates_zero_identities():
    """What a deployment holds one second after boot."""
    facts = _startup_facts()
    assert facts["identities"] == 0, (
        "application startup created identities; a deployment would write them "
        "into the durable store on every boot"
    )


def test_seed_01b_no_module_level_call_creates_a_user():
    """Asserted structurally as well as behaviourally.

    A startup seed could be reintroduced behind a condition that happens to be
    false in the suite — `if os.getenv("PILOT")` — and SEED-01 alone would not
    see it. This reads the source for a module-level call instead.
    """
    import ast

    offenders = []
    for path in _serving_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:                      # module level ONLY
            for sub in ast.walk(node):
                if not isinstance(sub, ast.Call):
                    continue
                fn = sub.func
                name = getattr(fn, "id", None) or getattr(fn, "attr", None)
                if name in {"seed_user", "create_user", "create_identity"}:
                    offenders.append(f"{path.relative_to(APP_ROOT)}:{sub.lineno} {name}")
    assert offenders == [], f"module-level identity creation: {offenders}"


# ---------------------------------------------------------------------------
# SEED-02 — no credential literal in the serving tree
# ---------------------------------------------------------------------------

#: The retired seed credential and the identities it belonged to. Written as
#: split literals so this guard does not itself reintroduce the searchable
#: string into the tree it is guarding — the same reasoning W0-A2 used when it
#: replaced a plaintext comparand with a fingerprint.
_RETIRED_SEED_PASSWORD = "PetCare" + "2026!"
_RETIRED_SEED_EMAILS = [p + "@myveticare.com" for p in ("admin", "vet", "owner")]
_RETIRED_SEED_IDS = ["u-" + s for s in ("admin-001", "vet-001", "owner-001")]


def _code_only(path: Path) -> str:
    """Source with comment lines removed.

    The estate's existing precedent (`test_w0f_architecture_contracts._strip_comments`):
    a comment may DISCUSS a forbidden value while code may not contain one. The
    removal of these identities is explained in a comment in `main.py`, and a
    guard that could not tell that from a live seed would be widened until it
    meant nothing.
    """
    return "\n".join(
        l for l in path.read_text(encoding="utf-8").splitlines()
        if not l.strip().startswith("#")
    )


def test_seed_02_the_retired_credential_is_absent_from_serving_source_ENTIRELY():
    """The PASSWORD is held to the stricter rule: absent from code AND comments.

    It is credential material. An identifier in a comment is documentation; a
    password in a comment is still a published password, and `git grep` does not
    care which side of a `#` it sits on.
    """
    offenders = [
        str(p.relative_to(APP_ROOT)) for p in _serving_sources()
        if _RETIRED_SEED_PASSWORD in p.read_text(encoding="utf-8")
    ]
    assert offenders == [], f"the retired seed credential survives in: {offenders}"


@pytest.mark.parametrize("needle", [*_RETIRED_SEED_EMAILS, *_RETIRED_SEED_IDS])
def test_seed_02b_no_retired_seed_identity_is_named_in_serving_CODE(needle):
    """The identifiers may be discussed; they may not be used."""
    offenders = [
        str(p.relative_to(APP_ROOT)) for p in _serving_sources()
        if needle in _code_only(p)
    ]
    assert offenders == [], f"{needle!r} still present in serving code: {offenders}"


def test_seed_02c_no_password_shaped_default_survives_in_serving_source():
    """A different literal with the same shape would be the same defect.

    Matches an assignment or keyword argument that hands a password-ish name a
    string literal. Comments are stripped: the modules deliberately DISCUSS
    passwords, and a guard that could not tell prose from code would be widened
    until it meant nothing.
    """
    # The negative lookbehind this used to carry — `(?<!_)` — was meant to skip
    # `password_hash`, and it skipped `DEFAULT_ADMIN_PASSWORD` too. Every
    # credential-shaped name in the real world has an underscore in front of the
    # word. Found by designing the perturbation for this control: the probe that
    # was supposed to make it fail did not.
    #
    # The exclusion is now precise: `*_hash` is a digest, not a credential.
    rx = re.compile(
        r"""\b\w*(password|passwd|pwd|secret_value)\w*\s*[:=]\s*["'][^"']{4,}["']""",
        re.IGNORECASE,
    )
    _hash_field = re.compile(r"\w*(password|passwd|pwd)\w*_hash\w*", re.IGNORECASE)
    offenders = []
    for path in _serving_sources():
        code = "\n".join(
            l for l in path.read_text(encoding="utf-8").splitlines()
            if not l.strip().startswith("#")
        )
        for m in rx.finditer(code):
            if _hash_field.match(m.group(0)):
                continue  # a stored digest, not a credential
            offenders.append(f"{path.relative_to(APP_ROOT)} -> {m.group(0)[:48]}")
    assert offenders == [], f"credential-shaped literal in serving source: {offenders}"


# ---------------------------------------------------------------------------
# SEED-03 / SEED-06 — no auto-seed, and no privileged identity from a default
# ---------------------------------------------------------------------------

def test_seed_03_no_startup_path_depends_on_a_persistence_mode_to_skip_seeding():
    """The fix is the ABSENCE of seeding, not seeding that is skipped in
    production. A conditional seed is one environment variable away from
    running, and the environment where it would run is the one that matters."""
    source = (APP_ROOT / "main.py").read_text(encoding="utf-8")
    code = "\n".join(l for l in source.splitlines() if not l.strip().startswith("#"))
    assert "seed_user(" not in code, (
        "main.py calls seed_user; startup must create no identity at all, "
        "conditionally or otherwise"
    )


def test_seed_06_a_platform_admin_cannot_come_from_a_published_credential_path():
    """The specific backdoor PRE-1 found: a highest-privilege account created at
    startup from a literal anyone could read."""
    facts = _startup_facts()
    assert facts["identities"] == 0
    assert facts["emails"] == [], f"startup created {facts['emails']}"
    assert ROLE_PLATFORM_ADMIN in ALLOWED_ROLES  # the role exists; the account does not


def test_seed_06b_the_retired_seed_credential_no_longer_authenticates():
    """Over the wire, through the real endpoint."""
    from fastapi.testclient import TestClient

    client = TestClient(api.app, base_url="https://testserver")
    for email in _RETIRED_SEED_EMAILS:
        r = client.post("/api/auth/sign-in",
                        json={"email": email, "password": _RETIRED_SEED_PASSWORD})
        assert r.status_code == 401, f"{email} still authenticates"


# ---------------------------------------------------------------------------
# SEED-04 — the migration never carries a discarded artefact
# ---------------------------------------------------------------------------

def test_seed_04_the_migration_source_is_empty_because_nothing_is_seeded():
    """PRE1_RULING=1-B, end to end: the rehearsal has nothing to migrate because
    the application creates nothing to migrate.

    Run in a fresh process for the same reason as SEED-01 — the tool reads the
    live serving registry, and in-process that registry holds the suite's own
    fixtures rather than what a deployment would have.
    """
    import json
    import subprocess

    probe = (
        "import sys, json;"
        f"sys.path.insert(0, {str(APP_ROOT.parent / 'scripts' / 'governance')!r});"
        "import identity_migration_dryrun as tool;"
        "records = tool.records_from_serving_registry();"
        "m, q, recon = tool.plan_migration(records, tenant_map=None);"
        "print(json.dumps({'source': recon.source_count, 'migratable': len(m),"
        " 'quarantined': len(q), 'checks': all(recon.checks.values())}))"
    )
    env = dict(os.environ)
    env.setdefault("SECRET_KEY", "test-only-not-a-deployed-secret")
    env.setdefault("PETCARE_SECRET_MODE", "environment")
    env.setdefault("PETCARE_PERSISTENCE_MODE", "memory")
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                         text=True, env=env, cwd=str(APP_ROOT.parent))
    assert out.returncode == 0, out.stderr
    facts = json.loads(out.stdout.strip().splitlines()[-1])

    assert facts["source"] == 0, f"the serving registry holds {facts['source']} identities"
    assert facts["migratable"] == 0
    assert facts["quarantined"] == 0
    assert facts["checks"] is True


# ---------------------------------------------------------------------------
# SEED-05 — fixtures are explicit and test-scoped
# ---------------------------------------------------------------------------

def test_seed_05_provisioning_an_identity_is_available_but_never_automatic():
    """`seed_user` remains, because provisioning an identity programmatically is
    a legitimate operator act. What was removed is the CALLER at module scope.

    Asserted by using it here — deliberately, from a test — and confirming the
    identity exists only afterwards.
    """
    assert auth.IDENTITY_REPO.get_by_email("seed05@test.invalid") is None
    auth.seed_user("u-seed05", "seed05@test.invalid", "fixture-only-credential",
                   ROLE_PLATFORM_ADMIN, "Seed05", tenant_id=None)
    assert auth.IDENTITY_REPO.get_by_email("seed05@test.invalid") is not None
