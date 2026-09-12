"""MIG-01..06, 09 — the identity migration's mapping invariants.

`MVC-W0F-IDENTITY-MIGRATION-PLAN-001` §5 names this file as the guard for the two
role invariants, and the rest of the plan's rules are asserted alongside them
because they fail the same way: silently, and invisibly afterwards.

That is the thread running through every control here. A migration that infers a
value produces a row indistinguishable from a verified one — nobody looking at
the target later can tell which identities were migrated and which were
reconstructed. So each control below asserts that an unmappable record is HELD,
not that it is handled.

The PostgreSQL-dependent controls (MIG-07, MIG-08, MIG-10) live in
`petcare_api/tests/test_identity_migration_postgres.py`, next to the ephemeral
database fixtures.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))
sys.path.insert(0, str(ROOT / "petcare_api"))

from identity_migration_dryrun import (  # noqa: E402
    ROLE_MAP,
    UNRESOLVED_DUPLICATE,
    UNRESOLVED_MALFORMED_RECORD,
    UNRESOLVED_NO_TENANT,
    UNRESOLVED_UNKNOWN_ROLE,
    UNRESOLVED_UNKNOWN_TENANT,
    SourceRecord,
    classify_password_hash,
    plan_migration,
)
from roles import VALID_ROLES, is_privilege_elevation, privilege_rank  # noqa: E402

SCRYPT = "scrypt$16384$8$1$" + "ab" * 16 + "$" + "cd" * 32


def _rec(**over) -> SourceRecord:
    base = dict(source_record_id="src-1", user_id="u-1", email="a@example.test",
                password_hash=SCRYPT, role="owner", tenant_id="t-1",
                full_name="A")
    base.update(over)
    return SourceRecord(**base)


def _reasons(quarantined) -> list[str]:
    return [q.reason for q in quarantined]


# ---------------------------------------------------------------------------
# Positive control
# ---------------------------------------------------------------------------

def test_positive_control_a_complete_record_migrates():
    """Without this, a planner that quarantined everything would satisfy every
    negative control in this file — and the live source currently DOES quarantine
    everything, so the risk is not hypothetical."""
    migratable, quarantined, recon = plan_migration([_rec()], tenant_map=None)
    assert len(migratable) == 1 and quarantined == []
    assert recon.migratable_count == 1
    assert all(recon.checks.values())


# ---------------------------------------------------------------------------
# MIG-01 / MIG-02 / MIG-03 — roles
# ---------------------------------------------------------------------------

def test_mig_01_every_known_role_maps_to_exactly_itself():
    """Identity-preserving by construction.

    It looks like a no-op and is the point: the estate mints two vocabularies for
    the same roles (CONF-01), and a migration that normalised them would change
    which identities `require_role()` accepts. Changing who may act is a Sponsor
    product decision, and a migration is the worst place to take one.
    """
    assert set(ROLE_MAP) == set(VALID_ROLES)
    for source, target in ROLE_MAP.items():
        assert source == target, f"the role map rewrites {source!r} to {target!r}"


def test_mig_01b_every_known_role_actually_migrates():
    for i, role in enumerate(sorted(VALID_ROLES)):
        migratable, quarantined, _ = plan_migration([
            _rec(source_record_id=f"s-{i}", user_id=f"u-{i}",
                 email=f"r{i}@example.test", role=role)
        ], tenant_map=None)
        assert quarantined == [], f"a catalogue role was quarantined: {role!r}"
        assert migratable[0].role == role


@pytest.mark.parametrize("role", ["superuser", "admin", "", None, "OWNER", 7])
def test_mig_02_an_unknown_role_is_quarantined_never_guessed(role):
    migratable, quarantined, _ = plan_migration([_rec(role=role)], tenant_map=None)
    assert migratable == []
    assert _reasons(quarantined) == [UNRESOLVED_UNKNOWN_ROLE]


def test_mig_02b_the_retired_role_is_quarantined_without_being_named():
    """Derived, not typed: `scripts` is a live source tree under
    MVC-RETIRED-ROLE-CUSTODY-001, and a test that named the value would need an
    exemption indistinguishable from the defect."""
    from petcare.auth import access_control

    defined = {
        getattr(access_control, n) for n in dir(access_control)
        if n.startswith("ROLE_") and isinstance(getattr(access_control, n), str)
    }
    not_admitted = sorted(defined - set(VALID_ROLES))
    assert not_admitted, "nothing outside the catalogue; this would test nothing"
    for role in not_admitted:
        migratable, quarantined, _ = plan_migration([_rec(role=role)], tenant_map=None)
        assert migratable == []
        assert _reasons(quarantined) == [UNRESOLVED_UNKNOWN_ROLE]


def test_mig_03_no_mapping_in_the_table_increases_privilege():
    """The invariant, checked against the table itself rather than against a
    sample. A promotion introduced by editing the map would be invisible
    afterwards: the target would show the elevated role as though always held."""
    for source, target in ROLE_MAP.items():
        assert not is_privilege_elevation(source_role=source, target_role=target)


def test_mig_03b_an_elevating_map_would_be_refused(monkeypatch):
    """Armed. The map is identity-preserving, so the guard can only be shown to
    bite by perturbing the map — otherwise it asserts nothing that could fail."""
    import identity_migration_dryrun as tool

    highest = max(VALID_ROLES, key=privilege_rank)
    lowest = min(VALID_ROLES, key=privilege_rank)
    assert privilege_rank(highest) > privilege_rank(lowest)

    monkeypatch.setattr(tool, "ROLE_MAP", {**ROLE_MAP, lowest: highest})
    migratable, quarantined, _ = tool.plan_migration([_rec(role=lowest)], tenant_map=None)
    assert migratable == [], "a privilege elevation was allowed through the map"
    assert _reasons(quarantined) == [UNRESOLVED_UNKNOWN_ROLE]


def test_mig_03c_privilege_rank_refuses_to_answer_for_an_unknown_role():
    """An unknown role has no rank and is never given one. Defaulting it to the
    lowest would make an unrecognised role look safe."""
    with pytest.raises(ValueError):
        privilege_rank("superuser")
    assert is_privilege_elevation(source_role="superuser", target_role="owner")
    assert is_privilege_elevation(source_role="owner", target_role="superuser")


# ---------------------------------------------------------------------------
# MIG-04 / MIG-05 — tenants
# ---------------------------------------------------------------------------

def test_mig_04_an_unknown_tenant_is_quarantined_when_a_map_is_supplied():
    migratable, quarantined, _ = plan_migration(
        [_rec(tenant_id="t-unknown")], tenant_map={"t-1": "t-1"}
    )
    assert migratable == []
    assert _reasons(quarantined) == [UNRESOLVED_UNKNOWN_TENANT]


def test_mig_04b_a_mapped_tenant_is_translated_exactly():
    migratable, _, _ = plan_migration(
        [_rec(tenant_id="old-t")], tenant_map={"old-t": "new-t"}
    )
    assert migratable[0].tenant_id == "new-t"


def test_mig_04c_no_map_means_copied_verbatim_never_inferred():
    """The plan's §4 rule. The absence of a map is not "any tenant is fine" — it
    is "tenants are copied", which is what §4 requires."""
    migratable, _, _ = plan_migration([_rec(tenant_id="t-verbatim")], tenant_map=None)
    assert migratable[0].tenant_id == "t-verbatim"


@pytest.mark.parametrize("tenant", [None, "", "   "])
def test_mig_05_a_record_with_no_tenant_is_quarantined_never_assigned(tenant):
    """Plan §4: an identity whose tenant is absent is NOT given one by proximity,
    by role, or by any other signal."""
    migratable, quarantined, _ = plan_migration([_rec(tenant_id=tenant)], tenant_map=None)
    assert migratable == []
    assert _reasons(quarantined) == [UNRESOLVED_NO_TENANT]


def test_mig_05b_no_migrated_record_can_lack_a_tenant():
    """The reconciliation check, over a mixed set."""
    _, _, recon = plan_migration([
        _rec(source_record_id="s1", user_id="u1", email="a@x.test", tenant_id="t"),
        _rec(source_record_id="s2", user_id="u2", email="b@x.test", tenant_id=None),
    ], tenant_map=None)
    assert recon.checks["no_migrated_row_without_tenant"] is True
    assert recon.migratable_count == 1
    assert recon.quarantined_count == 1


# ---------------------------------------------------------------------------
# MIG-06 — duplicates
# ---------------------------------------------------------------------------

def test_mig_06_a_duplicate_email_quarantines_every_side():
    """Not "the later one". Keeping the first, or the most recent, is a guess
    about which identity is real — and the survivor would be indistinguishable
    from an uncontested record."""
    migratable, quarantined, recon = plan_migration([
        _rec(source_record_id="s1", user_id="u1", email="dup@example.test"),
        _rec(source_record_id="s2", user_id="u2", email="dup@example.test"),
    ], tenant_map=None)
    assert migratable == []
    assert _reasons(quarantined) == [UNRESOLVED_DUPLICATE, UNRESOLVED_DUPLICATE]
    assert recon.duplicate_emails == ["dup@example.test"]


def test_mig_06b_case_differing_addresses_are_the_same_login():
    """`A@x` and `a@x` are one login. Migrating them as two identities would
    create an account whose owner can sign into whichever the store matched."""
    migratable, quarantined, _ = plan_migration([
        _rec(source_record_id="s1", user_id="u1", email="Dup@Example.test"),
        _rec(source_record_id="s2", user_id="u2", email="dup@example.test"),
    ], tenant_map=None)
    assert migratable == []
    assert _reasons(quarantined) == [UNRESOLVED_DUPLICATE, UNRESOLVED_DUPLICATE]


def test_mig_06c_the_stored_address_keeps_its_original_form():
    """Normalisation is for COMPARISON only. Rewriting a stored identifier would
    silently change what users type, and afterwards the change is
    indistinguishable from the address always having been different."""
    migratable, _, _ = plan_migration([_rec(email="Mixed.Case@Example.test")], tenant_map=None)
    assert migratable[0].email == "Mixed.Case@Example.test"


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def test_a_governed_scrypt_hash_is_carried_unchanged():
    migratable, _, _ = plan_migration([_rec()], tenant_map=None)
    assert migratable[0].password_hash == SCRYPT
    assert migratable[0].hash_format == "GOVERNED"


def test_a_legacy_hash_is_carried_and_marked_for_upgrade_on_login():
    """Plan §7: hashes move as opaque strings, and W0-J's rehash-on-next-login
    handles any legacy format that survives — at the one moment the plaintext is
    legitimately available."""
    legacy = "a" * 64
    migratable, _, _ = plan_migration([_rec(password_hash=legacy)], tenant_map=None)
    assert migratable[0].hash_format == "LEGACY_UPGRADES_ON_LOGIN"


@pytest.mark.parametrize("value", ["", None, "plaintext-password", "notahash", 42])
def test_an_unrecognised_credential_is_quarantined(value):
    """An unrecognisable hash is a credential nobody can verify. Migrating it
    produces an account that can never be signed into and never be told why —
    and, if it is a plaintext password, one that must never be stored."""
    migratable, quarantined, _ = plan_migration([_rec(password_hash=value)], tenant_map=None)
    assert migratable == []
    assert _reasons(quarantined) == [UNRESOLVED_MALFORMED_RECORD]


def test_the_migration_never_holds_a_plaintext_password():
    """Plan §7 invariant. Anything not matching a known hash format is held, so
    a plaintext value cannot reach the migratable set."""
    _, _, recon = plan_migration([_rec(password_hash="hunter2")], tenant_map=None)
    assert recon.checks["no_plaintext_password_present"] is True
    assert classify_password_hash("hunter2") is None


@pytest.mark.parametrize("missing", ["user_id", "full_name", "email"])
def test_an_incomplete_record_is_quarantined_not_repaired(missing):
    migratable, quarantined, _ = plan_migration([_rec(**{missing: None})], tenant_map=None)
    assert migratable == []
    assert _reasons(quarantined) == [UNRESOLVED_MALFORMED_RECORD]


# ---------------------------------------------------------------------------
# MIG-09 — determinism
# ---------------------------------------------------------------------------

def test_mig_09_a_second_dry_run_produces_an_identical_result():
    """A planner whose output varied between runs could not be reviewed: the
    quarantine set a Sponsor approved would not be the set that was applied."""
    records = [
        _rec(source_record_id="s1", user_id="u1", email="a@x.test"),
        _rec(source_record_id="s2", user_id="u2", email="b@x.test", tenant_id=None),
        _rec(source_record_id="s3", user_id="u3", email="c@x.test", role="nope"),
        _rec(source_record_id="s4", user_id="u4", email="d@x.test"),
        _rec(source_record_id="s5", user_id="u5", email="d@x.test"),
    ]
    first = plan_migration(records, tenant_map=None)
    second = plan_migration(records, tenant_map=None)
    assert first[0] == second[0]
    assert first[1] == second[1]
    assert first[2].checks == second[2].checks
    assert first[2].quarantine_reasons == second[2].quarantine_reasons


def test_counts_always_account_for_every_source_record():
    records = [
        _rec(source_record_id=f"s{i}", user_id=f"u{i}", email=f"{i}@x.test",
             tenant_id=None if i % 2 else "t-1")
        for i in range(10)
    ]
    migratable, quarantined, recon = plan_migration(records, tenant_map=None)
    assert recon.source_count == 10
    assert recon.migratable_count + recon.quarantined_count == 10
    assert recon.checks["no_row_lost"] is True
    assert recon.checks["no_row_invented"] is True
