# MVC-GENESIS-PLATFORM-ADMIN — run receipt

**Lane:** non-production implementation and verification of the single-use
first-`platform_admin` genesis mechanism.
**Authority:** `MVC-GENESIS-PLATFORM-ADMIN-001` §8, `[SPONSOR]`, 12 September 2026.
**Recorded:** `petcare_execution/GOVERNANCE/MVC-PREPROD-SPONSOR-DECISION-001/RATIFICATION-004.md`

```
GENESIS_NON_PRODUCTION_IMPLEMENTATION=COMPLETE
PRODUCTION_GENESIS_EXECUTED=NO
GENESIS_CONSUMED=NO
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
```

## What this lane closes

`FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY=UNRULED` — the blocking finding
recorded at the pre-P1 stop. `RATIFICATION-002` item 3 made `platform_admin`
the sole role permitted to administer tenant membership and withheld every
authority that could create one; registration is invite-gated to `owner` and
`veterinarian`, `PRE1_RULING=1-B` discarded the seed identities, and startup
creates none. Production had no authorized route to its first administrator.

The finding blocked plan Phase F. It never blocked B-D, and the prepared B-D
authorization request is unchanged.

## Built

| artefact | what it is |
|---|---|
| `petcare_runtime/migrations/0035_genesis_platform_admin.sql` | `GENESIS` provenance; a unique index admitting at most one `GENESIS` identity; the `platform_admin_genesis` consumption record with a singleton primary key. Creates no identity, consumes no authority. |
| `petcare_api/platform_admin_genesis.py` | the governed procedure - no role parameter, `INSERT` only, one transaction |
| `scripts/governance/platform_admin_genesis.py` | the operator entry point, with read-only `--check` |
| `petcare_api/tests/test_platform_admin_genesis_postgres.py` | 18 controls on real PostgreSQL |
| `tests/governance/test_platform_admin_genesis_authority.py` | 17 guards over sections 2/5/7, each with a meta-test |
| `.../GOVERNANCE/MVC-PREPROD-SPONSOR-DECISION-001/RATIFICATION-004.md` | the ruling, recorded verbatim |
| `.../GOVERNANCE/MVC-P1-PRODUCTION-ACTIVATION/P1_GENESIS_STEP-001.md` | the prepared production step (section 8) - not an authorization |

Two pre-existing files changed: `petcare_api/repositories.py` gains
`PROVENANCE_GENESIS` (additive; `VALID_PROVENANCE` 3 -> 4), and
`.github/workflows/verify.yml` names the new PostgreSQL suite in the non-skip
step - required by `tests/governance/test_ci_postgres_coverage.py`, which
exists because that step has fallen behind the tree three times.

## Defect found and fixed in the harness

`pg_harness.reset_w0f_tables` did not know about `platform_admin_genesis`. The
consequence was not a stale row: the FK from the consumption record onto
`user_identity` made the `user_identity` delete fail, and **every** suite
sharing the session database errored in teardown - 16 errors at once. Fixed by
emptying the child before its parent, the same ordering the tenant FK already
required.

## Regression

| invocation | result |
|---|---|
| `pytest tests petcare_runtime/tests petcare_api/tests` (the CI command) | **889 passed** |
| `pytest tests` alone | 271 passed |
| `pytest petcare_api/tests` alone | 371 passed |
| `pytest petcare_runtime/tests` alone | 247 passed |

Baseline before this lane was 854. Each suite was run alone as well as
combined, because conftest scope differs per invocation and a suite that passes
only in the combined command is a suite CI cannot be trusted to gate.

PostgreSQL coverage is real, not skipped: the suite runs against a live server,
and the 35 genesis controls were reported as passed rather than skipped -
`pytest.importorskip` did not swallow them.

## One reading the implementation had to make

Section 3 permits the first administrator to hold *"the tenant context required
by the governed production identity model"*. In this estate that model
represents platform scope as the **absence** of a tenant plus an explicit role,
never as a tenant standing for everyone (TENANT-04/TENANT-09). Binding the
administrator to the ruled first production tenant would additionally require
creating that tenant row first - migration 0034 puts an FK from
`user_identity.tenant_id` onto `tenant` - which section 9 withholds. The Sponsor
selected absence on 12 September; the genesis audit event carries
`UNATTRIBUTED`, the representation the estate already uses for a governed event
with no tenant perimeter and the reason 0034 deliberately puts no FK on
`audit_event.tenant_id`.

## Not done, because the ruling withholds it

The production genesis write; the production identity; the production
credential; the production tenant row; any second or replacement
`platform_admin`. `PRODUCTION_TENANT_ROW_CREATED=NO` is unchanged.
