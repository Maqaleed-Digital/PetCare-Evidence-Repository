# Gate register — 2026-09-04, post PORT-07..10

| Gate | Action | Status |
|---|---|---|
| **GATE-3** | Make `verify` a required status check on `main` via GitHub branch protection or a ruleset | **REACHED, NOT EXECUTED** |
| **GATE-5** | Purge the retired signing-key literal from published git history | **PARKED, NOT AUTHORIZED** |
| GATE-1 | live DB / production apply | not reached |
| GATE-2 | credential or key entry | not reached |
| GATE-4 | merge to `main` with incomplete evidence | not reached — no merge attempted |

## GATE-3 — required status check

Measured read-only, mutating nothing:

```
GET /repos/Maqaleed-Digital/PetCare-Evidence-Repository/branches/main/protection
    -> 404 "Branch not protected"
GET /repos/Maqaleed-Digital/PetCare-Evidence-Repository/rulesets
    -> []
```

`main` is unprotected and no rulesets exist. `verify` will run on pull requests
and report, but nothing stops a merge that ignores it — which is precisely the
condition under which PR #3 merged with an empty rollup.

**Desired state**

```
REPOSITORY        = Maqaleed-Digital/PetCare-Evidence-Repository   (PUBLIC)
DEFAULT_BRANCH    = main                                            (measured)
REQUIRED_CHECK    = verify                                          (job id in .github/workflows/verify.yml)
STRICT            = true    — require the branch up to date before merging
ADMIN_ENFORCEMENT = true    — otherwise the gate is advisory for the only person who can bypass it
PR_REQUIREMENTS   = require a pull request before merging; 1 approving review
                    (Sponsor solo lane: confirm whether self-review is acceptable
                     or whether this should be 0 with the check as the gate)
```

`STRICT`, `ADMIN_ENFORCEMENT` and the review count are recommendations, not
measurements — no existing protection or ruleset exists to be consistent with.
They are the Sponsor's to set.

**Prerequisite:** `verify` must have run at least once before GitHub will offer
it as a required check. It runs on push to `govern/**`, so the push in this run
should produce the first execution.

**Why it is Gate 3:** enabling it changes repository configuration through the
GitHub API or console. It is external configuration, not repository content, and
no command that changes protection, rulesets, repository settings or required
status checks was executed.

## GATE-5 — published-history purge

```
PUBLIC_GIT_HISTORY_EXPOSURE_CHANNEL = OPEN
KEY_INTRODUCING_COMMIT              = 5202bb5f  (2026-05-23)
HISTORY_PURGE_STATUS                = GATE-5_NOT_AUTHORIZED
```

`origin/main` no longer carries the literal as an active default — it refuses to
start on it. The literal remains in published history, and four published branch
tips still carry the active default:

```
origin/gate-evidence-prep              FIX=0 ACTIVE_DEFAULT=1
origin/m8-brand-cleanup                FIX=0 ACTIVE_DEFAULT=1
origin/mvc-ux-wo-001                   FIX=0 ACTIVE_DEFAULT=1
origin/mvc-ux-wo-002-trust-surfaces    FIX=0 ACTIVE_DEFAULT=1
origin/main                            FIX=1 ACTIVE_DEFAULT=0
```

Verified read-only. No branch was deleted, no tag removed, no history rewritten,
no force push, no `filter-repo`, no BFG.

Rebasing or retiring those four tips is a smaller, separate decision — and it
would **not** reduce the history exposure, only the tip exposure.
