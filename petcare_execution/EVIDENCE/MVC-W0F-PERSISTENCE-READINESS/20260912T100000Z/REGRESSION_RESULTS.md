# A14 — regression, per suite

Exact totals per suite, not an aggregate "green". The aggregate is what hid the
defect recorded below.

## Python estate

| Suite | Result |
|---|---|
| `tests` (root + governance) | **228 passed** |
| `petcare_runtime/tests` | **247 passed** |
| `petcare_api/tests` | **223 passed** |
| combined — the command CI runs | **698 passed** |

Baseline before this work: 520 (186 / 247 / 87). Net **+178 controls**, zero
removed, zero weakened.

### New suites

| File | Controls |
|---|---|
| `petcare_api/tests/test_secret_provider.py` | 64 |
| `petcare_api/tests/test_postgres_integration.py` | 35 |
| `petcare_api/tests/test_session_store_postgres_e2e.py` | 13 |
| `petcare_api/tests/test_identity_migration_postgres.py` | 12 |
| `petcare_api/tests/test_persistence_mode.py` | 12 |
| `tests/governance/test_identity_migration_contracts.py` | 36 |
| `tests/governance/test_ksa_portability.py` | 6 |

`tests/governance/test_w0f_architecture_contracts.py` — 11 passed, unchanged in
count, widened in scope (`scripts` added to `APPLICATION_TREES`).

## Each suite was also run ALONE, and that is not ceremony

Measuring only the combined total hid a real defect. `pytest tests` FAILED while
`pytest tests petcare_runtime/tests petcare_api/tests` passed, because the
environment bootstrap lived in `petcare_api/tests/conftest.py` — loaded for the
second command and not the first — and
`tests/governance/test_retired_key_absence.py` imports `routers.auth`.

It surfaced as a one-test arithmetic discrepancy between the two runs. Green CI
would have hidden it entirely, since CI runs only the combined command. Fixed by
moving the bootstrap to the repository-root `conftest.py`.

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
```

## Scanners

```
prohibited_literal   SCANNED=385   ACTIVE_LITERAL_DEFAULT=0
secret_scan          SCANNED=3854  ALLOWLISTED=0  FINDINGS=0   CLEAN
evidence bundles     BUNDLES=26  ARTEFACTS=163  FAILED=0
```

## PostgreSQL

```
POSTGRES_TEST_BACKEND=POSTGRESQL
POSTGRES_TEST_VERSION=16.11 (local ephemeral) / postgres:16 (CI service)
POSTGRES_TEST_LOCATION=LOCAL_EPHEMERAL
LIVE_DB_TOUCHED=NO
SQLITE_SUBSTITUTED=NO
```

CI gained a step that fails if the PostgreSQL controls were **skipped**, because
a skipped suite and a passing one are indistinguishable in a summary line.
Observed in CI on PR #21: `48 passed`, 0 skipped.

## Web and responsive

Not re-run locally: no web source was touched by this work. Measured in CI on
PR #21 against this change:

```
TypeScript     clean
Web unit       120 passed (18 files)
Responsive     90 passed
```

## Pre-existing CI skips, quantified

CI reports 7 skipped in the Python estate. They are
`tests/governance/test_cross_repository_traceability.py`, which skips when the
port-source sibling repository is absent — it is present locally and absent on a
runner.

Confirmed pre-existing rather than introduced: the baseline run on `cb5f165a`
(PR #20's merge) reported `513 passed, 7 skipped` for the same 520 collected.
This change contributes 0 skips.

```
ASSERTIONS_WEAKENED=0
CONTROLS_REMOVED=0
CONTROLS_STRENGTHENED=1   (T-DISP-05; see the PR-D receipt)
```
