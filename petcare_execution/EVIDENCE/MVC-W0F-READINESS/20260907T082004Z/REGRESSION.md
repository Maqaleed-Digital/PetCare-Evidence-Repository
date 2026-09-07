# Regression — full estate, post-repair

| Suite | Command | Result |
|---|---|---|
| governance + root | `pytest tests -q` | **143 passed** |
| serving API | `pytest petcare_api/tests -q` | **51 passed** |
| web unit | `npm run test` (vitest) | **120 passed** (18 files) |
| web e2e | `npx playwright test` | **90 passed** (mobile-chromium) |
| | **Total** | **404 green, 0 failed** |

Before the repair, `pytest tests` reported **1 failed, 142 passed**. The single
failure was the dangling-citation guard described in `PORT_LINEAGE_REPAIR.md`.
No test was modified, skipped, weakened or marked xfail to reach green:
`ASSERTIONS_WEAKENED=0`.

## Guard armedness (perturb, measure, revert)

```
W0-A/W0-A2  reintroduce literal default in _require_secret_key()
            -> 4 failed, 47 passed
            test_t_sec_01_unset_secret_refuses_to_start
            test_t_sec_01b_blank_secret_refuses_to_start
            test_t_sec_04_no_literal_fallback_in_source
            test_w0a_no_getenv_supplies_a_default_signing_key
            reverted; git diff clean

PORT-01     reintroduce pharmacy_operator into a scanned source
            -> 1 failed, 8 passed
            reverted; git diff clean
```

Both guards are armed: the forbidden state fails a test rather than passing
quietly.
