# Regression, per entrypoint

| Entrypoint | Result |
|---|---|
| `pytest tests` | **242 passed** |
| `pytest petcare_runtime/tests` | **247 passed** |
| `pytest petcare_api/tests` | **353 passed** |
| the seven PostgreSQL suites | **142 passed in 21.62s** |
| composite (the CI command) | **842 passed** |

242 + 247 + 353 = 842. The per-suite totals sum to the composite.

Baseline entering this lane: 802. Net **+40 controls**, zero removed.

## New

| File | Controls |
|---|---|
| `petcare_api/tests/test_tenant_membership_postgres.py` | 39 — the twelve authorized proof points |
| `petcare_api/tests/test_tenant_authority.py` | +1 — the bound administrative exemption must still name its route and authority |

## Scanners

```
prohibited_literal   SCANNED=399 ACTIVE_LITERAL_DEFAULT=0
secret_scan          SCANNED=3927 ALLOWLISTED=0 FINDINGS=0
```

## Migration chain

No migration was added. The tenant registry (`0034`) and the audit chain
(`0032`) already carried everything this lane needed — the governed path is
service code over the existing schema.

```
MIGRATIONS_IN_CHAIN=39   unchanged
```

## Web and responsive

No web source was modified by this lane. CI runs both suites on the branch.

```
ASSERTIONS_WEAKENED=0
CONTROLS_REMOVED=0
CONTROLS_STRENGTHENED=1
  test_t_ten_06 — was a bare regex requiring require_tenant() near every
  body.tenant_id. It now resolves the ENCLOSING ROUTE by AST and demands either
  tenant-scope authorization or a named, bound administrative authority, so an
  exemption cannot be a comment and cannot outlive its route.
```
