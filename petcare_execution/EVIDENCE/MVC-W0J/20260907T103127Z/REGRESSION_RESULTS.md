# W0-J regression — full current estate

Measured on `wave0/w0-j`, based on `main` at `28c4f45`.

| Suite | Result |
|---|---|
| governance + root | **168 passed** |
| serving API | **64 passed** |
| runtime | **247 passed** |
| web unit (vitest) | **120 passed** |
| typecheck (`tsc --noEmit`) | **clean** |
| responsive e2e (Playwright) | **90 passed** |
| **Total** | **689 green, 0 failed** |

`tests/` rose 160 -> **168** (eight migration-invariant assertions);
`petcare_api` rose 57 -> **64** (seven T-PW-01 assertions).

`RESPONSIVE=90/90` held.

## Scanners

```
secret_scan.py               SCANNED=3804 ALLOWLISTED=0 FINDINGS=0  CLEAN
prohibited_literal_scan.py   SCANNED=366  ACTIVE_LITERAL_DEFAULT=0
```

## Existing code changed

`petcare_api/routers/auth.py` — `_hash_password` now uses scrypt; a new
`_verify_password` replaces the inline bcrypt/sha256 branch at sign-in and adds
the rehash-on-success path.

No test was modified. The existing auth and session tests pass unchanged against
the new hashing, which is the useful signal: the credential format changed
underneath them without any assertion needing to move.

```
ASSERTIONS_WEAKENED=0
TESTS_MODIFIED=0
TESTS_SKIPPED=0
```
