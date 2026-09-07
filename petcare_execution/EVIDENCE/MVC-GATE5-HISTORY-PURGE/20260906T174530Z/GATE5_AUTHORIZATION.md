# Gate-5 authorization — what authorized this, and what did not

## Authorization source

```
GOVERNING_AUTHORITY     = SPONSOR_POLICY_SCOPED_GATE5_AUTHORIZATION
AUTHORIZATION_SOURCE    = SPONSOR_POLICY_DECISION_LOG
PORTFOLIO_CONTROL_PLANE = NOT_APPLICABLE
```

## Why the portfolio control plane is not the authority here

`MPP-HOST-ISO-001` governs remote *hosts*. Its mutation path is
`portfolio-plan create` -> `portfolio-authorize --plan` -> `portfolio-mutate`,
and `portfolio-mutate` executes against a **host identity receipt**.

A GitHub repository has no host identity receipt. The 2026-09-05 preflight
recorded three concrete failures:

- `myveticare` is not a registered portfolio project (only `almahmoud`, `gwm`,
  `md-web`);
- `repository-governance` is not a valid environment — `portfolio-project next`
  returns `FAIL: unknown environment`;
- `CONTROLLED_HISTORY_REWRITE` is not an action class the control plane knows.

There is therefore no PLAN_ID and no PLAN_SHA256 for `portfolio-authorize` to
bind to. The control plane is **not applicable** to this act — it is not being
bypassed, and no portfolio host was touched at any point in this run.

```
PRODUCTION_MUTATION    = NONE
LIVE_DB_MUTATION       = NONE
GCP_MUTATION           = NONE
PORTFOLIO_HOST_TOUCHED = NONE
```

## What the Sponsor authorized

A single scoped act: rewrite the owned history of
`Maqaleed-Digital/PetCare-Evidence-Repository` to remove a retired `SECRET_KEY`
literal, publish the rewrite, and restore branch protection to an identical
state. The Sponsor performed the publication transaction personally. This run
is the **post-publish closeout**, which is not itself an irreversible act.

## Scope note recorded honestly

The ratified authorization named **five** local Wave-0 refs. The measured local
carrying set was larger — fourteen heads. That delta was flagged in the
2026-09-05 preflight and was never ruled on.

It is resolved in this closeout by **reconciliation, not rewriting**: every
local ref was moved to the SHA that the already-validated `filter-repo`
commit-map assigns it. No new history was created locally, no ref was moved to
a SHA the map did not name, and no additional remote ref was mutated.

See `WAVE0_LOCAL_REF_RECONCILIATION.md` and `LOCAL_PRUNING.md`.
