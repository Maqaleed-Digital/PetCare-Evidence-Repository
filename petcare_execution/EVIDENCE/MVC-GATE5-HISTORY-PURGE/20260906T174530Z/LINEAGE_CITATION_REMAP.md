# Lineage citation remap — the defect the rewrite left behind

## What broke, and how it was found

The published rewrite left `main` **red**. CI run `34046982901` on
`3cef8f9db73a07aab33e953ac7d41c8b238d159d` failed in 27 seconds:

```
FAILED tests/governance/test_canonical_register_integrity.py::
       test_every_done_port_cites_a_closing_commit_that_is_a_real_object
AssertionError: closing commits that are not commits here:
  [('PORT-01','5e883c18'), ..., ('PORT-10','682309f1')]
1 failed, 420 passed, 7 skipped
```

This is a direct and predictable consequence of the purge. The canonical
registers cite commits **by SHA**, and assert that each resolves to a real
object. The rewrite gave every affected commit a new SHA, so ten `DONE` ports
were left citing objects that no longer exist. Nothing was wrong with the
purge; the registers had simply not been carried across it.

The same sweep found three further broken citations that no test currently
asserts. They were repaired too, because a lineage register that silently
cites dead objects is the exact failure mode `PORT-07` exists to prevent.

## Method

For each hex token in the canonical authority files: skip 64-char content
hashes, skip anything that already resolves, then require **exactly one**
prefix match in the validated `filter-repo` commit-map, and require the mapped
SHA to resolve in the rewritten history. Ambiguous or unmappable tokens were
left untouched. Short forms stay short, full forms stay full.

## Remap applied

| file | old | new | occ |
|---|---|---|---|
| `PORT_REGISTER.json` | `5e883c18` | `5b2814cc` | 2 |
| `PORT_REGISTER.json` | `6e4cbccd` | `3bdb099a` | 1 |
| `PORT_REGISTER.json` | `136bd100` | `6e033358` | 3 |
| `PORT_REGISTER.json` | `563ebeb3` | `1dd71d52` | 1 |
| `PORT_REGISTER.json` | `e9d36f5a` | `4a2a9060` | 1 |
| `PORT_REGISTER.json` | `ebed5cba` | `fda31044` | 1 |
| `PORT_REGISTER.json` | `682309f1` | `d08d95e9` | 1 |
| `CANONICAL_PORT_DIFFERENTIAL_AND_PLAN.md` | `204bd4cc` | `0364fe69` | 1 |
| `CANONICAL_REPOSITORY_AUTHORITY_SEAL.json` | `393e1cef` | `66ec0c32` | 1 |
| `CANONICAL_REPOSITORY_AUTHORITY_SEAL.json` | `88aa9d7b` | `25dbcea4` | 1 |
| `EVIDENCE_CUSTODY_INDEX.json` | `393e1cefc3c4399528b6ef6a4b8b8c7822e9fb19` | `66ec0c32c1d5b15d9bd6eccce55728b17d1b79c5` | 1 |
| `GATE_EVIDENCE_UNVERSIONED_CLOSURE.md` | `393e1cefc3c4399528b6ef6a4b8b8c7822e9fb19` | `66ec0c32c1d5b15d9bd6eccce55728b17d1b79c5` | 1 |
| `GATE_EVIDENCE_UNVERSIONED_CLOSURE.md` | `88aa9d7b8f19388b2551896699f0f1e64a3e9bec` | `25dbcea4e7077cfee1d4065f400b40c5b528c963` | 1 |

```
FILES_CHANGED = 5
BROKEN_CITATIONS_REPAIRED = 13 occurrences / 10 distinct commits
AMBIGUOUS_OR_UNMAPPABLE_LEFT_UNTOUCHED = 0
```

Every new SHA was verified to resolve to a `commit` in the rewritten history
before being written. All edited JSON still parses.

## Result

```
before: 2 failed, 426 passed
after:  428 passed
```

## What was deliberately not repaired

`filter-repo/suboptimal-issues` lists 14 abbreviated hashes embedded in
**commit messages**. Commit messages are immutable now that the rewrite is
published, and no test or register asserts them. They are left stale and
recorded in `FILTER_REPO_REPORT.md` rather than papered over.
