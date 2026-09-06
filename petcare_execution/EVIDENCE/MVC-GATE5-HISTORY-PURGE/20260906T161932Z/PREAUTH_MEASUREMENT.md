# Gate-5 pre-authorization measurement — read-only

Nothing was rewritten, force-pushed, deleted or reconfigured.

```
REMOTE_MUTATED = NO · PROTECTION_MUTATED = NO
IRREVERSIBLE_HISTORY_ACTION_PERFORMED = NO
```

## T0 — live vs frozen (all six match)

| ref | frozen OLD | live | rewritten target |
|---|---|---|---|
| main | 24de5399…5ad1 | MATCH | 3cef8f9db73a07aab33e953ac7d41c8b238d159d |
| gate-evidence-prep | c88d9f15…47a0 | MATCH | 4986725505de0af9e37b2854c170e364b1075cff |
| m8-brand-cleanup | a3cba7ba…4210 | MATCH | 770eb193fda6cdcbe41a7fa19e9b8caafb02bd23 |
| mvc-ux-wo-001 | ed4e0e36…d2cc | MATCH | 2e9c070468316b0cc6b3d259dd973b6606ea4e41 |
| mvc-ux-wo-002-trust-surfaces | 2b3e7b2a…5e53 | MATCH | 2e06ecf992a40ddd5b54ce13189755b1b6ec9351 |
| security/w0a-require-session-signing-key | 9fc8e249…5b65f | MATCH | a838d9f2b43e7cdcee659fab9729915533b78884 |

T0_PUBLISHED_COUNT=6 · TAGS_CARRYING=0 (of 7 tags) · FORKS=0 · OPEN_CARRYING_PRS=0
REPO_VISIBILITY=public · refs/pull/1..6/head present (GitHub-managed)

## Security invariants — armed differential, same scanner and same needle

```
OLD_POSITIVE_CONTROL      BLOBS=4879 SECRET_BLOBS=10 PATHS=5
REWRITTEN_CONTROLLED_REFS BLOBS=4879 SECRET_BLOBS=0  PATHS=0
```

The needle is recovered by fingerprint-window search over a proven carrier
(pre-rewrite `main`), then reused verbatim for both runs. The rewritten run is
therefore an armed zero, not a needle-not-found vacuity — an earlier revision of
the scanner seeded from the target set and reported
`NEEDLE_NOT_RECOVERED_FROM_SEED`, which would have read as a pass.

Carrying paths in old history:

- `petcare_api/routers/auth.py`
- `petcare_api/tests/test_secret_key_required.py`
- `petcare_api/tests/test_w0_ab_ordering_invariant.py`
- `petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/NOTION_AUTHORITY_SYNC.md`
- `tests/governance/test_repository_scanners.py`

Introducing commit `5202bb5f…0dc96` is unreachable from all six rewritten refs
and reachable from the old refs, so that test is armed too.

## Head-tree identity

```
main  HEAD_TREE_IDENTICAL = YES  (a46ee9f034882eab0bd730b3cf59e5df5c5a1c67 both sides)
```

Non-main refs legitimately differ. The changed-path audit shows the rewrite
touched only:

- four refs — `petcare_api/routers/auth.py` alone;
- `security/w0a-require-session-signing-key` — `petcare_api/routers/auth.py`
  **and** `petcare_api/tests/test_secret_key_required.py`.

That second file is implementation-and-its-test edited in step — the exact
signature the W0-A2 guard docstring names as the disarming pattern. It is
confined to one historical branch tip. `main`'s tree is byte-identical to the
post-PR-#6 merge commit, so the guard is provably armed at `main`.

## Protection baseline — read independently, matches the required state

```
strict=true · checks=[{context:verify, app_id:15368}] · admins=true
reviews=null · restrictions=null · force=false · deletions=false
linear=false · conversation_resolution=false · block_creations=false
lock_branch=false · fork_syncing=false
```

`window.json` relaxes exactly two controls (`required_status_checks`,
`allow_force_pushes`). `restore.json` rebinds `verify` / `app_id 15368`.

## Local blast radius

```
LOCAL_HEADS_CARRYING = 14  (8 local-only + 6 counterparts of published refs)
refs/gate5new = 50 · refs/remotes/gate5mirror = 50 · refs/remotes/gate5probe = 42
refs/stash = da12e50d… PRESERVE
local main e93e083b… -> commit-map -> 4f36096bbe23de48b61ead9a20446b1b00366774
```

## Blockers reached — no irreversible step attempted

1. **No authorizable plan exists.** `myveticare` is not a registered portfolio
   project (only `almahmoud`, `gwm`, `md-web`); `repository-governance` is not a
   valid environment — `portfolio-project next` returns
   `FAIL: unknown environment`; `CONTROLLED_HISTORY_REWRITE` is not an action
   class the control plane knows. `portfolio-mutate` executes over SSH against a
   host identity receipt, which a GitHub repository does not have. Sections 8, 9
   and 11 are unexecutable as written: there is no PLAN_ID and no PLAN_SHA256 for
   `portfolio-authorize --plan` to bind to.

2. **Mirror status is contradicted in writing.** `GATE5_RESUME_CONDITIONS.md`
   and `GATE5_PREFLIGHT.md` both condemn the mirror at `~/dev/gate5-mirror.git`
   as `DISCARDED_INVALID`, never to be pushed, to be deleted before the next
   attempt. But its `filter-repo` run is dated 2026-09-05T12:46:42Z — after
   PR #6 merged at 09:44:32Z — and its commit-map is keyed on `24de5399`, so it
   is in fact the post-merge clone the resume conditions call for, and it passes
   every admissible-rewrite test above. Sponsor ruling required.

3. **Local-ref scope delta, still unresolved.** The ratified authorization names
   five local Wave-0 refs; the transaction must cover eight local-only carrying
   refs. Flagged in the 2026-09-05 preflight, never ruled on.
