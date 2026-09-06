# T0 measurement

The frozen T0 measurement is preserved in the sibling pre-authorization pack
`petcare_execution/EVIDENCE/MVC-GATE5-HISTORY-PURGE/20260906T161932Z/PREAUTH_MEASUREMENT.md`,
recorded read-only before any irreversible act:

```
T0_PUBLISHED_COUNT = 6      (main + 5 non-main)
TAGS_CARRYING      = 0      (of 7 tags)
FORKS              = 0
OPEN_CARRYING_PRS  = 0
REPO_VISIBILITY    = public
refs/pull/1..6/head present (GitHub-managed)

LOCAL_HEADS_CARRYING = 14   (8 local-only + 6 counterparts of published refs)
refs/gate5new = 50 · refs/remotes/gate5mirror = 50 · refs/remotes/gate5probe = 42
refs/stash = da12e50d…  PRESERVE
local main e93e083b… -> commit-map -> 4f36096bbe23de48b61ead9a20446b1b00366774
```

Every number above was **re-measured** in this closeout rather than carried
forward on trust:

| T0 claim | re-measured here |
|---|---|
| local heads carrying = 14 | 14 (`ALL_NAMESPACE_PRE_CLEANUP.md`) |
| gate5probe = 42 / gate5mirror = 50 / gate5new = 50 | identical (`GATE5_SCAFFOLDING_CLEANUP.md`) |
| local main maps to `4f36096b…` | identical (`LOCAL_MAIN_RECONCILIATION.md`) |
| old-history secret blobs = 10, paths = 5 | identical (`OLD_HISTORY_POSITIVE_CONTROL.md`) |
| main head tree identical | identical (`MAIN_HEAD_TREE_IDENTITY.md`) |
| stash preserved, not carrying | identical (`STASH_PRESERVATION.md`) |
