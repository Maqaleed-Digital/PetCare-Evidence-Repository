# A3–A6 — the PostgreSQL adapter, against real PostgreSQL

```
POSTGRES_ADAPTER_IMPLEMENTED=YES
POSTGRES_TEST_BACKEND=POSTGRESQL
POSTGRES_TEST_VERSION=16.11
POSTGRES_TEST_LOCATION=LOCAL_EPHEMERAL
LIVE_DB_TOUCHED=NO
CLOUD_CREDENTIAL_USED=NO
SQLITE_SUBSTITUTED_FOR_POSTGRES=NO
```

The cluster is created by `initdb` into a temporary directory, listens on
127.0.0.1 only, uses trust auth, and is stopped and removed at exit. CI uses an
ephemeral `postgres:16` service container instead; both are pointed at by
`PETCARE_TEST_PG_URL`.

**Unavailability is a failure, not a skip.** A suite that silently skips its only
integration coverage reports green having evaluated nothing, and that green is
indistinguishable from having run. `verify.yml` additionally asserts that the
PostgreSQL controls were not skipped.

## The migration chain, actually replayed

```
MIGRATIONS_IN_CHAIN=36
MIGRATIONS_APPLIED_CLEANLY=36
FAILURES=0
TABLES_CREATED=50 (+4 from 0031)
```

This verifies a claim `MVC-W0F-DATA-STORE-DECISION-001` previously only asserted:
the thirty-five pre-existing migrations are portable SQL and replay unchanged
against PostgreSQL 16. `MVC-W0F-KSA-MIGRATION-READINESS-001` §2 depends on it —
the KSA target is built by replaying the chain.

## FINDING — the chain is not re-runnable, and there was no runner

`0001_ep01_ep02_baseline.sql` and `0002_ep01_ep02_wave_02.sql` create nine tables
with unguarded `CREATE TABLE`. Replaying the chain over an already-migrated
database fails with `DuplicateTable` at the first one. There was no migration
runner and no applied-migrations ledger anywhere in the estate.

Found by running it. It matters because both the activation pack's schema-apply
phase and the KSA readiness specification say "apply the migration chain", and
neither is an operation that could be retried.

**The repair is a ledger, not `IF NOT EXISTS` on thirty-six files.**
`scripts/governance/apply_migrations.py` applies each migration at most once,
inside its own transaction, recording filename and SHA-256 in a
`schema_migration` table it creates itself. Editing the historical migrations
instead would move the correctness requirement into every future migration's
text, where one omission is invisible until a cutover — and would make a
partially-applied migration silently resumable, which is exactly when it must
not be.

```
RUNNER_FIRST_RUN=36 applied
RUNNER_SECOND_RUN=0 applied, 36 already recorded, schema byte-identical
RUNNER_DRY_RUN=0 applied, only the ledger table exists
RUNNER_DRIFT_DETECTION=REFUSES a migration edited after it was applied
```

## Controls

| ID | Control | Result |
|---|---|---|
| DB-01 | the chain applies from a clean state; the four W0-F tables exist | PASS |
| DB-02 | the raw chain is **not** re-runnable and refuses loudly (recorded finding) | PASS |
| DB-02b | the runner applies each migration exactly once; schema identical after a second run | PASS |
| DB-02c | the runner refuses a migration edited after being applied (armed by mutating the ledger digest, landing asserted) | PASS |
| DB-02d | a dry run applies nothing | PASS |
| DB-03 | an invalid role is rejected by the repository AND by a `CHECK` constraint (`SQLSTATE 23514`) | PASS |
| DB-03c | every `ROLE_*` constant the estate defines but the catalogue omits is refused — derived, never named | PASS |
| DB-04 | a blank tenant is refused; a NULL tenant remains expressible; a duplicate email raises `SQLSTATE 23505` | PASS |
| DB-05 | a migrated identity with no tenant, or with no source record, is refused by the database | PASS |
| DB-06 | a revoked session cannot resolve active; the row is preserved | PASS |
| DB-07 | an expired session cannot resolve active; the row is preserved | PASS |
| DB-08 | a foreign-tenant session cannot resolve and cannot be revoked | PASS |
| DB-09 | an unknown session cannot resolve | PASS |

**No refusal was accepted on "it raised".** Every negative control asserts the
exception class and, where PostgreSQL supplies one, the `SQLSTATE` — so a missing
table or a syntax error fails the control instead of satisfying it.
`test_the_w0f_constraints_actually_exist` states the precondition directly.

```
TESTS=petcare_api/tests/test_postgres_integration.py   35 passed
```

## Two defects this work produced and caught

1. **The pool `configure` hook left the connection in a transaction.**
   `psycopg_pool` silently discards a connection a hook leaves open, retries, and
   then reports a pool timeout — so a perfectly reachable database presented as
   "could not be reached". Fixed with an explicit `commit()`, documented at the
   call site.
2. **`open_pool` reported a refused connection as slowly as an unreachable
   network.** A direct preflight connection now runs first, so the reported
   exception is the real one and a refusal is immediate.
