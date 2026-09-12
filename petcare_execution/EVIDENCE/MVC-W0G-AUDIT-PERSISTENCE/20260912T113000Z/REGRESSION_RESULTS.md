# A14 / A15 — regression, per entrypoint

Exact totals per suite. The composite total alone is not evidence that the
individual suites work — this programme has already been bitten by that.

| Entrypoint | Command | Result |
|---|---|---|
| `ROOT_TEST_COMMAND` | `pytest tests` | **228 passed** |
| `RUNTIME_TEST_COMMAND` | `pytest petcare_runtime/tests` | **247 passed** |
| `API_TEST_COMMAND` | `pytest petcare_api/tests` | **245 passed** |
| `POSTGRES_TEST_COMMAND` | the four PostgreSQL suites | **82 passed** |
| `CI_COMPOSITE_COMMAND` | `pytest tests petcare_runtime/tests petcare_api/tests` | **720 passed** |

228 + 247 + 245 = 720. The per-suite totals sum to the composite, which is the
check that catches a conftest-scope divergence — the defect found in the W0-F
lane, where `pytest tests` failed while the composite passed.

Baseline entering this lane: 698. Net **+22 controls**, zero removed.

### New and changed

| File | Controls |
|---|---|
| `petcare_api/tests/test_audit_persistence_postgres.py` | 22 (new) |
| `petcare_api/tests/test_audit_chain_wired.py` | 6 — moved behind the repository boundary; T-CHAIN-05 **strengthened** |
| `petcare_api/tests/test_audit_probe_authority.py` | 6 — moved behind the boundary |
| `petcare_api/tests/test_governance_attestation.py` | 5 — moved behind the boundary |

T-CHAIN-05 previously asserted `audit_chain_persisted is False` — a
characterisation of the gap, not of the requirement. It now asserts that activity
and durability are reported SEPARATELY and that durability AGREES with the
configured store. Pinning it to `False` would have failed the moment the service
was correctly configured; pinning it to `True` would let an in-memory deployment
claim durability it does not have.

```
ASSERTIONS_WEAKENED=0
CONTROLS_REMOVED=0
CONTROLS_STRENGTHENED=1   (T-CHAIN-05)
```

## Scanners

```
prohibited_literal   SCANNED=389   ACTIVE_LITERAL_DEFAULT=0
secret_scan          SCANNED=3876  ALLOWLISTED=0  FINDINGS=0  CLEAN
evidence bundles     BUNDLES=27  ARTEFACTS=174  FAILED=0   (before this bundle)
```

## Web and responsive

Not re-run locally: no web source was modified. `middleware.ts` and
`app/pharmacy/` were READ during PRE-2 discovery and left untouched. CI runs both
suites on this branch.

## Pre-existing CI skips

7, all `tests/governance/test_cross_repository_traceability.py`, which skips when
the port-source sibling repository is absent — present locally, absent on a
runner. Identical on the `cb5f165a` baseline. This lane contributes 0.
