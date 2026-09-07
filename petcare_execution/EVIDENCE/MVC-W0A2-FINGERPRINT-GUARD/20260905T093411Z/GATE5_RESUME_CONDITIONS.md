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

---

# APPENDED 2026-09-06 — mirror governance correction

*Append-only. Nothing above this line has been altered. The text above stands as
written; this records what it referred to and what superseded it.*

## The `DISCARDED_INVALID` classification

The section "The mirror" above condemns a mirror as discarded and says the next
attempt must start from a fresh `git clone --mirror` after PR #6 merges. That
was written when only one mirror existed, and it is correct about that one.

- `DISCARDED_INVALID` referred to the **earlier, invalid** mirror at
  `tmp.ULizkXaVgX`.
- That earlier mirror **disarmed the W0-A guard**. It was **destroyed** and was
  never pushed. The prohibition on it stands unchanged.

## `~/dev/gate5-mirror.git` is a different artefact

- It is the **second, post-W0-A2 mirror** — the fresh post-merge clone this
  document called for.
- Created **after PR #6 merged**: `filter-repo` ran 2026-09-05T12:46:42Z;
  PR #6 merged 09:44:32Z the same day.
- Its `commit-map` is keyed on `24de5399`, the post-merge `main`.
- `main` head-tree identity **passed** against it (`a46ee9f0…` on both sides).
- The armed scanner showed **old > 0, rewritten = 0** against it.
- The introducing commit was **unreachable** from its rewritten refs.
- The **Sponsor explicitly accepted** it for Gate-5 publication.
- The Gate-5 Sponsor transaction used it, successfully.

The condemnation was read forward onto an artefact it was never written about.
The 2026-09-06 pre-authorization measurement flagged the contradiction and
required a Sponsor ruling; the ruling was given, and this is its record.

## Status of the conditions above

Every admissible-rewrite condition listed above was met, and each is evidenced
in `petcare_execution/EVIDENCE/MVC-GATE5-HISTORY-PURGE/20260906T174530Z/`:

| condition | evidence |
|---|---|
| zero retired-key blobs from controlled rewritten refs | `REWRITTEN_HISTORY_SCAN.md` |
| introducing commit unreachable from controlled refs | `REWRITTEN_HISTORY_SCAN.md` |
| HEAD-tree identity (for `main`) | `MAIN_HEAD_TREE_IDENTITY.md` |
| changed-blob audit | `FILTER_REPO_REPORT.md` |
| protection preserved and restored, independently read | `PROTECTION_FIELD_COMPARISON.md` |
| fresh-clone validation after push | `FRESH_CLONE_VERIFICATION.md` |

The warning above that "a post-rewrite green suite is NOT sufficient evidence"
was honoured: tree identity at `main` is the primary proof, and the test estate
is recorded as secondary.

## Blast-radius numbers above are superseded

The figures in "Blast radius as last measured" were correct when written, and
were re-measured at T0 and again in the closeout. Use the closeout figures:
`ALL_NAMESPACE_PRE_CLEANUP.md` — 20 carrying refs (14 local heads + 6 probe
remote-tracking refs).

```
MIRROR_GOVERNANCE_CORRECTION_WRITTEN = YES
```
