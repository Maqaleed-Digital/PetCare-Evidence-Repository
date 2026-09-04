# GCP lane disposition — closing the loop, not the question

**Date:** 2026-09-04 · **Under:** `MVC-W0A-INCIDENT-001`
**Supersedes as a live execution item:** any "GCP Read Pending" continuation label,
any amendment of `GCP_FORENSIC_READ_CARD.md` treated as work-in-flight, and any
current key-rotation workstream on legacy Cloud Run.

## What this record is for

Three consecutive runs re-derived the same credential gate on GCP and stopped there.
The gate is real, but it is not *this* programme's gate: GCP is not a MyVetiCare
infrastructure workstream, and re-deriving its identity wall does not advance the
build. This record fixes the boundary so the next continuation does not resurrect it.

## Disposition

```
GCP_IS_CURRENT_TARGET          = NO
CURRENT_CLOUD_AUTHORITY        = AWS
GCP_ROLE                       = LEGACY_HISTORICAL_PROVENANCE_ONLY

LEGACY_GCP_EXPOSURE            = UNRESOLVED_HISTORICAL
LEGACY_GCP_SERVING             = NO      (measured 2026-09-04T11:29Z)
HISTORICAL_PUBLIC_IAM          = UNRESOLVED_BEHIND_IDENTITY_WALL

PATHFINDER_REFERENCE           = MYVETICARE-PATHFINDER-002
SUPPORT_CASE                   = 71156723
GCP_IAM_READ                   = NOT_AUTHORIZED_AS_CURRENT_EXECUTION_LANE
GCP_CREDENTIAL_GATE            = DO_NOT_REDERIVE

KEY_EXPOSURE_CHANNEL           = PUBLIC_GIT_HISTORY
ROTATION_ON_CLOUD_RUN          = NOT_CURRENT_EXECUTION_ACTION

CP2_EXCLUSION_2_TRIGGERED      = NO_FROM_CURRENT_CHECK
```

## The only permitted GCP-shaped action

One unauthenticated public reachability check against the two legacy endpoints, with
negative controls, capturing status / headers / body / curl exit. Nothing else:
no `gcloud`, no `gcloud auth login`, no IAM read, no dashboard, no rotation, no
deployment, no deletion, no configuration change.

Latest result — `petcare_execution/EVIDENCE/MVC-W0A-EXPOSURE/20260904T112921Z/`:
`API_HTTP=500` (Google Frontend error page, not application output),
`WEB_HTTP=404` byte-identical to both invented controls. Neither returned 200, so
the cloud-agnostic incident trigger did not fire and execution continued.

## Why the historical question stays open rather than closing

`prj-maq-petcare-prod` is stranded in source org `126195085761`. The usable historical
principal sits behind the expired `appstempdomain.goog` identity, and
`admin@maqaleed.tech` is cross-org permission denied. Recovering that identity is
Google-support case `71156723` and belongs to **PATHFINDER-002**, not to this lane.

Consequently `LEGACY_GCP_EXPOSURE` survives as `UNRESOLVED_HISTORICAL`, and it survives
for exactly one reason: CP-2 exclusion 2 is cloud-agnostic. Retiring GCP as a target
does not retire that trigger. But an unresolved historical question is a *parked* item,
not an open execution item, and it must not be re-scheduled as work.

## Artefacts reclassified, not falsified

| Artefact | New status |
|---|---|
| `GCP_FORENSIC_READ_CARD.md` | **PARKED behind PATHFINDER-002.** Preserved verbatim as the read plan a recovered identity would execute. Not a current execution item; no amendment is scheduled. |
| `PRODUCTION_REMEDIATION_PLAN.md` IR-01…IR-02b | **PARKED** — read-only GCP steps, unreachable behind the same identity wall. |
| `PRODUCTION_REMEDIATION_PLAN.md` IR-03…IR-07 | **PARKED / NOT A CURRENT WORKSTREAM.** Rotation and redeploy target a service with no healthy revision on a cloud that is no longer the target. Preserved as history. |
| `W0A_GCP_REACHABILITY_DETERMINATION.md` | Preserved. Its `CP2_EXCLUSION_2_TRIGGERED=NO` is re-confirmed by the 2026-09-04 check. |

Nothing above is deleted or rewritten. The governance model here is append-only
correction: history stays, status changes.

## The exposure that is actually current

The signing-key literal reached the public repository through **git history**, not
through a cloud service. That channel is unaffected by anything on GCP.

Its live half was closed on 2026-09-04: PR #3 merged at `204bd4cc`, and
`origin/main` no longer carries the literal as an active default — it now refuses to
start on it. What remains is the literal in *published history* and at the tips of
several published side branches. Removing it from published history is
`HISTORY_PURGE_PLAN`, classified `GATE_CLASS=GATE-5_IRREVERSIBLE_ACTION`,
`STATUS=NOT_AUTHORIZED_BY_THIS_RUN`.

## Continuation label

- **Old:** `GCP Read Pending`
- **Corrected:** *Legacy-GCP reachability check (unauthenticated only); IAM read parked
  behind PATHFINDER-002.*
