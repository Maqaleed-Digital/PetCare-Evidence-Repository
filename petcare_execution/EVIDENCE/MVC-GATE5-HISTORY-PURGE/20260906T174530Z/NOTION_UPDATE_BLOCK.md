# Notion-ready update block

```
GATE5_STATUS = PURGE_COMPLETE_OWNED_REFS

AUTHORIZATION_SOURCE    = SPONSOR_POLICY_DECISION_LOG
PORTFOLIO_CONTROL_PLANE = NOT_APPLICABLE
REPOSITORY_VISIBILITY   = PUBLIC

W0A2_RUNTIME_RISK             = CLOSED
OWNED_PUBLISHED_HISTORY_SECRET = REMOVED
OWNED_LOCAL_HISTORY_SECRET     = REMOVED

LOCAL_WAVE0_REFS_REWRITTEN = 5/5
LOCAL_ALL_NAMESPACE_SWEEP  = CLEAN
STASH_PRESERVED            = YES

MAIN_PROTECTION_RESTORED  = YES
REQUIRED_CHECK            = verify
REQUIRED_CHECK_APP_ID     = 15368
PROTECTION_WINDOW_SECONDS = 15

RESIDUAL_GITHUB_MANAGED_REFS    = refs/pull/1..6/head  (6)
RESIDUAL_PUBLIC_DISCOVERABILITY = CONFIRMED_ANONYMOUS
UNKNOWN_EXTERNAL_CLONES         = YES
SUPPORT_REQUEST_REQUIRED        = YES

SECURITY_LANE_STATUS  = CLOSED_FOR_OWNED_HISTORY
CP2_DECISION_LOG_LODGED = YES
```

**Do not create another CP-2 row.** This updates the existing one.

## One-paragraph summary

The retired `SECRET_KEY` literal has been removed from all owned history of the
public repository `Maqaleed-Digital/PetCare-Evidence-Repository`. An armed
fingerprint scanner that finds 10 carrying blobs across 5 paths in the retained
old history finds **zero** across all 42 owned origin branches and across every
local namespace, before and after garbage collection. The introducing commit is
unreachable from every owned ref. `main`'s head tree is byte-identical to its
pre-purge tree, so the rewrite changed history and not code. Branch protection
was restored byte-identically, with `verify` / `app_id 15368` rebound, after a
15-second window that relaxed exactly two controls. Six GitHub-managed
`refs/pull/*/head` refs still expose the literal and are **anonymously
fetchable**; they cannot be rewritten by us, a Support request is drafted, and
external clones cannot be recalled — so the control that actually closes the
runtime risk is the W0-A2 fingerprint guard, which rejects the retired key
without holding it. A rewrite-induced defect was found and fixed in the same
run: the canonical registers cited pre-rewrite commit SHAs and had left `main`
red; they were remapped through the validated commit-map and the estate is
green at 428 tests.
