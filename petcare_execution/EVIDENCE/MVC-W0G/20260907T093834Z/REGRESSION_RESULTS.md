# W0-G regression — full current estate

Measured on `wave0/w0-g`, based on `main` at `200b169`.

| Suite | Result |
|---|---|
| governance + root (`pytest tests`) | **153 passed** |
| serving API (`pytest petcare_api/tests`) | **57 passed** |
| runtime (`pytest petcare_runtime/tests`) | **234 passed** |
| web unit (vitest) | **120 passed** |
| typecheck (`tsc --noEmit`) | **clean** |
| responsive e2e (Playwright) | **90 passed** |
| **Total** | **654 green, 0 failed** |

`petcare_api` rose from 51 to **57**: six new W0-G controls in
`test_audit_chain_wired.py`.

`RESPONSIVE=90/90` held.

## Scanners

```
secret_scan.py               SCANNED=3783 ALLOWLISTED=0 FINDINGS=0  CLEAN
prohibited_literal_scan.py   SCANNED=361  ACTIVE_LITERAL_DEFAULT=0
```

## One existing test was modified — and it was not weakened

`test_t_gov_01_chain_claim_matches_independent_verification` asserted the
pre-W0-G state:

```python
assert independent is False
assert body["audit_chain_verification"] == "NOT_WIRED_INTO_SERVING_PATH"
```

W0-G exists to change that state, so a state snapshot had to move. What did NOT
move is the invariant the test guards — that the endpoint reports what an
independent check computes, never a constant:

```python
assert body["audit_chain_active"] is independent   # unchanged
```

Two assertions were **added**, not removed: that the chain is not persisted, and
that durability is reported separately. Assertion count for this test went from
4 to 6.

`ASSERTIONS_WEAKENED=0`. No test was skipped, xfailed, or deleted.
