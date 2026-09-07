# Local pruning — measured, not assumed

```
PRUNED_LOCAL_CARRYING = 3
```

## The containment test had to be corrected

The naive test — "zero commits unique versus `origin/main`" — is **wrong after a
history rewrite**. Every old commit has a new SHA, so `git rev-list --count
<branch> ^origin/main` counts the branch's entire old history and reports 42, 44
and 46 for three branches that are in fact fully merged.

Measured naively, all three candidates read as `contained=NO` and would have
been retained.

The correct test maps the branch tip through the commit-map first, then asks
whether the **mapped** tip is contained in `origin/main`. That is what was used.

## Candidates, measured

| ref | OLD | MAPPED | reaches introducing commit | mapped contained in `origin/main` | unique commits | action |
|---|---|---|---|---|---|---|
| `govern/canonical-repository-authority` | `793c64b93b86cce35b7ad06044de12015ce6721c` | `06341f9905b3db4d1458c9640313e44d9dc43d1f` | YES | YES | 0 | **DELETED** |
| `govern/denominator-inventory` | `b8b5014e5a1f6848cfb6022034c77485dc2c0f3b` | `710ecbe548682efe16c439a695e31fa43e895773` | YES | YES | 0 | **DELETED** |
| `security/w0a2-fingerprint-guard` | `e78159b285a7719759941421941b04ef0ab08ee1` | `0085cc18dc1c9bc53fcf648a2029f10373807caf` | YES | YES | 0 | **DELETED** |

All three satisfied every criterion: not `main`, reaches the introducing commit,
mapped tip fully contained in rewritten `origin/main`, zero unique commits, no
independent held work. Their content is already in `main` via merged PRs #4, #5
and #6.

## What was not touched

- The 28 `petcare/*` and `conflict_*` local branches — none reaches the
  introducing commit; none was modified or deleted.
- `refs/stash` — preserved (`STASH_PRESERVATION.md`).
- `refs/tags/*` — 7 tags, none carrying, none touched.
- The five published non-main heads — reconciled, not deleted
  (`WAVE0_LOCAL_REF_RECONCILIATION.md`).
