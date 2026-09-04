# W0-A vulnerable artefact — GCP reachability determination

**Date:** 2026-09-03 · **Authorization:** `MVC-GCP-FORENSIC-READ-001` (read-only, approved)
**Project:** `prj-maq-petcare-prod` · **Authority:** MVC-GOV-CANON-001

## Result

```
GCP_READ_STATUS               = BLOCKED_CREDENTIAL_GATE
GCP_EXPOSURE_CLASSIFICATION   = CLASS_G6_INDETERMINATE
OVERALL_EXPOSURE              = CLASS_E_INDETERMINATE   (unchanged)
PROVEN_NONE                   = NO
CP2_EXCLUSION_2_TRIGGERED     = NO
GATE                          = GCP_READ_CREDENTIAL_ENTRY_REQUIRED
```

The forensic read was authorized and was attempted. It could not be performed.

## What was attempted

`gcloud` is installed (SDK 563.0.0) and three accounts hold stored credentials:

| Account | Result |
|---|---|
| `waheeb@gwmest.com` (active) | reauthentication required |
| `admin@maqaleed.tech` | reauthentication required |
| `admin_maqaleed.tech@…appstempdomain.goog` | reauthentication required |

Each was tried explicitly with `--account=`, which selects an existing
credential without mutating local gcloud config and without any login. All three
returned:

> `There was a problem refreshing your current auth tokens: Reauthentication
> failed. cannot prompt during non-interactive execution.`

The refresh tokens have expired. Recovering them requires `gcloud auth login`,
which is **explicitly withheld** by `MVC-GCP-FORENSIC-READ-001` and is in any
case impossible in a non-interactive session. An `application_default_credentials.json`
exists but dates from 2026-05-31 and is subject to the same expiry.

**No project query was issued.** `projects describe` failed at the auth layer,
so not even project existence was established.

## What this determination does and does not say

It says only that the question remains open. Specifically **not** established:

```
PROJECT_EXISTS                        = UNKNOWN
VULNERABLE_IMAGE_DIGEST               = UNKNOWN
VULNERABLE_IMAGE_PRESENT              = UNKNOWN
VULNERABLE_IMAGE_EXECUTED             = UNKNOWN
PUBLICLY_REACHABLE                    = UNKNOWN
SESSION_ISSUANCE_EVIDENCE             = UNKNOWN
REQUEST_LOGS_PRESENT                  = UNKNOWN
LOG_WINDOW_COVERS_VULNERABLE_INTERVAL = UNKNOWN
LOG_EVIDENCE_AT_RISK                  = UNKNOWN
```

Every one of these is `UNKNOWN`, not `NO`. A credential gate produces silence,
and silence is not absence. This is the same discipline applied to the AWS
result: `CLASS_A_NOT_PRESENT_IN_AWS` is true and does not close the exposure.

## Why product work continues

`CP2_EXCLUSION_2_TRIGGERED = NO`. The incident override fires only on
`PUBLICLY_REACHABLE=YES` **and** `VULNERABLE_IMAGE_EXECUTED=YES`. Neither is
proven, so the override does not fire and PORT work proceeds. That is not a
finding of safety — it is the absence of a proven incident.

## Time sensitivity

This is the one part of the residual that decays. If the vulnerable service ever
served publicly, the evidence that would show it — request logs, audit logs,
Cloud Build records — sits under retention policies that expire. `LOG_EVIDENCE_AT_RISK`
is `UNKNOWN` precisely because the retention window could not be read. Every day
the credential gate stays shut, the chance that the question becomes permanently
unanswerable rises.

Deleting or tearing down the project would also destroy that evidence.
**Teardown is not closure**, and doing it before classification would convert an
open question into a permanently indeterminate one.

## To close this

One of:

1. An operator runs `gcloud auth login` for an account with read access to
   `prj-maq-petcare-prod`, after which this determination can be completed
   read-only under the existing authorization; or
2. Documented evidence that the project and its Artifact Registry and Cloud Run
   services were decommissioned, with dates — in which case the exposure closes
   by decommissioning and this becomes `CLASS_G1`.

Absent either, the classification stays `CLASS_G6_INDETERMINATE`.
