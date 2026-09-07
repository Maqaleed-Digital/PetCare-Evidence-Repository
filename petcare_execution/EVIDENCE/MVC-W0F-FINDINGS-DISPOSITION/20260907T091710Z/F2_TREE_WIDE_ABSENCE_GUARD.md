# F2 — absence guard widened from three directories to the tree

**Finding.** W0-F acceptance criterion 3 claims no `pharmacy_operator`
"anywhere in the tree". The guard enforcing it
(`petcare_web/__tests__/absence-guards.test.ts`) scanned
`petcare_web/{app,components,lib}` — three directories of one application. The
claim was far wider than its enforcement.

## AC3 taken literally is unachievable — and undesirable

A guard that forbids the role must name it. The governance decision that retires
it must quote it. Sealed evidence recording the retirement contains it by
construction. A literal tree-wide zero would require falsifying the record.

The enforceable form is two-sided, and both sides are now asserted:

```
live source       ZERO occurrences, no exceptions, no register entry exempts
everywhere else   every occurrence explicitly REGISTERED, with a reason
```

## Live source trees — zero tolerance

```
petcare_api
petcare_web/app
petcare_web/components
petcare_web/lib
petcare_runtime/src
scripts
```

One live occurrence was found and **removed**: two dead
`assigned_pharmacy_operator_id` fields in
`petcare_runtime/src/petcare/auth/access_control.py`. They were declared on
`AccessContext` and `ResourceContext` and read by nothing — no policy decision,
no call site passed them. `petcare_runtime` is 234 green before and after.

Live occurrences now: **0**.

## Exclusions — path-specific, each justified

| Path | Reason |
|---|---|
| `.git` | version control internals, not source |
| `node_modules` | third-party dependencies |
| `__pycache__` | bytecode regenerated from source already scanned |
| `.claude-flow` | agent tooling state, not repository content |
| `petcare_execution/EVIDENCE` | sealed evidence; rewriting it to satisfy a scanner would falsify the record |
| `petcare_execution/GOVERNANCE` | governance prose, including the register itself; a decision retiring a role must name it |

No wildcard. Nothing that could hide a live source tree. The four guard files
that must name the needle are listed explicitly, not pattern-matched.

## Everything else must be registered

Fourteen artefacts outside live source carry the role. Each is registered in
`RETIRED_ROLE_CUSTODY_REGISTER.json` with a classification and a reason:

- **4 × `STALE_DESIGN_ARTEFACT`** — AI_RUNTIME orchestrator/integration TypeScript
  that models the role as authorization. These carry an in-file marker (F3).
- **5 × `HISTORICAL_CONTRACT_RECORD`** — API contracts and RBAC matrices that
  predate W0-D. Adding keys to a contract record to satisfy a scanner would
  alter the contract, so these are registered rather than edited.
- **5 × `HISTORICAL_CHECKLIST_KEY`** — go-live checklist keys such as
  `pharmacy_operator_ready`. These carry the string as a past process step, not
  as an authorization role.

An unregistered occurrence fails the guard. Retention is permitted; silent
retention is not.

## Measured

```
ABSENCE_GUARD_SCOPE=TREE_WIDE
ABSENCE_GUARD_EXCLUSIONS=6 (all path-specific and justified)
LIVE_SOURCE_OCCURRENCES=0
REGISTERED_ARTEFACTS=14
ABSENCE_GUARD_PERTURBATION_PASS=YES
```
