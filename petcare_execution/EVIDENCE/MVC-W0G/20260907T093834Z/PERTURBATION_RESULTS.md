# W0-G perturbation — the controls are armed

A chain that cannot fail these tests is decorative. Each control was made to fail
by a single controlled violation, then restored byte-for-byte.

## Corruption classes — the negative controls themselves

These run against the working implementation and assert that corruption is
DETECTED. They are the arming, not a smoke test.

| Control | Corruption | Detected as | Localised |
|---|---|---|---|
| **T-CHAIN-01** | edit `action_result` on a stored historical row | `hash_mismatch` | index 1 |
| **T-CHAIN-02** | delete a row from the middle | `prev_hash_mismatch` | index 1 |
| **T-CHAIN-03** | append a sibling claiming the same parent (fork) | `prev_hash_mismatch` | index 2 |
| **T-CHAIN-04** | verify a broken chain twice | stays broken; log unmutated | — |

T-CHAIN-02 is the one a per-row integrity check would miss entirely: nothing is
edited, so every surviving row is internally valid. Only the chain position
reveals the gap.

## Implementation perturbation — proving the tests bind to the implementation

| # | Violation | Result | Restored |
|---|---|---|---|
| P1 | chain linking removed from `_audit()` | **7 failed** — all six T-CHAIN plus `test_t_gov_01` | clean |
| P2 | verification overwritten to always report `ok=True` (silent self-heal) | **4 failed** — T-CHAIN-01/02/03/04 | clean |

P2 is the important one. A chain that repairs itself passes every positive test
and destroys the only evidence that the log was ever broken. Without P2, the
suite could not tell a working verifier from one that lies.

Baseline and restored: `petcare_api` 57 passed.

```
PERTURBATION_GUARDS_PROVEN=2 implementation classes + 4 corruption classes
WORKTREE_RESTORED=YES — no perturbation committed
```
