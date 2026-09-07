# PORT_REGISTER lineage repair — old→new closing-commit map

Ten DONE rows cited commits orphaned by the Gate-5 history rewrite. Seven
distinct SHAs across ten rows.

| Row(s) | Cited (pre-rewrite) | Re-anchored to | Commit subject |
|---|---|---|---|
| PORT-01, PORT-02 | `5e883c18` | `5b2814cc` | port(PORT-01/02): absence guards — assert the forbidden state, not just the good one |
| PORT-03 | `6e4cbccd` | `3bdb099a` | port(PORT-03): error boundaries, ported as behaviour not as code |
| PORT-04, PORT-05, PORT-06 | `136bd100` | `6e033358` | port(PORT-04/05/06): viewport, safety reachability and crash detection |
| PORT-07 | `563ebeb3` | `1dd71d52` | port(PORT-07): governance register integrity, against canonical authorities |
| PORT-08 | `e9d36f5a` | `4a2a9060` | port(PORT-08): empty, loading and error states — and one fabricated queue |
| PORT-09 | `ebed5cba` | `fda31044` | port(PORT-08/09): close PORT-08; marketplace seam that consumes and cannot re-own |
| PORT-10 | `682309f1` | `d08d95e9` | port(PORT-10): the cross-repository denominator — 106 measured, 499 not |

## How the mapping was obtained, and why the source does not matter

The old→new pairs were looked up in the `filter-repo` commit-map at
`~/dev/gate5-mirror.git/filter-repo/commit-map`.

That mirror is recorded as `DISCARDED_INVALID` in `GATE5_RESUME_CONDITIONS.md`
and `GATE5_PREFLIGHT.md`, and its true status is one of the open questions in the
Gate-5 preflight. **This repair does not rest on resolving that question**, and
takes no position on it. The commit-map was used only as a lookup hint; every
pair was then verified against this repository directly:

1. the target resolves to a real object of type `commit`;
2. the target is reachable from `main` (`git merge-base --is-ancestor`);
3. the target's changed-path set contains the files that row declares as its
   `targets`.

All seven pass all three checks. Any mapping the commit-map had got wrong would
have failed check 3, because a wrong commit does not touch the right files. The
verification is what carries the claim; the lookup source is replaceable.

## Result

`test_every_done_port_cites_a_closing_commit_that_is_a_real_object` moves from
FAILING to passing. `tests/governance`: 109 passed.

The register's 8-character convention was preserved — see `RUN_RECEIPT.md` for
why full SHAs were not substituted.
