# W0-H regression — full current estate

Measured on `wave0/w0-h`, based on `main` at `6a0c315`.

| Suite | Result |
|---|---|
| governance + root | **160 passed** |
| serving API | **57 passed** |
| runtime | **234 passed** |
| web unit (vitest) | **120 passed** |
| typecheck (`tsc --noEmit`) | **clean** |
| responsive e2e (Playwright) | **90 passed** |
| **Total** | **661 green, 0 failed** |

`tests/` rose from 153 to **160**: seven new W0-H assertions.

`RESPONSIVE=90/90` held.

## Scanners

```
secret_scan.py               SCANNED=3789 ALLOWLISTED=0 FINDINGS=0  CLEAN
prohibited_literal_scan.py   SCANNED=362  ACTIVE_LITERAL_DEFAULT=0
```

## No existing test was modified

W0-H adds guards and an unapplied migration. It changes no application code, so
no existing assertion needed to move.

```
ASSERTIONS_WEAKENED=0
TESTS_MODIFIED=0
TESTS_SKIPPED=0
```
