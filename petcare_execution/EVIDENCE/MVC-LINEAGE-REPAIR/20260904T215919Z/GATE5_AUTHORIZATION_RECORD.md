# Gate-5 authorization record — AUTHORIZED, EXECUTION DEFERRED

**Sponsor ruling:** 2026-09-05. **Not executed in this run.**

```
GATE5_AUTHORIZATION = AUTHORIZED
EXECUTION_STATE     = DEFERRED_UNTIL_LINEAGE_REPAIR_PR_MERGED
GATE5_SCOPE         = MAIN_AND_BRANCH_HISTORY
```

Sequenced after this PR lands so settled history is rewritten **once**, not twice.

## Authorized controlled scope — measured, not assumed

Published refs proven to contain `5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96`:

```
origin/main
origin/gate-evidence-prep
origin/m8-brand-cleanup
origin/mvc-ux-wo-001
origin/mvc-ux-wo-002-trust-surfaces
origin/security/w0a-require-session-signing-key
origin/govern/canonical-repository-authority
```

Local-only refs (5): `wave0/w0-a…`, `w0-b…`, `w0-c…`, `w0-d…`, `w0-e…`

Tags carrying: **0 of 7.** Forks: **0** (`network_count=0`). Open PRs: **0**.

## Conditions

1. One bounded `filter-repo` transaction; no unrelated history edits.
2. Preserve every non-secret change.
3. Temporary `main` force-push exception **only** for the purge push.
4. Reapply the exact protection in the same execution block:
   `REQUIRED_CHECK=verify · STRICT=true · ADMIN_ENFORCEMENT=true ·
   ALLOW_FORCE_PUSHES=false · ALLOW_DELETIONS=false`
5. Rewrite the 5 local Wave-0 refs in the same transaction.
6. Verify the literal is absent from every controllable rewritten ref.

## Residuals that no purge can close — state them, do not paper over them

```
refs/pull/1-4/*                     GitHub-controlled; NOT rewriteable by us
UNKNOWN_EXTERNAL_CLONES             = YES
SEARCH_ENGINE_OR_PLATFORM_CACHE     = UNKNOWN
```

A GitHub Support request for persistent PR objects may follow the purge.

**Do not claim universal erasure.** History rewrite reduces discoverability; it
cannot revoke bytes already copied elsewhere. The live risk is already closed —
`MAIN_HEAD_ACTIVE_LITERAL=NO`; this is history remediation, not incident
response.
