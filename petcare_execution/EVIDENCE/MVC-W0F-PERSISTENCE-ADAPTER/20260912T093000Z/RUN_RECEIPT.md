# MyVetiCare — W0-F persistence adapter (PR-D), 2026-09-12

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_MUST_BE_PROVEN_APPLIED_BEFORE_ADJUDICATION
```

## Preflight — live state, verified before editing

```
START_HEAD=cb5f165a37c2337594222c985f7d7f6003296db0
PR18=MERGED  ad10910cdc4b69be743490eb2b6fef50aaa7cb6f  2026-09-07T14:00:39Z
PR19=MERGED  22c9efe0ed79c2db4a9106d03169ce061b12a52b  2026-09-07T14:12:33Z
PR20=MERGED  cb5f165a37c2337594222c985f7d7f6003296db0  2026-09-07T14:58:53Z
SESSION_STORE_WIRED=YES   (read_session consults the store; order verified in source)
AC7_07_PRESENT=YES
SUPERSEDING_GOVERNANCE_DECISION=NONE
BASELINE_REGRESSION=520 passed
```

Live state matched the instruction's expectations exactly, so nothing was redone.

## What this PR does

```
B6  SECRET_PROVIDER_IMPLEMENTED=YES
B7  POSTGRES_ADAPTER_IMPLEMENTED=YES
    POSTGRES_TEST_BACKEND=POSTGRESQL (16.11, local ephemeral)
    LIVE_DB_TOUCHED=NO
    LIVE_SECRET_CREATED=NO
```

See `SECRET_PROVIDER_RESULTS.md`, `POSTGRES_INTEGRATION_RESULTS.md`,
`SESSION_REVOCATION_POSTGRES.md`, `ARCHITECTURE_STATE.md`,
`PERTURBATION_MATRIX.md`.

## Regression

```
tests/ (root + governance)       186 passed
petcare_runtime/tests            247 passed
petcare_api/tests                211 passed   (was 87; +124 new controls)
  test_secret_provider.py         64
  test_persistence_mode.py        12
  test_postgres_integration.py    35
  test_session_store_postgres_e2e 13
COMBINED (the CI command)        644 passed

prohibited_literal   SCANNED=374  ACTIVE_LITERAL_DEFAULT=0
secret_scan          SCANNED=3835 ALLOWLISTED=0 FINDINGS=0  CLEAN
evidence bundles     25 bundles, 157 artefacts, FAILED=0

ASSERTIONS_WEAKENED=0
PERTURBATIONS=6, all proven applied, all restored, 0 vacuous
```

Web and responsive not re-run: no web source touched. Last measured (PR #16):
120 vitest, tsc clean, 90/90 Playwright.

## Findings recorded rather than quietly fixed

### 1 · `pytest tests` failed while the CI command passed — Rule 13, exactly

Requiring `PETCARE_PERSISTENCE_MODE` made `routers.auth` unimportable without it,
and `tests/governance/test_retired_key_absence.py` imports that module. The
bootstrap was in `petcare_api/tests/conftest.py`, which is loaded for the
combined command CI runs and **not** for `pytest tests` alone. Green CI would
have hidden it.

Found by measuring each suite separately rather than trusting the combined total,
after a one-test arithmetic discrepancy between the two. Moved to the
repository-root `conftest.py`, which already exists for the same reason
(sys.path). All four invocations now pass: `tests` 186, `petcare_runtime/tests`
247, `petcare_api/tests` 211, combined 644.

### 2 · The migration chain cannot be re-run, and had no runner

Nine tables in `0001`/`0002` use unguarded `CREATE TABLE`. Fixed with a ledger
(`scripts/governance/apply_migrations.py`), not by editing thirty-six historical
migrations. Full reasoning in `POSTGRES_INTEGRATION_RESULTS.md`.

### 3 · CONF-01 is live, and is NOT resolved here

`main.py` seeds its pilot identities with `"platform_admin"`, `"veterinarian"`
and `"owner"`, while `require_role()` accepts only `"Platform Admin"`,
`"Veterinarian"` and `"Owner"`. Those seeded identities authenticate and are then
refused by every protected route with `403 Unknown role`. Tests that need a
working session seed the display spelling instead, which is why the suite does
not show it.

The storage catalogue in `petcare_api/roles.py` therefore admits **both**
vocabularies — exactly what the serving layer already mints, no more and no less
— so adding a catalogue changes no behaviour and the conflict stays visible.

**Choosing one vocabulary changes authorization outcomes for existing identities
and is a Sponsor product decision.** It is not taken here.

```
CONF_01_STATUS=LIVE_AND_UNRESOLVED_SPONSOR_DECISION_REQUIRED
```

### 4 · Registration issued unusable sessions; spent invite codes returned

Both described in `SESSION_REVOCATION_POSTGRES.md`. Both fixed, because both are
defects in the surface this PR rewires rather than adjacent work.

### 5 · Control STRENGTHENED — T-DISP-05

The retired role can no longer be stored, so it cannot reach authorization at
all. The test previously proved it COULD authenticate and was then refused at the
route; it now proves it cannot authenticate, which is what its name always said.
The authorization-layer exclusion (`ROLE_PHARMACY_OPERATOR not in VALID_ROLES`)
is retained and asserted first, so the two layers are proven independently.

### 6 · Evidence custody — five receipts exist only in a working copy

`evidence/receipts/2026-09-07-*.md`, including the W0-F PR-B completion receipt,
are untracked. They are the durable record of merged work and they are not in the
repository. Not fixed here: committing another run's receipts inside this PR
would attribute them to this change. Raised for disposition.

```
UNTRACKED_RECEIPTS=5
```

## Not done, and gated

```
DATABASE_PROVISIONED=NO            GATE_LIVE_APPLY
SCHEMA_APPLIED_TO_PRODUCTION=NO    GATE_LIVE_APPLY
SECRET_CREATED=NO                  GATE_CREDENTIAL_ENTRY
IDENTITY_MIGRATION_DRY_RUN=NOT_IN_THIS_PR  (PR-E)
PRODUCTION_ACTIVATION_PACK=NOT_IN_THIS_PR  (PR-E)
```
