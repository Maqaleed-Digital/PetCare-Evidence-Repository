# A20 — regression, per entrypoint

Every canonical entrypoint run independently AND the composite. An individual
command's failure is not hidden behind composite green — this programme has
already been bitten by that once.

| Entrypoint | Command | Result |
|---|---|---|
| `ROOT_TEST_COMMAND` | `pytest tests` | **242 passed** |
| `RUNTIME_TEST_COMMAND` | `pytest petcare_runtime/tests` | **247 passed** |
| `API_TEST_COMMAND` | `pytest petcare_api/tests` | **313 passed** |
| `POSTGRES_TEST_COMMAND` | the six PostgreSQL suites | **103 passed** |
| `CI_COMPOSITE_COMMAND` | `pytest tests petcare_runtime/tests petcare_api/tests` | **802 passed** |

242 + 247 + 313 = 802. The per-suite totals sum to the composite, which is the
check that catches a conftest-scope divergence.

Baseline entering this lane: 720. Net **+82 controls**, zero removed.

## New this lane

| File | Controls |
|---|---|
| `petcare_api/tests/test_role_authority.py` | 31 — ROLE-01..09, PHARM-ROLE-01..04, CONF-01 closure |
| `petcare_api/tests/test_tenant_registry.py` | 18 — TENANT-01..10 |
| `petcare_api/tests/test_seed_retirement.py` | 16 — SEED-01..06 |
| `tests/governance/test_retired_role_family.py` | 14 — context-aware family guard + 9 meta-tests |
| `petcare_api/tests/test_end_to_end_identity_postgres.py` | 3 — the full governed path |

## Scanners

```
prohibited_literal   SCANNED=391   ACTIVE_LITERAL_DEFAULT=0
secret_scan          SCANNED=3897  ALLOWLISTED=0  FINDINGS=0  CLEAN
evidence bundles     BUNDLES=28  ARTEFACTS=186  FAILED=0   (before this bundle)
credential literals  FILES_SCANNED=239  COUNT=0
```

## Migration chain

```
MIGRATIONS_IN_CHAIN=39   (+0032 audit persistence, +0033 role catalogue, +0034 tenant registry)
REPLAYED_CLEANLY=39
TENANT_ROWS_AFTER_REPLAY=0
```

## Web and responsive

`middleware.ts` was modified, so the web suites are materially in scope. They are
run by CI on this branch (`npm run typecheck`, `npm test`, `npm run e2e`) and
were not re-run locally — node and Playwright are CI-provisioned here.

## CI, observed on PR #25

```
Python estate   795 passed, 7 skipped   (= 802 collected, matching local)
PostgreSQL step  82 passed, 0 skipped
TypeScript       clean
Web unit        120 passed (18 files)   — middleware.ts changed, so this is in scope
Responsive       90 passed
```

### The non-skip guard fell behind AGAIN

The `PostgreSQL controls must not be skipped` step named four suites; this lane
added two more (`test_tenant_registry.py`, `test_end_to_end_identity_postgres.py`)
and the step kept passing at 82 while 21 further PostgreSQL controls were outside
it.

That is the second time. The list is now six, and the step carries a note that it
must be extended whenever a PostgreSQL suite is added — deliberately not derived
by globbing, because a derived list stops being a decision and would silently
include files nobody meant to gate on.

## Assertions

```
ASSERTIONS_WEAKENED=0
CONTROLS_REMOVED=0
CONTROLS_STRENGTHENED=2
  test_auth.py::test_sign_in_valid_sets_cookies — accepted any of five spellings
    including `admin`, `vet` and `pharmacy`; now asserts the canonical id exactly.
    An assertion that broad could not have failed on a wrong vocabulary, which is
    part of why CONF-01 survived.
  test_t_disp_05 — now derives EVERY role the catalogue refuses and asserts each,
    rather than naming one.
```
