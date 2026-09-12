# A14 — the identity migration rehearsal, after PRE-1

```
IDENTITY_MIGRATION_REHEARSAL=PASS_EMPTY_BY_DESIGN
IDENTITY_SOURCE_SEEDS=0
IDENTITY_DISCARDED_SEEDS=3
IDENTITY_MIGRATABLE=0
IDENTITY_QUARANTINED=0
```

## Empty, and correct

Before the ruling the rehearsal reported `SOURCE=3, MIGRATABLE=0,
QUARANTINED=3` — everything held as `UNRESOLVED_NO_TENANT`, because the seeded
identities carried no tenant and the plan forbids inferring one.

It now reports `SOURCE=0`. The three identities are not quarantined; they no
longer exist, because `PRE1_RULING=1-B` discarded them and the startup path that
created them is gone.

**The difference matters.** A quarantine of 3 is a backlog someone has to
disposition before a cutover. A source of 0 is a migration that has nothing to
do — which is the correct end state when production identity is created through
the governed registration path rather than migrated from development seeds.

```
BEFORE  SOURCE=3  MIGRATABLE=0  QUARANTINED=3   (a backlog)
AFTER   SOURCE=0  MIGRATABLE=0  QUARANTINED=0   (nothing to migrate)
```

## There are no production identities to migrate

Stated plainly rather than implied: this estate has never held a production
identity. The migration plan's own §1 said so —

> **there are no persisted credentials today.** Everything is re-seeded at each
> start.

— and the ruling resolves it by not carrying the development seeds across.

## What a future real migration would require

Unchanged, and now structurally enforced:

- a **registered tenant** for every tenant-scoped identity. `TENANT-10` proves
  the migration cannot create one: the foreign key refuses the write and no
  identity lands.
- an **explicit canonical role**. Migration `0033` narrows the stored catalogue,
  so a display spelling cannot enter.
- the **governed registration / invite path** for anything created rather than
  migrated.

## Verbatim tool output

# Identity migration — reconciliation report

```
IDENTITY_SOURCE_COUNT=0
IDENTITY_MIGRATABLE_COUNT=0
IDENTITY_QUARANTINED_COUNT=0
IDENTITY_REJECTED_COUNT=0
APPLIED=NO (dry run — zero authoritative rows written)
```

## Reconciliation checks (plan §12)

| check | result |
|---|---|
| no_row_lost | PASS |
| no_row_invented | PASS |
| no_role_elevated | PASS |
| no_migrated_row_without_tenant | PASS |
| no_email_appears_twice | PASS |
| every_hash_is_a_known_format | PASS |
| no_plaintext_password_present | PASS |

## Quarantine

None.

## Counts by reason

```
```

