"""W0-J — the six migration invariants, enforced in CI.

`MVC-EXEC-001 V1.0 §8`:

```
I-1  audit partition present in the FIRST migration        (already satisfied by A)
I-2  seller identity non-nullable on every commercial record
I-3  no migration destructively deletes anchored evidence
I-4  every migration is reversible, or explicitly recorded irreversible with a
     Sponsor reference
I-5  role catalogue changes only by migration carrying a Sponsor-decision reference
I-6  audit chain columns backfilled with an explicit, recorded decision for
     pre-existing rows
```

CP-2 W0-J `TESTS`: *"CI gate that FAILS on a migration violating any invariant
(prove it can fail)"*. Each invariant below is perturbation-proven.

**I-2 is enforced as staged, not as an immediate NOT NULL.** CP-2's own W0-H
`MIGRATION_DESIGN` sequences it: *additive first -> deterministic classification
where provable -> rows that cannot be classified recorded as UNRESOLVED, never
guessed -> validate -> only then enforce NOT NULL if safe.* A gate demanding NOT
NULL today would fail the migration that CP-2 instructs be written additively,
and would push authors toward guessing values for historical rows — the exact
outcome W0-H forbids. So the gate requires seller identity to be **present and
either enforced or carrying a recorded enforcement plan**, which is what makes
"non-nullable eventually" a checkable claim rather than an aspiration.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "petcare_runtime/migrations"
MIGRATIONS = sorted(MIGRATIONS_DIR.glob("*.sql"))

#: Tables that carry commercial consideration and therefore need a seller.
COMMERCIAL_TABLE = re.compile(
    r"CREATE TABLE(?:\s+IF NOT EXISTS)?\s+(\w*(?:order|invoice|settlement|charge|payment)\w*)",
    re.I,
)
_DESTRUCTIVE = re.compile(r"\b(DROP\s+TABLE|DELETE\s+FROM|TRUNCATE)\b", re.I)
_ANCHORED = re.compile(r"audit|evidence|attestation|ledger|chain", re.I)
_ROLE_CATALOGUE = re.compile(r"\b(role_catalogue|role_catalog|valid_roles|role_definition)\b", re.I)
_SPONSOR_REF = re.compile(r"(Sponsor|CP-2|MVC-[A-Z0-9-]+|GATE_[A-Z_]+)", re.I)
_IRREVERSIBLE = re.compile(r"IRREVERSIBLE", re.I)


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _statements(sql: str) -> str:
    """SQL with comment lines stripped — what the database would actually run."""
    return "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))


def test_migrations_are_scannable():
    assert len(MIGRATIONS) >= 30, f"migration scan collapsed to {len(MIGRATIONS)}"


def test_i1_audit_partition_present_in_the_first_migration():
    """I-1 — auditability cannot be retrofitted. If the audit table is not there
    from the first migration there is a period the estate cannot account for."""
    first = MIGRATIONS[0]
    assert re.search(r"CREATE TABLE\s+audit_event\b", _text(first), re.I), (
        f"the first migration ({first.name}) creates no audit partition"
    )


def test_i2_every_commercial_record_has_seller_identity():
    """I-2, enforced as CP-2 stages it.

    A commercial table with no seller identity at all is the violation. A
    commercial table whose seller identity is additive-and-pending is the
    documented intermediate state, and must carry its enforcement plan.
    """
    all_sql = "\n".join(_text(m) for m in MIGRATIONS)

    # Seller identity is carried ONCE, on the record that bears the
    # consideration, and inherited by rows that reference it. Settlement
    # preparation, review and export are processing stages over an order, not
    # separate sales — duplicating the seller onto each would create several
    # mutable copies of a field REQ-FIN-S1 requires to be immutable.
    #
    # So the rule is structural rather than a list of table-name exceptions: a
    # commercial table must either carry seller identity itself, or reference a
    # record that does. An exclusion list would have to grow with every new
    # table and would eventually hide a real gap.
    missing = []
    for m in COMMERCIAL_TABLE.finditer(all_sql):
        table = m.group(1).lower()
        body_start = m.end()
        body = all_sql[body_start: body_start + 2000]

        touching = [f for f in MIGRATIONS if re.search(rf"\b{re.escape(table)}\b", _text(f), re.I)]
        has_own_seller = any(
            re.search(rf"\b{re.escape(table)}\b[\s\S]{{0,2000}}?seller_id", _text(f), re.I)
            or re.search(rf"ALTER TABLE\s+{re.escape(table)}\s+ADD COLUMN\s+seller_", _text(f), re.I)
            for f in touching
        )
        inherits = bool(re.search(r"\b(order_id|review_id|settlement_preparation_id)\b", body, re.I))

        if not has_own_seller and not inherits:
            missing.append(table)

    assert missing == [], (
        "commercial records that neither carry seller identity nor reference a "
        f"record that does (I-2): {sorted(set(missing))}"
    )


def test_i2b_pending_seller_enforcement_records_its_precondition():
    """The staged form of I-2 is only honest if the final step is written down.
    A NULLable seller column with no recorded enforcement plan is not 'staged',
    it is just absent."""
    offenders = []
    for m in MIGRATIONS:
        sql = _text(m)
        if not re.search(r"ADD COLUMN\s+seller_id", sql, re.I):
            continue
        if "SET NOT NULL" not in sql.upper() or "PRECONDITION" not in sql.upper():
            offenders.append(m.name)
    assert offenders == [], (
        f"seller identity introduced without a recorded enforcement plan (I-2): {offenders}"
    )


def test_i3_no_migration_destructively_deletes_anchored_evidence():
    """I-3 — anchored evidence is the record that other claims rest on. A
    migration that deletes it removes the ability to check the past."""
    offenders = []
    for m in MIGRATIONS:
        stmts = _statements(_text(m))
        for hit in _DESTRUCTIVE.finditer(stmts):
            window = stmts[hit.start(): hit.start() + 200]
            if _ANCHORED.search(window):
                offenders.append(f"{m.name} -> {hit.group(0)} near anchored evidence")
    assert offenders == [], f"destructive statement against anchored evidence (I-3): {offenders}"


def test_i4_irreversible_migrations_are_recorded_with_a_sponsor_reference():
    """I-4 — a migration may be irreversible, but never silently. The record is
    what lets a rollback plan be written before it is needed rather than after."""
    offenders = []
    for m in MIGRATIONS:
        sql = _text(m)
        stmts = _statements(sql)
        irreversible = bool(re.search(r"\b(DROP\s+(TABLE|COLUMN)|TRUNCATE)\b", stmts, re.I))
        if irreversible and not (_IRREVERSIBLE.search(sql) and _SPONSOR_REF.search(sql)):
            offenders.append(m.name)
    assert offenders == [], (
        f"irreversible migration without a recorded Sponsor reference (I-4): {offenders}"
    )


def test_i5_role_catalogue_changes_carry_a_sponsor_decision_reference():
    """I-5 — W0-D's whole point: a retired role must not return as a quiet
    role-catalogue migration. Changing the catalogue is a Sponsor product act."""
    offenders = []
    for m in MIGRATIONS:
        sql = _text(m)
        if _ROLE_CATALOGUE.search(_statements(sql)) and not _SPONSOR_REF.search(sql):
            offenders.append(m.name)
    assert offenders == [], (
        f"role catalogue changed without a Sponsor-decision reference (I-5): {offenders}"
    )


def test_i6_audit_chain_columns_carry_an_explicit_decision_for_pre_existing_rows():
    """I-6 — the decision about pre-chain rows must be recorded, whatever it is.

    Back-filling and leaving NULL are both defensible; doing either silently is
    not, because the resulting log looks identical and means something different.
    """
    offenders = []
    for m in MIGRATIONS:
        sql = _text(m)
        if not re.search(r"ADD COLUMN\s+(prev_hash|event_hash)", sql, re.I):
            continue
        upper = sql.upper()
        if "PRE-EXISTING ROWS" not in upper or not re.search(
            r"NOT\s+BACK-?FILLED|LEFT\s+NULL|BACKFILL", upper
        ):
            offenders.append(m.name)
    assert offenders == [], (
        f"audit chain columns added with no recorded decision for pre-existing rows (I-6): {offenders}"
    )
