# Gate-5 resume conditions

Gate 5 remains **AUTHORIZED** under the T0 policy-scoped model and **PAUSED**
until this PR merges.

## Preconditions

1. **Fingerprint guard merged to `main`.**
2. **`CURRENT_HEAD_TRACKED_PLAINTEXT = 0`** — enforced continuously by
   `tests/governance/test_retired_key_absence.py`, so it cannot regress
   silently.
3. **Real retired key still rejected** — out-of-band probe, re-run after merge.
4. **`HEAD_TREE_IDENTICAL = YES`** for every ref, proved offline, before any
   remote mutation. For `main` specifically the old and rewritten HEAD trees
   must be byte-identical. This is the precondition whose absence stopped the
   first attempt.
5. **A post-rewrite green suite is NOT sufficient evidence.** `filter-repo`
   mutates tests and implementation together; the first rehearsal passed 150
   tests on a tree that accepted the retired key.

## Admissible rewrite proof

- zero retired-key blobs reachable from any controlled rewritten ref;
- the introducing commit unreachable from every controlled rewritten ref;
- HEAD-tree identity at every ref;
- a changed-blob audit showing only historical commits affected;
- protection preserved and restored, verified by an independent read;
- fresh-clone validation after push.

## The mirror

The disposable mirror from the first attempt has been **discarded**. It contains
the invalid rewrite that disarmed the guard and must never be pushed. The next
attempt starts from a fresh `git clone --mirror` after this PR is merged.

## Blast radius as last measured

Pre-T0 pruning removed two fully-contained merged branches, so the published
carrying set is now **6**, not the 7 originally authorized — smaller, and inside
the policy. Local-only carrying refs: **7**. Carrying tags: **0**. Forks: **0**.
Re-measure at the next T0; do not reuse these numbers.
