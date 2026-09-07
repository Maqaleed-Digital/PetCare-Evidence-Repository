# W0-I regression — full current estate

Measured on `wave0/w0-i`, based on `main` at `4ed4469`.

| Suite | Result |
|---|---|
| governance + root | **160 passed** |
| serving API | **57 passed** |
| runtime | **243 passed** |
| web unit (vitest) | **120 passed** |
| typecheck (`tsc --noEmit`) | **clean** |
| responsive e2e (Playwright) | **90 passed** |
| **Total** | **670 green, 0 failed** |

`petcare_runtime` rose from 234 to **243**: nine new W0-I controls.

`RESPONSIVE=90/90` held.

## Scanners

```
secret_scan.py               SCANNED=3795 ALLOWLISTED=0 FINDINGS=0  CLEAN
prohibited_literal_scan.py   SCANNED=363  ACTIVE_LITERAL_DEFAULT=0
```

## No existing test or module was modified

W0-I adds a new package (`petcare.professional_authority`), its tests, and an
unapplied migration. No existing application code changed, so no existing
assertion needed to move.

```
ASSERTIONS_WEAKENED=0
TESTS_MODIFIED=0
TESTS_SKIPPED=0
EXISTING_MODULES_MODIFIED=0
```
