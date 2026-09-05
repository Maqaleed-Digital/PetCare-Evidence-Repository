# Notion update block — PREPARED, NOT APPLIED

```
W0-A2                          = fingerprint guard authored (PR open)
CURRENT_HEAD_TRACKED_PLAINTEXT = 0   (was 11 occurrences across 5 files)
RETIRED_KEY_SHA256             = 1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca
REAL_KEY_STILL_REJECTED        = YES (out-of-band probe)
BEHAVIOUR_CHANGE               = NONE

GATE5_AUTHORIZATION            = STILL_VALID_POLICY_SCOPED
GATE5_EXECUTION                = PAUSED_UNTIL_W0A2_MERGED
GATE5_NEW_PRECONDITION         = HEAD_TREE_IDENTICAL before any remote mutation
GATE5_BLAST_RADIUS_LAST_MEASURED = 6 published (after pre-T0 prune of 2) · 7 local · 0 tags · 0 forks
OLD_GATE5_MIRROR               = DISCARDED (contained the invalid rewrite)

CP2_DECISION_LOG_LODGED        = YES · Proposed · Date Ratified 2026-08-31
DENOMINATOR_STATUS             = NOT_REPRODUCIBLE_MISSING_SOURCE (unchanged)
LINEAGE_RATIFIED               = NO (unchanged)
```

## The finding worth recording in the handoff

Gate 5 was correctly stopped, and the reason generalises:

> **A content-based history rewrite cannot distinguish a secret as a leaked
> value from the same secret as the value a guard refuses.** Rewriting the
> second silently disarms the guard — and the test suite cannot detect it,
> because the rewrite edits the assertions and the implementation together.

Two standing rules follow:

1. *"No active literal" is not evidence of "no literal at HEAD."* Measure the
   bytes.
2. A green suite after a history rewrite is **not** independent evidence.
   Gate-5 acceptance requires HEAD-tree identity plus zero secret reachability,
   with tests only as a secondary signal.

The durable fix is the one in this PR: security guards should hold a
**fingerprint**, never the forbidden value, so history can be rewritten without
touching live behaviour.
