# MVC-W0F-READINESS — post-Gate-5 re-measurement and lineage repair

**Run:** `20260907T082004Z` · **Authority:** MVC-GOV-CANON-001
**Start head:** `3cef8f9db73a07aab33e953ac7d41c8b238d159d`
**Cloud authority:** AWS (GCP `RETIRED_HISTORICAL`)

## What this run is, and what it is not

`MVC-W0F-ENGINEERING-HANDOFF-001` sets `W0_F_AGENT_IMPLEMENTATION=NO` and states
that no agent lane may implement the serving-layer replacement. That boundary was
kept. **No part of W0-F was implemented in this run.**

What this run did is the work that sits *around* that boundary and does not cross
it: re-measure the estate after the Gate-5 closeout, prove the guards are still
armed, and repair one defect that the re-measurement exposed on `main`.

## The defect found on main

`tests/governance/test_canonical_register_integrity.py::test_every_done_port_cites_a_closing_commit_that_is_a_real_object`
was **failing on `main`**. All ten DONE rows of `PORT_REGISTER.json` cited closing
commits that are not objects in this repository.

Cause: the citations are pre-rewrite SHAs. The frozen OLD `main` (`24de5399…`) is
likewise absent and the current head is the rewrite target recorded in
`MVC-GATE5-HISTORY-PURGE/20260906T161932Z/PREAUTH_MEASUREMENT.md`. The history
rewrite reassigned every SHA and the register was never re-anchored, so ten
governance citations were left dangling.

This is a provenance break, not a behaviour break. The ported behaviours are all
present and tested; only the proof-of-landing pointers were stale.

## The repair

Each stale citation was re-anchored to the commit that carries the same change in
current history. The mapping is in `PORT_LINEAGE_REPAIR.md`. Every mapping was
verified independently of the source it was looked up from: each target must be a
real commit, reachable from `main`, and must have touched the files that row
declares as its targets. All ten satisfy all three.

The register's 8-character citation convention was preserved. Abbreviations are
unambiguous at these values and full SHAs would not have prevented this failure
mode — a rewrite reassigns full SHAs too.

## Estate re-measured (the pack's counts were stale)

| Suite | Pack states | Measured now |
|---|---|---|
| `petcare_api/tests` | 46 | **51** |
| `petcare_web` vitest | 85 | **120** |
| `petcare_web` Playwright | 90 | **90** |
| `tests/` (governance + regression) | not stated | **143** |
| **Total** | — | **404 green** |

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
| 3 | no `pharmacy_operator` anywhere | **NOT MET AS WORDED** — see below |
| 4 | identity persists across restart/instances | **BLOCKED** — W0-F substrate |
| 5 | tenant assignment survives migration | **BLOCKED** — W0-F substrate |
| 6 | `SECRET_KEY` from governed storage | **BLOCKED** — `GATE_CREDENTIAL_ENTRY` |
| 7 | session revocation decided | **BLOCKED** — sponsor decision, not agent work |
| 8 | memory-hard KDF | **BLOCKED** — credential migration |
| 9 | rollback rehearsed against restore | **BLOCKED** — `GATE_LIVE_APPLY` |
| 10 | marketplace consumed, not duplicated | **MET** — `MARKETPLACE_SEAM_WIRED = false` |

## Findings handed to the engineering team — not actioned here

**F-1 · AC3's guard is narrower than AC3's claim.** AC3 says "no
`pharmacy_operator` anywhere in the tree". The guard enforcing it
(`absence-guards.test.ts`) scans only `petcare_web/{app,components,lib}`. Live
residue outside that scope: two dead `assigned_pharmacy_operator_id` dataclass
fields in `petcare_runtime/src/petcare/auth/access_control.py`, declared and never
read by any policy decision. No live authorization path grants the retired role.

Also present, and *not* live code: `.ts` files under `petcare_execution/AI_RUNTIME/`
still model `pharmacy_operator` as a first-class role, including a
`policy_enforcer.ts` that would grant it dispensing authority. There is no
`tsconfig.json` or `package.json` anywhere under `petcare_execution`, so nothing
compiles, type-checks or runs these — they are design artifacts carrying a
reversed W0-D decision in prose form, not an exploitable grant.

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
