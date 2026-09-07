# Tenant sweep + F3 — regression

Measured on `govern/tenant-sweep-f3`, based on `main` at `e26c76a`.

| Suite | Before | After |
|---|---|---|
| governance + root | 168 | **174 passed** |
| serving API | 64 | **70 passed** |
| runtime | 247 | **247 passed** |
| web unit (vitest) | 120 | **120 passed** |
| typecheck (`tsc --noEmit`) | clean | **clean** |
| responsive e2e (Playwright) | 90 | **90 passed** |
| **Total** | 689 | **701 green, 0 failed** |

`tests/` +6: the estate tenant-signature guard (5) and its literal-scope
meta-test (1). `petcare_api` +6: the audit-probe authority controls.

`RESPONSIVE=90/90` held.

## Scanners

```
secret_scan.py               SCANNED=3810 ALLOWLISTED=0 FINDINGS=0  CLEAN
prohibited_literal_scan.py   SCANNED=368  ACTIVE_LITERAL_DEFAULT=0
```

## Perturbation summary

| Control | Probe | Result |
|---|---|---|
| P5 (W0-I re-verified) | restore `tenant_id=None` default | **FAILED** |
| P6 | class resolution bypasses the shared tenant lookup | **FAILED** |
| P7 | tenant matching removed from the shared lookup | **FAILED** (×2 controls) |
| Tenant guard | planted `= None` default | **detected** |
| Tenant guard | planted `= "platform"` default | **detected** |
| Tenant guard | 4 spellings of the parameter name | **detected** |
| F3 probe A | `PROBE_ROLE = "PHARMACY_OPERATOR"` in `petcare_api` | **FAILED** |
| F3 probe B | `PROBE = "Pharmacy_Operator"` in `petcare_runtime` | **FAILED** |
| F3 probe C | the same string inside a `#` comment | **passed** — correctly silent |

Every perturbation was reverted and the tree re-verified green.

## Code changed

```
petcare_api/main.py    /audit/ui no longer accepts a client-supplied tenant;
                       claimed actor/role are prefixed client-asserted:
tests/governance/test_retired_role_absence.py   case-insensitive needle,
                       token-wise exemption, prose stripping
```

No existing test was modified, skipped or weakened. The retired-role guard now
scans more than it did, which is the point of the F3 repair.

```
ASSERTIONS_WEAKENED=0
TESTS_MODIFIED=0
TESTS_SKIPPED=0
```
