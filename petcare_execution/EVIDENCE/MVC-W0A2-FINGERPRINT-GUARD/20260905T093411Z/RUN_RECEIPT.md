# Run receipt — W0-A2 fingerprint guard

**Date:** 2026-09-05 · **Branch:** `security/w0a2-fingerprint-guard` from `36e03de0`
**Not** the Gate-5 history rewrite. A normal authored security PR.

## Why this exists

The Gate-5 offline rehearsal rewrote the retired signing key out of history and
produced a tree whose guard compared against the tombstone instead of the key.
That tree **accepted the real retired key** — and 150 tests passed, because the
content-based rewrite had edited the assertions in step with the implementation.

The root cause was not the rewrite. It was that the plaintext lived at HEAD as a
guard comparand at all. A content-based rewrite cannot distinguish the secret as
a leaked value from the secret as the value something refuses.

## What changed

`_require_secret_key()` now compares a SHA-256 fingerprint. Normalisation is
unchanged, so it refuses exactly the values it refused before, and the retired
key appears nowhere in the file.

**11 plaintext occurrences across 5 files removed** — guard comparand, docstring,
two test constants, five scanner fixtures, one line of governance prose.

```
CURRENT_HEAD_TRACKED_PLAINTEXT = 0
FINGERPRINT_PINNED             = 1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca
```

## Behaviour proved, not assumed

Repository tests exercise the *mechanism* with a synthetic value and a patched
fingerprint set — they cannot use the real key without reintroducing it. The
real-key proof is therefore out-of-band, run once from history, with the
material wiped immediately:

```
real retired key   -> REJECTED
ordinary key       -> ACCEPTED
whitespace / unset -> REJECTED
tombstone marker   -> ACCEPTED  (deliberate; not a governance requirement)
```

## Guards added

The fingerprint set is **pinned** — without that, emptying it would defeat
W0-A2 while every synthetic test still passed. A repository-wide guard proves no
tracked file contains the key, carries its own positive control, and checks that
the guard file has not itself acquired the value. A companion structural test
forbids any secret-sized literal comparand in `auth.py`, and a third proves the
fingerprint check is actually reached rather than sitting in dead code.

## Measured

| Check | Result |
|---|---|
| python combined | **428 passed** |
| governance | **109 passed** |
| petcare_api (W0-A/B) | **51 passed** |
| retired-key absence guard | 5 passed |
| vitest / tsc | 120 passed / clean |
| playwright | **90 / 90** |
| secret scan | CLEAN, 0 allowlisted |
| prohibited-literal scan | 0 active defaults |

```
PRODUCTION_MUTATED = NO · LIVE_DB_MUTATED = NO · GCP_MUTATED = NO
IRREVERSIBLE_HISTORY_ACTION_PERFORMED = NO
GATE5_AUTHORIZATION = STILL_VALID_POLICY_SCOPED
GATE5_EXECUTION     = PAUSED_UNTIL_THIS_MERGES
GATE5_NEW_PRECONDITION = HEAD_TREE_IDENTICAL
OLD_MIRROR_DISCARDED = YES
```
