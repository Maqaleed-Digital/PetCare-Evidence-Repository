# filter-repo report

The rewrite was produced by `git filter-repo` in the mirror at
`~/dev/gate5-mirror.git`. Its own artefacts are reproduced here rather than
summarised:

| artefact | this pack |
|---|---|
| `filter-repo/commit-map` | `FILTER_REPO_COMMIT_MAP.txt` (429 lines) |
| `filter-repo/ref-map` | `FILTER_REPO_REF_MAP.txt` (14 refs) |

## First changed commit

```
5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96 -> 43921489b9be7b4375d9f2706496e19005648953
```

`filter-repo`'s own `first-changed-commits` names the **introducing commit** as
the first commit the rewrite altered. Everything before it maps to itself.
That is an independent corroboration, from the tool rather than from the
operator, that the rewrite began exactly where the literal entered.

## Refs rewritten

14 refs appear in `ref-map`. Six of them are the published set
(`REMOTE_REF_MAP.md`); the other eight are local-only refs, reconciled in this
closeout rather than published (`WAVE0_LOCAL_REF_RECONCILIATION.md`,
`LOCAL_PRUNING.md`).

## Known cosmetic residue, recorded not hidden

`filter-repo/suboptimal-issues` lists 14 abbreviated commit hashes that appear
inside *commit messages* and were left as-is when the commits they referenced
were rewritten. Commit messages are immutable now that the rewrite is
published, so these remain stale by construction. They are prose references
inside historical messages, not machine-checked citations, and nothing asserts
them. The machine-checked citations that *did* break were repaired — see
`LINEAGE_CITATION_REMAP.md`.
