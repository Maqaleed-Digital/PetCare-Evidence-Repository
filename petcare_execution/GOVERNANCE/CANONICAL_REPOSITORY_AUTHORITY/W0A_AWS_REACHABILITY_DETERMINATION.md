# W0-A vulnerable artefact — AWS reachability determination

**Date:** 2026-09-03 · **Scope:** AWS only (GCP retired by instruction, not inspected)
**Authority:** MVC-GOV-CANON-001

## Result

```
AWS_EXPOSURE_CLASSIFICATION = CLASS_A_NOT_PRESENT_IN_AWS
OVERALL_EXPOSURE            = CLASS_E_INDETERMINATE
CP2_EXCLUSION_2_TRIGGERED   = NO
```

Those two lines are not in conflict, and the difference between them is the
whole finding. **MyVetiCare has no presence in AWS at all**, so AWS cannot have
served the vulnerable image. But AWS is not where the image went.

## What the primary source actually says

W0-A's commit message states the image "was built and pushed to a production
**Artifact Registry**". Artifact Registry is a Google Cloud service; the AWS
equivalent is ECR. The same message defers the *future* secret store to an "AWS
architecture decision", which is how both clouds come to appear in one paragraph.

Repository evidence settles which one carried the artefact:

| Evidence | Finding |
|---|---|
| `petcare_api/cloudbuild.yaml` | builds and pushes `me-central2-docker.pkg.dev/prj-maq-petcare-prod/petcare-artifacts/petcare-api:latest` |
| `petcare_web/cloudbuild.yaml` | same pattern |
| Terraform files | **0** |
| ECS task definitions | **0** |
| buildspec / appspec | **0** |
| `AWS_PRODUCTION_RUNBOOK/` | a runbook and plan — no deployed resource |

The only recorded build-and-push path for the vulnerable image is GCP Cloud
Build into GCP Artifact Registry.

## AWS search performed (read-only)

Accounts reachable: `822127611052` (stage-a / stage-b) and `293528978461`
(legacy). 25 regions enumerated from `ec2 describe-regions`.

| Region | ECR repositories |
|---|---|
| me-central-1 | `s2ppro-production`, `prowork-production`, `societa-production` |
| eu-central-1 | `s2ppro-production`, `md-web-preprod`, `societa-production` |
| eu-west-1, us-east-1 | none |
| me-south-1 | **endpoint connect timeout — not searched** |
| legacy account (me-central-1, eu-central-1, us-east-1) | none |

ECS clusters, eu-central-1: `workcaptain-production`, `societa-production`,
`s2ppro-production`, `md-web-preprod`. me-central-1: none.

**No `petcare-*` ECR repository and no petcare ECS cluster exists in either
account.** The AWS estate runs other Maqaleed projects only.

### Exhaustive sweep

The table above came from targeted checks. A subsequent sweep of **all 25
enumerated regions across both accounts** returned ECR repositories in exactly
two regions — `me-central-1` and `eu-central-1`, both under `822127611052` — and
ECS clusters in exactly one, `eu-central-1`. The legacy account `293528978461`
returned **no ECR repository in any region**. Nothing named `petcare` appeared
anywhere.

That sweep does **not** upgrade region coverage to complete, and the reason is
worth stating plainly: it suppressed stderr, so an unreachable region and an
empty region produce identical silence. `me-south-1` timed out under the
targeted check, and in the sweep it is indistinguishable from a region that
simply holds nothing. Silence is not absence. Coverage therefore remains 24 of
25 and `PROVEN_NONE` remains `NO` on that count as well as on the larger one.

```
VULNERABLE_ECR_IMAGE_FOUND            = NO
VULNERABLE_IMAGE_EXECUTED (in AWS)    = NO
CURRENTLY_RUNNING_VULNERABLE_IMAGE    = NO
PUBLICLY_REACHABLE (in AWS)           = NOT_APPLICABLE
REGION_COVERAGE_COMPLETE              = NO  (me-south-1 unreachable)
PROVEN_NONE                           = NO
```

## Why `PROVEN_NONE = NO`

Two reasons, and neither is a technicality.

1. `me-south-1` timed out, so coverage is 24 of 25 regions. The residual is
   implausible — a petcare image cannot appear in a region when no AWS build
   path exists at all — but implausible is not proven.
2. More importantly, **an AWS-clean result does not answer the exposure
   question.** The artefact's recorded home is GCP Artifact Registry. Searching
   AWS and finding nothing is a true statement about the wrong cloud. Recording
   this as "no exposure" would be a false negative on a security question, which
   is precisely the `UNKNOWN → NO` conversion this lane forbids.

## What remains open

The image was tagged `:latest`, which is mutable. Even with access, digest
identity for the pre-W0-A build may no longer be recoverable from the tag alone;
it would have to come from Cloud Build history.

```
GCP_ARTIFACT_REGISTRY_EXPOSURE = NOT_ASSESSED (out of scope by instruction)
RESIDUAL_GATE = GCP_ARTEFACT_DISPOSITION_DECISION
```

If the GCP project is genuinely retired **and its Artifact Registry and any
Cloud Run services were torn down**, the exposure is closed by decommissioning
and this residual can be closed with that evidence. If the project still exists
and still serves, the exposure is live and unassessed. Which of those is true is
not determinable from inside this repository.
