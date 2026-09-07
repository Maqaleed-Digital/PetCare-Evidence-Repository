# PORT_REGISTER lineage remap — independent re-derivation

**This file confirms an existing repair. It does not perform one.**

Gate-5 closure (PR #7) re-anchored the ten DONE rows of `PORT_REGISTER.json`
whose closing commits were orphaned by the history rewrite, and records that work
in `MVC-GATE5-HISTORY-PURGE/20260906T174530Z/LINEAGE_CITATION_REMAP.md`.

This run re-derived the same mapping independently, before discovering PR #7 had
landed it. Both derivations produce a byte-identical register (blob `edc0d67`).

| Row(s) | Pre-rewrite | Re-anchored to | Commit subject |
|---|---|---|---|
| PORT-01, PORT-02 | `5e883c18` | `5b2814cc` | port(PORT-01/02): absence guards — assert the forbidden state, not just the good one |
| PORT-03 | `6e4cbccd` | `3bdb099a` | port(PORT-03): error boundaries, ported as behaviour not as code |
| PORT-04, PORT-05, PORT-06 | `136bd100` | `6e033358` | port(PORT-04/05/06): viewport, safety reachability and crash detection |
| PORT-07 | `563ebeb3` | `1dd71d52` | port(PORT-07): governance register integrity, against canonical authorities |
| PORT-08 | `e9d36f5a` | `4a2a9060` | port(PORT-08): empty, loading and error states — and one fabricated queue |
| PORT-09 | `ebed5cba` | `fda31044` | port(PORT-08/09): close PORT-08; marketplace seam that consumes and cannot re-own |
| PORT-10 | `682309f1` | `d08d95e9` | port(PORT-10): the cross-repository denominator — 106 measured, 499 not |

## Verification method

Candidate pairs were looked up in the `filter-repo` commit-map at
`~/dev/gate5-mirror.git/filter-repo/commit-map`. **Nothing here rests on that
mirror's governance status**, and this file takes no position on it. The map was
used only as a lookup hint; every pair was then verified against this repository
directly:

1. the target resolves to a real object of type `commit`;
2. the target is reachable from `main` (`git merge-base --is-ancestor`);
3. the target's changed-path set contains the files that row declares as its
   `targets`.

All seven pass all three. A wrong mapping would fail check 3, because a wrong
commit does not touch the right files. The verification carries the claim; the
lookup source is replaceable.

## Why this is worth recording

The remap is a governance citation chain — the register's rows are the proof that
ported behaviours landed. A second derivation, reached from the commit graph
rather than from the mirror artifact, arriving at the same ten values, is
independent corroboration that the Gate-5 remap is correct.

It also establishes that the remap is reproducible from the repository alone, so
it does not depend on retaining the mirror.
