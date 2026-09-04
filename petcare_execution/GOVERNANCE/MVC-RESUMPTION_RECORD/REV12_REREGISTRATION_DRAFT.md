# REV-12 re-registration — DRAFT, NOT RATIFIED

**Date:** 2026-09-05 · **Under:** `MVC-GOV-CANON-001`
**Status:** `REV12_STATUS=DRAFT_NOT_RATIFIED`
**Does not modify** `MVC-RESUMPTION_RECORD.md`. REV 8's row stays exactly as written.

## What the preflight established

```
REV8_SEAL_VALID_FOR_REV8_BYTES = YES
HASH_CHAIN_INTACT              = YES
LATER_REVISIONS_NOT_REREGISTERED = YES
REV8_ALL_DRIFTED_BYTES_RECOVERED = YES  (4 of 4)
```

REV 8 registered six artefacts. Two still reproduce; four do not. All four
non-reproducing byte-sets were **recovered in full** from the
`Maqaleed-Digital` git object database, by hashing extracted blob bytes — git
object IDs were never compared against the registered SHA-256.

Every one of the four registered blobs lives in a **single commit, `21cb463`**
(2026-08-31), which is REV 8's own commit. That is the finding: REV 8 sealed
the documents as they stood at REV 8, later revisions legitimately changed four
of them, and no later REV re-registered. **There is no custody break, no
corruption, and no fresh baseline.** The defect is a missing re-registration.

## The six artefacts

| Document | REV-8 SHA-256 | REV-8 blob | Current SHA-256 | Δ REV8→current | Class |
|---|---|---|---|---|---|
| MVC-BRD-001 V3.2 | `d480cb71…3862c0a` | `a7e49290ba15` | `32f53669…efc287d` | +124 −13 | REVISED |
| MVC-IMPLEMENTATION-BASELINE-001 V1.0 | `a5c831e4…2a9e36e1f39` | — | identical | — | **UNCHANGED** |
| MVC-BUILD-GAP-001 V1.0 | `e05d19a9…6c77c13bed09` | `2004d14567a6` | `1cd7ccf7…4f5d00f6` | +47 −0 | REVISED |
| MVC-EXEC-BACKLOG-001 V1.0 | `df3cb3d7…dcff5b84e551` | `2b1dead68a04` | `c537f615…254c1c1d` | +119 −0 | REVISED |
| MVC-EXEC-001 V1.0 | `e8a8dfc8…64cfc968fea19` | — | identical | — | **UNCHANGED** |
| MVC-RT-003 V1.0 | `1546d5f7…dfc6dc2cfd29` | `617739154965` | `adeb6425…264b397a` | +70 −0 | REVISED |

Three of the four revisions are **purely additive**. Only V3.2 removed lines,
and its denominator text is byte-identical across the change — the drift does
not touch the `495` figure, which was already stale when REV 8 sealed it.

Revising commits: `a379cf3` (content correctness, ARCH-05 CP-1, P0 auth
defects) and `c56b399` (CP-2 residue reconciliation). Both are ordinary
authoring, recorded in REVs 9–11.

## What REV 12 would do

```
REV12_PURPOSE = RE-REGISTER_CURRENT_BYTES_AND_BIND_DIFF_CHAIN
```

1. Register the **current** SHA-256 of all six artefacts.
2. Bind the REV8 → current diff chain, so the two seals are linked rather than
   one superseding the other silently.
3. Record `21cb463` as the commit the REV-8 seal describes, which is what makes
   the earlier seal verifiable rather than merely historical.
4. Leave REV 8 untouched.

## What REV 12 would NOT do

- It does not ratify anything. The lineage remains DRAFT: *"All outputs are
  DRAFT pending Sponsor verdict. Nothing is ratified."*
- It does not repair the stale `495` inside V3.2 — that needs the narrow V3.3
  authoring act (C-21).
- It does not assert a custody break, because there was none.

## Standing lesson

A hash register that is not re-issued when its artefacts are legitimately
revised produces something that **looks exactly like corruption** and is not.
The discriminator is recoverability: if the registered bytes are still
retrievable from an object database, the seal was valid and the register is
merely stale. That test cost one `git cat-file` per candidate blob and turned a
suspected custody break into a bookkeeping defect.
