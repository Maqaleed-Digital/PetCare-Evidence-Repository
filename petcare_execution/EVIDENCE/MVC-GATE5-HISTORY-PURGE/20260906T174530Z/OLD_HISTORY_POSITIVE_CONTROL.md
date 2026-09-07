# Positive control — the scanner was armed before it returned a zero

A zero from an unarmed scanner is indistinguishable from a zero from a clean
repository. This control was executed and sealed **before any local cleanup, GC
or reflog expiry**, while the old objects were still present.

## The instrument

Detection is the W0-A2 recipe: a blob matches when it contains a **25-byte
window whose SHA-256 equals the pinned fingerprint**.

```
FINGERPRINT            = 1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca
COMPARAND_LENGTH_BYTES = 25
```

The comparand is derived in-memory by AST from the introducing commit
(`SECRET_KEY = os.getenv("SECRET_KEY", <const>)`, exactly one candidate
required), its digest is checked against the pinned fingerprint, and it is
never printed, never written to disk and never passed on a command line. Every
reported hit is confirmed by re-hashing the window at that offset. Scanner
source: `gate5_scan.py`.

## Result — run against retained old history (20 carrying refs)

```
BLOBS_SCANNED                        = 5039
OLD_HISTORY_POSITIVE_CONTROL         = 10   (matching blobs)
OLD_HISTORY_POSITIVE_CONTROL_PATH_COUNT = 5
TOTAL_OCCURRENCES                    = 22
```

Carrying paths:

- `petcare_api/routers/auth.py`
- `petcare_api/tests/test_secret_key_required.py`
- `petcare_api/tests/test_w0_ab_ordering_invariant.py`
- `petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/NOTION_AUTHORITY_SYNC.md`
- `tests/governance/test_repository_scanners.py`

This reproduces the independent pre-authorization measurement (10 blobs,
5 paths) exactly, from a scanner written fresh in this run. Raw output:
`OLD_HISTORY_POSITIVE_CONTROL.txt`.

The threshold was **greater than zero**, not ten. The agreement at ten is a
corroboration, not a tuned target.

## Ordering, which is the whole point

```
1. positive control run and sealed      <- old objects still present
2. owned-remote scan                     -> 0
3. local reconciliation and pruning
4. scaffolding refs removed
5. all-namespace scan                    -> 0
6. reflog expire + gc --prune=now
7. all-namespace scan re-run             -> 0
```

A zero produced at step 5 or 7 is admissible **because** step 1 passed first
with the same instrument in the same session.
