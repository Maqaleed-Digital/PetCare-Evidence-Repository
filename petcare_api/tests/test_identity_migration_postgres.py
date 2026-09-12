"""MIG-07, MIG-08, MIG-10 — the identity migration against real PostgreSQL.

The mapping invariants are asserted in
`tests/governance/test_identity_migration_contracts.py`. These three cannot be:
each is a claim about what reaches a database, and a claim about writes cannot be
proven without one.

`MIG-07` is the one that matters most. "Dry run" is a promise that nothing was
written, and the only way to keep that promise honestly is to look afterwards.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(ROOT / "scripts" / "governance"))

psycopg = pytest.importorskip("psycopg")
from psycopg import errors as pgerrors  # noqa: E402

import identity_migration_dryrun as tool  # noqa: E402
from pg_harness import create_database, drop_database, replay_migrations  # noqa: E402

SCRYPT = "scrypt$16384$8$1$" + "ab" * 16 + "$" + "cd" * 32


def _rec(**over) -> tool.SourceRecord:
    base = dict(source_record_id="src-1", user_id="u-1", email="a@example.test",
                password_hash=SCRYPT, role="owner", tenant_id="t-1", full_name="A")
    base.update(over)
    return tool.SourceRecord(**base)


MIXED_SOURCE = [
    _rec(source_record_id="s1", user_id="u1", email="ok1@x.test"),
    _rec(source_record_id="s2", user_id="u2", email="ok2@x.test", role="veterinarian"),
    _rec(source_record_id="s3", user_id="u3", email="no-tenant@x.test", tenant_id=None),
    _rec(source_record_id="s4", user_id="u4", email="bad-role@x.test", role="wizard"),
    _rec(source_record_id="s5", user_id="u5", email="dup@x.test"),
    _rec(source_record_id="s6", user_id="u6", email="DUP@x.test"),
    _rec(source_record_id="s7", user_id="u7", email="bad-hash@x.test",
         password_hash="not-a-hash"),
]
EXPECTED_MIGRATABLE = 2
EXPECTED_QUARANTINED = 5


def _provision_tenants(url: str, *tenant_ids: str) -> None:
    """TENANT-10: migrating a real identity requires explicit tenant authority.

    The migration tool does NOT create tenants — `apply_to` writes identities and
    nothing else, so a source record naming an unknown tenant now fails on the
    foreign key rather than quietly creating a scope. These fixtures therefore
    supply the tenant the way a governed cutover would: deliberately, before the
    migration runs.
    """
    with psycopg.connect(url, autocommit=True) as conn:
        for tid in tenant_ids:
            conn.execute(
                "INSERT INTO tenant (tenant_id, display_name) VALUES (%s, %s) "
                "ON CONFLICT (tenant_id) DO NOTHING",
                (tid, f"Fixture {tid}"),
            )


def _counts(url: str) -> tuple[int, int]:
    with psycopg.connect(url) as conn:
        identities = conn.execute("SELECT count(*) FROM user_identity").fetchone()[0]
        held = conn.execute(
            "SELECT count(*) FROM identity_migration_quarantine"
        ).fetchone()[0]
    return identities, held


def test_positive_control_the_fixture_source_is_not_all_quarantine():
    """Without this, MIG-08's counts could be satisfied by a planner that
    migrated nothing — which is what the LIVE source currently produces."""
    migratable, quarantined, _ = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    assert len(migratable) == EXPECTED_MIGRATABLE
    assert len(quarantined) == EXPECTED_QUARANTINED


# ---------------------------------------------------------------------------
# MIG-07
# ---------------------------------------------------------------------------

def test_mig_07_a_dry_run_writes_zero_rows(clean_postgres):
    """Checked by looking at the database, not by trusting the code path.

    `plan_migration` is pure by construction, but "the function does not write"
    is exactly the kind of claim that survives a refactor which makes it false.
    """
    before = _counts(clean_postgres)
    assert before == (0, 0)
    tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    assert _counts(clean_postgres) == (0, 0), "a dry run wrote to the database"


def test_mig_07b_the_cli_refuses_to_apply_without_an_explicit_target(capsys):
    """A tool that could find production by reading the same configuration the
    application reads is one flag away from writing to it."""
    rc = tool.main(["--apply"])
    assert rc == 2
    assert "APPLY_REFUSED" in capsys.readouterr().err


def test_mig_07c_the_cli_dry_run_writes_nothing_and_reports_counts(
    clean_postgres, tmp_path
):
    source = tmp_path / "source.json"
    source.write_text(
        __import__("json").dumps([
            {"source_record_id": r.source_record_id, "user_id": r.user_id,
             "email": r.email, "password_hash": r.password_hash, "role": r.role,
             "tenant_id": r.tenant_id, "full_name": r.full_name}
            for r in MIXED_SOURCE
        ]),
        encoding="utf-8",
    )
    report = tmp_path / "report.md"
    rc = tool.main(["--source-json", str(source), "--report", str(report)])
    assert rc == 0
    text = report.read_text()
    assert f"IDENTITY_SOURCE_COUNT={len(MIXED_SOURCE)}" in text
    assert f"IDENTITY_MIGRATABLE_COUNT={EXPECTED_MIGRATABLE}" in text
    assert f"IDENTITY_QUARANTINED_COUNT={EXPECTED_QUARANTINED}" in text
    assert "dry run — zero authoritative rows written" in text
    assert _counts(clean_postgres) == (0, 0)


def test_mig_07d_the_report_never_contains_credential_material(tmp_path):
    """The report is reviewed by a human and stored as evidence. A password hash
    in it would put credential material into an artefact nobody treats as one."""
    migratable, quarantined, recon = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    report = tool.render_report(recon, migratable, quarantined, applied=None)
    assert SCRYPT not in report
    assert "password_hash" not in report


# ---------------------------------------------------------------------------
# MIG-08
# ---------------------------------------------------------------------------

def test_mig_08_applying_to_an_ephemeral_database_produces_the_expected_counts(
    clean_postgres,
):
    migratable, quarantined, recon = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    assert all(recon.checks.values())
    _provision_tenants(clean_postgres, "t-1")
    result = tool.apply_to(clean_postgres, migratable, quarantined)
    assert result == {"identities_written": EXPECTED_MIGRATABLE,
                      "quarantine_written": EXPECTED_QUARANTINED}
    assert _counts(clean_postgres) == (EXPECTED_MIGRATABLE, EXPECTED_QUARANTINED)


def test_mig_08b_every_written_identity_carries_its_provenance_and_source(
    clean_postgres,
):
    """Without both, a migrated row cannot be reconciled against anything — which
    is the same defect as an invented row."""
    migratable, quarantined, _ = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    _provision_tenants(clean_postgres, "t-1")
    tool.apply_to(clean_postgres, migratable, quarantined)
    with psycopg.connect(clean_postgres) as conn:
        rows = conn.execute(
            "SELECT provenance, source_record_id, tenant_id FROM user_identity"
        ).fetchall()
    assert rows and all(r[0] == "IDENTITY_MIGRATION" for r in rows)
    assert all(r[1] for r in rows)
    assert all(r[2] for r in rows)


def test_mig_08c_a_quarantined_identity_cannot_be_written_as_authoritative(
    clean_postgres,
):
    """The structural half of the rule.

    Even if the tool were changed to write a quarantined record, the database
    refuses it — so the invariant does not depend on this script continuing to
    obey it.
    """
    _, quarantined, _ = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    tenantless = [q for q in quarantined if q.reason == tool.UNRESOLVED_NO_TENANT]
    assert tenantless, "the fixture produced no tenantless record to test with"

    forced = tool.Migratable(
        source_record_id=tenantless[0].source_record_id, user_id="u-forced",
        email="forced@x.test", password_hash=SCRYPT, role="owner",
        tenant_id="", full_name="Forced", hash_format="GOVERNED",
    )
    with pytest.raises(pgerrors.Error):
        tool.apply_to(clean_postgres, [forced], [])
    assert _counts(clean_postgres)[0] == 0


def test_mig_08d_the_quarantine_records_the_reason_and_the_source_values(
    clean_postgres,
):
    _, quarantined, _ = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    tool.apply_to(clean_postgres, [], quarantined)
    with psycopg.connect(clean_postgres) as conn:
        rows = dict(conn.execute(
            "SELECT reason, count(*) FROM identity_migration_quarantine "
            "GROUP BY reason"
        ).fetchall())
    assert rows == {
        tool.UNRESOLVED_NO_TENANT: 1,
        tool.UNRESOLVED_UNKNOWN_ROLE: 1,
        tool.UNRESOLVED_DUPLICATE: 2,
        tool.UNRESOLVED_MALFORMED_RECORD: 1,
    }


def test_mig_08e_a_second_apply_does_not_silently_overwrite(clean_postgres):
    """MIG-06's structural half. Re-running an apply must not quietly replace
    identities — the UNIQUE constraint is what actually prevents it."""
    migratable, quarantined, _ = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
    _provision_tenants(clean_postgres, "t-1")
    tool.apply_to(clean_postgres, migratable, quarantined)
    with pytest.raises(pgerrors.UniqueViolation):
        tool.apply_to(clean_postgres, migratable, quarantined)
    assert _counts(clean_postgres) == (EXPECTED_MIGRATABLE, EXPECTED_QUARANTINED)


# ---------------------------------------------------------------------------
# MIG-10
# ---------------------------------------------------------------------------

def test_mig_10_rollback_recreate_reapply_reconciles(postgres_admin_url):
    """The rehearsal AC-9 requires, against a RESTORE rather than a backup.

    The target is destroyed and rebuilt by replaying the chain — not cloned —
    because `MVC-W0F-KSA-MIGRATION-READINESS-001` §2 says the chain is the
    canonical definition and a clone would carry whatever drift the source had
    accumulated.
    """
    name = "petcare_mig_rehearsal"
    url = create_database(postgres_admin_url, name)
    try:
        replay_migrations(url)
        _provision_tenants(url, "t-1")
        migratable, quarantined, recon = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
        first = tool.apply_to(url, migratable, quarantined)
        first_counts = _counts(url)
        assert first_counts == (EXPECTED_MIGRATABLE, EXPECTED_QUARANTINED)

        # Rollback: the whole target, rebuilt from the chain.
        drop_database(postgres_admin_url, name)
        url = create_database(postgres_admin_url, name)
        replay_migrations(url)
        _provision_tenants(url, "t-1")
        assert _counts(url) == (0, 0), "the rebuilt target was not empty"

        migratable2, quarantined2, recon2 = tool.plan_migration(MIXED_SOURCE, tenant_map=None)
        second = tool.apply_to(url, migratable2, quarantined2)

        assert second == first, "reapplying produced different counts"
        assert _counts(url) == first_counts
        assert recon2.checks == recon.checks
        assert recon2.quarantine_reasons == recon.quarantine_reasons
    finally:
        drop_database(postgres_admin_url, name)


def test_mig_10b_the_reconciliation_checks_gate_the_apply(clean_postgres, capsys,
                                                          tmp_path, monkeypatch):
    """`--apply` refuses when reconciliation fails.

    Armed by perturbing a check to fail, so the refusal is shown to depend on the
    checks rather than on nothing.
    """
    import json as _json

    source = tmp_path / "s.json"
    source.write_text(_json.dumps([
        {"source_record_id": "s1", "user_id": "u1", "email": "a@x.test",
         "password_hash": SCRYPT, "role": "owner", "tenant_id": "t-1",
         "full_name": "A"}
    ]), encoding="utf-8")

    real = tool.reconcile
    monkeypatch.setattr(
        tool, "reconcile",
        lambda *a, **k: {**real(*a, **k), "no_row_lost": False},
    )
    rc = tool.main(["--source-json", str(source), "--apply",
                    "--database-url", clean_postgres])
    assert rc == 2
    assert "APPLY_REFUSED" in capsys.readouterr().err
    assert _counts(clean_postgres) == (0, 0)
