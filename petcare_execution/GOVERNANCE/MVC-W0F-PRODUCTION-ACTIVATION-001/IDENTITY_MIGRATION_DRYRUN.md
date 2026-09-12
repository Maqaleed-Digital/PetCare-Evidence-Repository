# A9 — the identity migration, rehearsed

```
IDENTITY_MIGRATION_DRYRUN=PASS
IDENTITY_SOURCE_COUNT=3
IDENTITY_MIGRATABLE_COUNT=0
IDENTITY_QUARANTINED_COUNT=3
IDENTITY_REJECTED_COUNT=0
PRODUCTION_MUTATED=NO
ROWS_WRITTEN_BY_DRY_RUN=0   (asserted against the database, not inferred)
```

Tool: `scripts/governance/identity_migration_dryrun.py`, specified by
`MVC-W0F-IDENTITY-MIGRATION-PLAN-001` §11.

## The result against the live source, and what it means

All three seeded pilot identities quarantine as `UNRESOLVED_NO_TENANT`. Nothing
is migratable.

That is the migration working, not failing. Plan §4 is explicit: an identity
whose `tenant_id` is `None` keeps `NULL` and is quarantined — it is **not**
assigned a tenant by proximity, by role, or by any other signal, because an
inferred scope is indistinguishable from a verified one once written.

The consequence is operational and belongs in front of the Sponsor rather than
inside a cutover window:

> **A production identity migration run today would migrate nobody and
> quarantine everybody.**

```
W0J_PRECONDITION=SPONSOR_TENANT_ASSIGNMENT_FOR_PILOT_IDENTITIES
```

This is a decision, not one of the five gates.

## What the tool does

1. inventories source records — by default the live in-memory registry, which is
   what the plan §1 identifies as the source (there is no persisted credential
   store to read instead);
2. normalises identifiers for **comparison only** — the stored address keeps its
   original form, because rewriting an identifier users type would be
   indistinguishable afterwards from it always having been different;
3. maps roles through an explicit table that is **identity-preserving**;
4. maps tenants through an explicit table, or copies them verbatim when none is
   supplied — and `tenant_map` is a REQUIRED parameter, so "no map" is always a
   decision at the call site rather than an omission;
5. quarantines unknown roles, unknown tenants, absent tenants, duplicates and
   unrecognised credentials, each with its own reason;
6. carries password hashes as opaque strings, and only in formats this estate can
   verify;
7. reports counts and a reconciliation table;
8. writes nothing unless `--apply` is given WITH an explicit `--database-url`.

## Why the role map maps every role to itself

CONF-01: the estate mints two vocabularies for the same roles. A migration that
normalised them would change which identities `require_role()` accepts — and the
change would be invisible afterwards, since the target would simply show the new
spelling as though it had always been held. Changing who may act is a Sponsor
product decision and a migration is the worst place to take one.

## Controls

| ID | Control | Result |
|---|---|---|
| MIG-01 | every known role maps to exactly itself, and every one migrates | PASS |
| MIG-02 | an unknown role is quarantined, never guessed; the retired role included, derived rather than named | PASS |
| MIG-03 | no mapping increases privilege — asserted over the table, and armed by perturbing it | PASS |
| MIG-04 | a tenant outside the supplied map is quarantined as `UNRESOLVED_UNKNOWN_TENANT` | PASS |
| MIG-05 | a record with no tenant is quarantined, never assigned one | PASS |
| MIG-06 | a duplicate email quarantines **every** side, case-insensitively | PASS |
| MIG-07 | a dry run writes zero rows — verified by reading the database afterwards | PASS |
| MIG-08 | applying to an ephemeral database produces the expected counts, with provenance and source id on every row | PASS |
| MIG-09 | a second dry run produces an identical result | PASS |
| MIG-10 | destroy → replay the chain → reapply reconciles to identical counts | PASS |

```
TESTS
  tests/governance/test_identity_migration_contracts.py      36 passed
  petcare_api/tests/test_identity_migration_postgres.py      12 passed
```

## Structural backstop

`MIG-05` is enforced by the database, not only by the tool:

```sql
CHECK (provenance <> 'IDENTITY_MIGRATION' OR tenant_id IS NOT NULL)
CHECK (provenance <> 'IDENTITY_MIGRATION' OR source_record_id IS NOT NULL)
```

If the rule lived only in this script, a re-run, a manual insert or a repair
could place an unresolved identity into the authoritative table — and afterwards
it would be indistinguishable from a verified one. `test_mig_08c` proves the
database refuses it even when the tool is told to write it.

## Credentials

```
PLAINTEXT_PASSWORD_ACCESSED=NEVER
HASHES_RE_HASHED=NONE
UNRECOGNISED_HASH=QUARANTINED
REPORT_CONTAINS_CREDENTIAL_MATERIAL=NO   (asserted by test_mig_07d)
```

A hash nobody can verify produces an account that can never be signed into and
never be told why, so it is held rather than carried. Legacy formats that
`_verify_password` still accepts are carried and marked
`LEGACY_UPGRADES_ON_LOGIN` — W0-J's rehash-on-next-login completes them at the
one moment the plaintext is legitimately available.
