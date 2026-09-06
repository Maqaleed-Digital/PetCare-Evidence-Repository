# Gate-5 controlled history remediation — closeout run receipt

```
RUN_DATE   = 2026-09-06
RUN_DIR    = petcare_execution/EVIDENCE/MVC-GATE5-HISTORY-PURGE/20260906T174530Z
REPOSITORY = Maqaleed-Digital/PetCare-Evidence-Repository
REPOSITORY_VISIBILITY = PUBLIC
```

## Publication, verified

```
ORIGIN_MAIN                  = 3cef8f9db73a07aab33e953ac7d41c8b238d159d
SPONSOR_PUBLISH_VERIFIED     = YES
NON_MAIN_REMOTE_MAP_VERIFIED = 5/5
```

## Protection

```
PROTECTION_RESTORED           = YES
PROTECTION_RESTORED_IDENTICAL = YES
REQUIRED_CHECK                = verify
REQUIRED_CHECK_APP_ID         = 15368
STRICT                        = true
ADMIN_ENFORCEMENT             = true
ALLOW_FORCE_PUSHES            = false
ALLOW_DELETIONS               = false
PROTECTION_WINDOW_SECONDS     = 15
TEMPORARILY_RELAXED_CONTROLS  = 2  (required_status_checks, allow_force_pushes)
```

## Armed differential

```
OLD_HISTORY_POSITIVE_CONTROL            = 10 blobs
OLD_HISTORY_POSITIVE_CONTROL_PATH_COUNT = 5 paths
POST_PUSH_CARRYING                      = 0
SECRET_BLOBS_REACHABLE_ORIGIN           = 0   (42 refs, 5206 blobs)
INTRODUCING_COMMIT_REACHABLE_OWNED_REFS = NO
PURGE_COMPLETE_OWNED_REFS               = YES
MAIN_HEAD_TREE_IDENTICAL                = YES  (a46ee9f0…)
```

## Local estate

```
ALL_NAMESPACE_PRE_CLEANUP_CARRYING   = 20  (14 heads + 6 gate5probe)
PRUNED_LOCAL_CARRYING                = 3
WAVE0_LOCAL_REFS_UPDATED             = 5/5
PUBLISHED_NONMAIN_LOCAL_REFS_UPDATED = 5/5
LOCAL_MAIN_RECONCILED                = YES  (e93e083b… -> 4f36096b…)
GATE5PROBE_REFS_REMOVED              = 42
GATE5MIRROR_REFS_REMOVED             = 50
GATE5NEW_REFS_REMOVED                = 50
GATE5MIRROR_REMOTE_REMOVED           = YES
STASH_PRESERVED                      = YES
STASH_SECRET_RISK                    = NO
ALL_NAMESPACE_CARRYING_BEFORE_GC     = 0
ALL_NAMESPACE_SECRET_BLOBS_BEFORE_GC = 0
ALL_NAMESPACE_CARRYING_AFTER_GC      = 0
ALL_NAMESPACE_SECRET_BLOBS_AFTER_GC  = 0
```

## Fresh clone

```
FRESH_CLONE_MAIN        = 3cef8f9db73a07aab33e953ac7d41c8b238d159d
FRESH_CLONE_TESTS       = 428 python passed, 0 failed; 120 web unit passed
RESPONSIVE              = 90 passed
SECRET_SCAN             = CLEAN  (3713 scanned, 0 findings)
PROHIBITED_LITERAL_SCAN = CLEAN  (358 scanned, 0 active literal defaults)
EVIDENCE_BUNDLES        = 10 bundles, 76 artefacts, 0 failed
```

## Defect found and repaired during closeout

`main` was **red** after publication: the canonical registers cited pre-rewrite
commit SHAs. Ten `DONE` port citations, plus three further citations no test
asserts, were remapped through the validated commit-map.
See `LINEAGE_CITATION_REMAP.md`. Estate went from `2 failed, 426 passed` to
`428 passed`.

## Residual, stated plainly

```
RESIDUAL_GITHUB_MANAGED_REFS      = refs/pull/1..6/head
RESIDUAL_GITHUB_MANAGED_REF_COUNT = 6
RESIDUAL_PUBLIC_DISCOVERABILITY   = CONFIRMED_ANONYMOUS
UNKNOWN_EXTERNAL_CLONES           = YES
SUPPORT_REQUEST_DRAFTED           = YES  (not submitted)
W0A2_RUNTIME_RISK                 = CLOSED
```

## Not done, deliberately

- `refs/pull/*` not mutated.
- `security/w0a-require-session-signing-key` not deleted — classified
  `NON_DEPLOYABLE`; deletion is a separate future act.
- Stash not dropped.
- No production, live-database, GCP or portfolio-host mutation of any kind.
- GitHub Support request drafted but **not submitted**.
