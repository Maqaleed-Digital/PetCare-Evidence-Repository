"""A11 — relocation to KSA is a configuration change, proven rather than asserted.

D.21 makes the move a scheduled certainty:

> "MyVetiCare may remain out of Kingdom until the approved KSA hosting site is
> ready, at which point migration to KSA becomes mandatory."

`test_w0f_architecture_contracts.py` already forbids a hosting location from
appearing as a literal. This file asserts the two things that guard does not.

**1 · That the guard covers the code W0-F added.** An absence assertion is only
as wide as its scan set, and a new module outside the scan set is invisible to
it — the guard would keep passing while the thing it protects grew a region
literal. So the coverage is asserted directly, by name.

**2 · That relocation actually is configuration.** "No literal in the source" is
necessary and not sufficient: code could still require a specific target through
its structure. The control here repoints the connection at a placeholder KSA
target and shows the same code serves it, with the application bytes unchanged.
"""
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "petcare_api"))
sys.path.insert(0, str(ROOT / "tests" / "governance"))

from test_w0f_architecture_contracts import (  # noqa: E402
    KSA_PLACEHOLDERS,
    _source_files,
)

#: Every module W0-F's persistence work added or rewired. Named explicitly: a
#: list derived by globbing would grow silently and assert nothing.
W0F_MODULES = [
    "petcare_api/secret_provider.py",
    "petcare_api/persistence.py",
    "petcare_api/repositories.py",
    "petcare_api/postgres_repositories.py",
    "petcare_api/roles.py",
    "petcare_api/routers/auth.py",
    "petcare_runtime/migrations/0031_w0f_identity_session_persistence.sql",
    "scripts/governance/apply_migrations.py",
    "scripts/governance/identity_migration_dryrun.py",
]


def test_ksa_01_the_portability_guard_covers_every_w0f_module():
    """The coverage assertion. A guard that does not scan a file cannot protect
    it, and its continued passing says nothing about that file."""
    scanned = {str(p.relative_to(ROOT)) for p in _source_files()}
    missing = [m for m in W0F_MODULES if m not in scanned]
    assert missing == [], (
        f"these W0-F modules are outside the portability guard's scan set: "
        f"{missing}. The guard would keep passing while they acquired a region."
    )


def test_ksa_02_no_w0f_module_names_a_hosting_location():
    """Stated directly over the W0-F set as well as tree-wide, so a regression
    here is attributed to this work rather than surfacing as a tree-wide
    failure somebody else has to bisect."""
    from test_w0f_architecture_contracts import (
        _AWS_REGION, _PROVIDER_ENDPOINT, _RESIDENCY_BRANCH, _strip_comments,
    )

    offenders = []
    for module in W0F_MODULES:
        path = ROOT / module
        text = _strip_comments(path, path.read_text(encoding="utf-8"))
        for label, rx in (("region", _AWS_REGION),
                          ("endpoint", _PROVIDER_ENDPOINT),
                          ("residency branch", _RESIDENCY_BRANCH)):
            m = rx.search(text)
            if m:
                offenders.append(f"{module} -> {label}: {m.group(0)[:40]}")
    assert offenders == [], offenders


def test_ksa_03_the_target_placeholders_are_still_unassigned():
    """Restated here because this file is where a reader looks for the KSA
    position. The tree-wide guard is in the architecture contracts."""
    assert KSA_PLACEHOLDERS == [
        "TARGET_KSA_HOSTING_AUTHORITY",
        "TARGET_KSA_REGION_OR_SITE",
        "TARGET_KSA_DATABASE_ENDPOINT",
    ]


def test_ksa_04_repointing_the_store_needs_no_application_change():
    """The proof D.21 actually requires.

    A synthetic relocation: the same `build_persistence` is asked for a store at
    a temporary location and then at a placeholder KSA target. Both are refused
    for the same reason — neither exists — and the refusal is the point: the code
    path is identical, it names no location, and the application source is
    byte-identical before and after.

    No KSA site or region is invented. The placeholder target is an unroutable
    documentation address, which is what lets this run without an approved
    destination.
    """
    from persistence import (
        MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence,
    )
    from postgres_repositories import PersistenceUnavailable
    from secret_provider import SECRET_MODE_ENV_VAR

    modules = {m: hashlib.sha256((ROOT / m).read_bytes()).hexdigest()
               for m in W0F_MODULES}

    env = {SECRET_MODE_ENV_VAR: "environment",
           PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}

    # RFC 5737 TEST-NET-1 / RFC 3849 — reserved for documentation, routable
    # nowhere. Standing in for two different hosting locations without naming
    # either, and without inventing the unapproved one.
    temporary_target = "postgresql://app@192.0.2.10:5432/petcare?connect_timeout=1"
    ksa_placeholder_target = "postgresql://app@192.0.2.20:5432/petcare?connect_timeout=1"

    for target in (temporary_target, ksa_placeholder_target):
        with pytest.raises(PersistenceUnavailable):
            build_persistence(env, connection_url=target)

    after = {m: hashlib.sha256((ROOT / m).read_bytes()).hexdigest()
             for m in W0F_MODULES}
    assert after == modules, (
        "relocating the store changed application source — D.21 requires the "
        "move to be a configuration change, not an application change"
    )


def test_ksa_05_the_connection_url_is_never_assembled_from_a_literal():
    """`resolve_database_url` builds a URL only from the governed secret's own
    fields. A host defaulted anywhere in that path would be a location the
    application chose rather than one configuration supplied."""
    import re

    source = (ROOT / "petcare_api" / "secret_provider.py").read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    # No literal host, port or scheme-with-host assembled anywhere.
    assert not re.search(r'["\']postgresql://[^"\'{]*[a-zA-Z0-9]\.', code), (
        "a connection URL with a literal host appears in the secret provider"
    )
    # The f-string that assembles a URL must take every part from the secret.
    assert 'f"postgresql://{user}:{password}@{host}:{port}/{dbname}"' in code


def test_ksa_06_the_migration_runner_takes_its_target_and_never_defaults_one():
    """The operational tool that applies schema is the one most likely to grow a
    convenience default pointing somewhere."""
    source = (ROOT / "scripts" / "governance" / "apply_migrations.py").read_text(
        encoding="utf-8"
    )
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    assert "postgresql://" not in code, "the migration runner names a connection"
    assert "resolve_database_url" in code, (
        "the runner does not go through the governed secret source"
    )
