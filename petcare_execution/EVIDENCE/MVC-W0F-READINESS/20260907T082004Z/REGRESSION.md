# Regression — full estate

Measured on `main` at `8c3c63d6c5c8ef8b74cee0c61b67ea1e4dbb6d45` (after Gate-5
closeout PR #7). This run modifies no code, so these are baseline measurements,
not before/after.

| Suite | Command | Result |
|---|---|---|
| governance + root | `pytest tests -q` | **143 passed** |
| serving API | `pytest petcare_api/tests -q` | **51 passed** |
| web unit | `npm run test` (vitest) | **120 passed** (18 files) |
| web e2e | `npx playwright test` | **90 passed** (mobile-chromium) |
| | **Total** | **404 green, 0 failed** |

No test was modified, skipped, weakened or marked xfail: `ASSERTIONS_WEAKENED=0`.

The web suites were measured before rebasing onto the Gate-5 closeout. That
measurement carries: PR #7 changed **zero** files under `petcare_web`,
`petcare_api`, `petcare_runtime`, `scripts` or `tests` — it touched only evidence
directories and `PORT_REGISTER.json`. Verified with
`git diff --name-only 3cef8f9 origin/main -- <those paths>` returning empty.

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
quietly. The pack records 3 failures for W0-A; it is now 4, because W0-A2 added
the AST ordering check.
