# MVC-W0F-READINESS — post-Gate-5 estate re-measurement

**Run:** `20260907T082004Z` · **Authority:** MVC-GOV-CANON-001
**Base:** `8c3c63d6c5c8ef8b74cee0c61b67ea1e4dbb6d45` (`main`, after Gate-5 closeout PR #7)
**Cloud authority:** AWS (GCP `RETIRED_HISTORICAL`)

## What this run is, and what it is not

`MVC-W0F-ENGINEERING-HANDOFF-001` sets `W0_F_AGENT_IMPLEMENTATION=NO` and states
that no agent lane may implement the serving-layer replacement. That boundary was
kept. **No part of W0-F was implemented in this run.**

This run does the work that sits *around* that boundary: re-measure the estate
after the Gate-5 closeout, prove the guards are still armed, and record what a
W0-F engineering team will find when it picks the work up.

**This run changes no code and no governance register.** It adds evidence only.

## A correction, recorded because it is the finding

The run began against a **stale local `main` at `3cef8f9`**, which predated the
Gate-5 closeout merge. Measured there, `tests/governance::test_every_done_port_cites_a_closing_commit_that_is_a_real_object`
was failing: all ten DONE rows of `PORT_REGISTER.json` cited commits orphaned by
the history rewrite.

That failure is **not present on the real `main`**. Gate-5 closure (PR #7) had
already re-anchored every citation, and records the work in
`MVC-GATE5-HISTORY-PURGE/20260906T174530Z/LINEAGE_CITATION_REMAP.md`.

The remap was nonetheless re-derived here independently — from the current commit
graph, verifying each candidate resolves to a real commit, is reachable from
`main`, and touched the files its row declares as `targets`. The result is
**byte-identical** to what PR #7 landed (both produce blob `edc0d67`), across all
seven distinct SHAs and ten rows. Two independent derivations agreeing is
worthwhile corroboration of the remap, so it is recorded in
`PORT_LINEAGE_REPAIR.md` — as confirmation, not as a repair.

The operational lesson is the ordinary one: measure against the remote, not a
local branch that has not been fetched.

## Estate re-measured (the pack's counts are stale)

| Suite | Pack states | Measured now |
|---|---|---|
| `petcare_api/tests` | 46 | **51** |
| `petcare_web` vitest | 85 | **120** |
| `petcare_web` Playwright | 90 | **90** |
| `tests/` (governance + regression) | not stated | **143** |
| **Total** | — | **404 green, 0 failed** |

`partner_network` is **36** modules, not the 37 the pack states; the pack counted
a directory listing that included `__pycache__`. EP-07 seal is unaffected.

The pack carries `DENOMINATOR_STATUS=RELAYED_NOT_REMEASURED`, so these drifts are
consistent with its own declared caveat rather than a contradiction of it.

## Guards proven armed by perturbation

| Guard | Perturbation | Failures | Restored |
|---|---|---|---|
| W0-A / W0-A2 | reintroduce a literal default in `_require_secret_key()` | **4** | clean |
| PORT-01 | reintroduce `pharmacy_operator` into a scanned source | **1** | clean |

W0-A now fails **4**, not the 3 the pack records — W0-A2 added the AST ordering
check. Both perturbations were reverted and the tree verified clean.

## Acceptance criteria — measured status

| # | Criterion | Status |
|---|---|---|
| 1 | api tests green, guards armed | **MET** (51 green, armed by perturbation) |
| 2 | web green, `ASSERTIONS_WEAKENED=0` | **MET** (120 vitest + 90 Playwright) |
| 3 | no `pharmacy_operator` anywhere | **NOT MET AS WORDED** — see F-1 |
| 4 | identity persists across restart/instances | **BLOCKED** — W0-F substrate |
| 5 | tenant assignment survives migration | **BLOCKED** — W0-F substrate |
| 6 | `SECRET_KEY` from governed storage | **BLOCKED** — `GATE_CREDENTIAL_ENTRY` |
| 7 | session revocation decided | **BLOCKED** — sponsor decision, not agent work |
| 8 | memory-hard KDF | **BLOCKED** — credential migration |
| 9 | rollback rehearsed against restore | **BLOCKED** — `GATE_LIVE_APPLY` |
| 10 | marketplace consumed, not duplicated | **MET** — `MARKETPLACE_SEAM_WIRED = false` |

Seven of ten criteria are blocked behind a gate or behind the agent boundary.
That is the honest answer to "what safe W0-F implementation work is available
now": essentially none. The substrate itself is the forbidden part, and the
criteria that do not touch it are already met.

## Findings handed to the engineering team — not actioned here

**F-1 · AC3's guard is narrower than AC3's claim.** AC3 says "no
`pharmacy_operator` anywhere in the tree". The guard enforcing it
(`petcare_web/__tests__/absence-guards.test.ts`) scans only
`petcare_web/{app,components,lib}`.

Live residue outside that scope: two dead `assigned_pharmacy_operator_id`
dataclass fields in `petcare_runtime/src/petcare/auth/access_control.py`,
declared and never read by any policy decision. **No live authorization path
grants the retired role.**

Also present, and *not* live code: `.ts` files under
`petcare_execution/AI_RUNTIME/` still model `pharmacy_operator` as a first-class
role, including a `policy_enforcer.ts` that would grant it dispensing authority.
There is no `tsconfig.json` or `package.json` anywhere under `petcare_execution`,
so nothing compiles, type-checks or runs these. They are design artifacts
carrying a reversed W0-D decision in prose form, not an exploitable grant.

Deciding what "the tree" means for AC3 is a governance judgment under
MVC-GOV-CANON-001, so the guard's scope was left alone rather than widened
unilaterally.

**F-2 · GCP build configuration survives under AWS authority.** Six
`cloudbuild.yaml` files remain (`petcare_api/`, `petcare_web/`, four under
`petcare_execution/PHASE_2/`). No guard asserts their absence. Removing delivery
configuration is a deployment-path change and was not taken unilaterally.

## Boundary

Not crossed: production datastore choice · residency `D.21` · identity migration ·
live production mutation · Gate-5 · GCP as a target.
