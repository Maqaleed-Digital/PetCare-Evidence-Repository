# F3 — `policy_enforcer.ts`: stale design artefact, not a live grant

## Classification

```
POLICY_ENFORCER_CLASSIFICATION=STALE_DESIGN_ARTEFACT
NOT_LIVE_AUTHORIZATION
```

`petcare_execution/AI_RUNTIME/orchestrator/policy_enforcer.ts` contains:

```ts
return actorRole === "veterinarian" || actorRole === "pharmacy_operator";
```

which grants dispensing authority to the role W0-D retired.

**It is not a runtime exposure, and this record does not claim one.** There is no
`tsconfig.json` and no `package.json` anywhere under `petcare_execution/`. The
only TypeScript projects in the repository are `petcare-web` and `petcare_web`.
Nothing compiles, type-checks, bundles or executes this file. It grants no
authority to anything.

What it is, is a design record that contradicts a current security decision in
prose — which is a real governance defect, because the next person to build from
it would reverse W0-D.

## Disposition chosen, and why

The instruction offered two routes: align the artefact's semantics with W0-D, or
prepend an explicit stale marker.

**The marker was chosen.** Editing the logic would silently convert a historical
design record into something that looks like a current, correct specification —
destroying the evidence that this reversal was ever contemplated, while leaving
the file looking authoritative. The repository's governance convention throughout
is append-and-mark, not rewrite: the Gate-5 preflight correction, the W0-F count
correction, and the sealed evidence bundles all follow it.

Marker prepended to the four AI_RUNTIME artefacts that model the role as
authorization:

```
STATUS=STALE_DESIGN_ARTEFACT
SUPERSEDED_BY=W0-D
PHARMACY_OPERATOR_DISPENSING=RETIRED
DO_NOT_IMPLEMENT_FROM_THIS_FILE
```

| File | Why it carries the role |
|---|---|
| `orchestrator/policy_enforcer.ts` | grants dispensing to the retired role |
| `orchestrator/types.ts` | declares it in the actor-role union |
| `orchestrator/agent_runtime_controller.ts` | branches on it in dispatch |
| `integration/synthetic_requests.ts` | asserts it as an actor in a fixture |

## Guard

`tests/governance/test_retired_role_absence.py` enforces both halves:

- the role may appear in an artefact registered as stale or historical;
- it must **fail** if the role appears in any live source tree;
- an artefact registered as carrying an in-file marker must actually carry one,
  so the marker cannot be quietly stripped.

## Measured

```
POLICY_ENFORCER_DISPOSITION=IN_FILE_STALE_MARKER + REGISTERED
LIVE_PHARMACY_OPERATOR_GRANTS=0
```
