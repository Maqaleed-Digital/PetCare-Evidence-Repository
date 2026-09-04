# MVC-W0A-INCIDENT-PRESERVATION-001

**Date:** 2026-09-03 · **Mode:** read-only preservation and classification
**Canonical repo:** `~/dev/petcare-evidence-repository` · **Branch:** `govern/canonical-repository-authority`
**HEAD at capture:** `016bd766d5a089811ad313a9cca0d57fc674b0ca`
**NO PRODUCTION MUTATION PERFORMED.**

## Headline

The escalation was raised on the reading that an anonymous `500` proved a caller had
reached the vulnerable service. Two independent checks change that picture — one
weakens the incident, one strengthens a different finding.

**Weakened.** The vulnerable code did not exist when the only documented production
deployment happened. `petcare_api/routers/auth.py` was created 2026-05-23; PH5.1
recorded PRODUCTION_ACTIVE on 2026-04-06. `VULNERABLE_IMAGE_EXECUTED` reverts
**YES → UNKNOWN**.

**Strengthened.** The retired literal is not merely *in public history* — it is in the
**default branch of a public repository today**, and the W0-A fix has never been
pushed. That is a live, confirmed, unremediated exposure independent of any deployment.

**Corrected.** The `500`/`503` bodies are Google Frontend error pages, not application
output; steady state is `503` on every path including random ones. No application is
serving. What the negative controls *do* establish is that the API service object
exists and emitted no IAM denial.

## Determination

```
NOTION_AUTHORITY_SYNC              = COMPLETE (prior run, HEAD 016bd766) — 3 contradictions
PRODUCT_REQUIREMENTS_TOTAL         = 499 (RELAYED, not measured)
LOCAL_REGISTER_TOTAL               = 106 (Implementation-B)

CANONICAL_STARTING_HEAD            = 016bd766d5a089811ad313a9cca0d57fc674b0ca
PUBLIC_CANONICAL_REPOSITORY        = YES  Maqaleed-Digital/PetCare-Evidence-Repository
PRIVATE_PORT_SOURCE                = YES  Maqaleed-Digital/PetCare-Platform
SECRET_PRESENT_IN_PUBLIC_HISTORY   = YES
SECRET_PRESENT_IN_PUBLIC_HEAD      = YES  <-- worse than "history"; origin/main, live now
FILE_PATH                          = petcare_api/routers/auth.py
FIRST_VULNERABLE_COMMIT            = 5202bb5f  2026-05-23  (file created here)
LAST_VULNERABLE_COMMIT_IN_SOURCE   = 9111f631  2026-05-23
FIX_COMMIT                         = 3224c65d / e98ee966  2026-09-01  (NOT pushed)
PUBLIC_HISTORY_EXPOSURE_WINDOW     = 2026-05-23T22:22:51Z -> OPEN (103 days)

VULNERABLE_IMAGE_EXECUTED          = UNKNOWN   <-- was YES; corrected, see C-1
FIRST_KNOWN_PRODUCTION_DEPLOYMENT  = 2026-04-06 (predates the defect by 7 weeks)
DEPLOYMENT_AFTER_2026-05-23        = NO EVIDENCE (neither proven nor disproven)
VULNERABLE_SERVING_WINDOW          = UNKNOWN; upper bound 2026-05-23 -> 2026-09-01

CURRENT_ENDPOINT                   = petcare-api-prod-232802712581.me-central2.run.app
CURRENT_GET_STATUS                 = 500 (first hit) then 503 steady
CURRENT_HEAD_STATUS                = 503
RANDOM_PATH_STATUS                 = 503  <-- no application routing
RESPONSE_ORIGIN                    = Google Frontend error page, NOT application output
SERVICE_OBJECT_EXISTS              = YES (discriminated by 3 negative controls)
PETCARE_WEB_PROD                   = DOES NOT EXIST (byte-identical control 404)
IAM_401_403_OBSERVED               = NO
CURRENT_PUBLIC_NETWORK_REACHABILITY= PROBABLE_NOT_PROVEN
CURRENT_RUNTIME_SERVING            = NO
CURRENT_RUNTIME_VULNERABLE         = NO_CODE_EXECUTING

HISTORICAL_PUBLIC_IAM              = UNKNOWN (credential-gated; one read closes it)
SESSION_ISSUANCE_EVIDENCE          = UNKNOWN (credential-gated)
LOG_EVIDENCE_AT_RISK               = UNKNOWN (retention unreadable)

SESSION_MECHANISM                  = signed cookie (itsdangerous), stateless
SESSION_TTL                        = 28800s (8h)
REVOCATION_MECHANISM               = NONE; rotation IS global invalidation
FORGERY_IMPACT_IF_KEY_WAS_LIVE     = CRITICAL
FORGERY_IMPACT_REALISED            = UNKNOWN

CURRENT_SOURCE_FIXED               = YES (local branch only; fail-closed, guards ARMED)
GCP_READ_STATUS                    = BLOCKED_CREDENTIAL_GATE (re-confirmed this session)

SECURITY_INCIDENT_CREDIBILITY      = MODERATE
CP2_EXCLUSION_2_TRIGGERED          = NO
NO_MUTATION_PERFORMED              = YES
```

## Why MODERATE and not HIGH

The three facts offered as a chain do not link. A publicly-derivable default only
matters if code carrying it ran; nothing evidences that it did, and the one deployment
on record predates it. The endpoint's missing `403` is a real signal about the invoker
policy, but it attaches to a service that is executing no code at all.

What is **confirmed** is narrower and still worth fixing: a session-signing default sits
in a public default branch, unremediated, 103 days on.

Two credential-gated reads — the service IAM policy, and the revision list with creation
timestamps — resolve this to CONFIRMED or to NO-INCIDENT. Both are in
`GCP_FORENSIC_READ_CARD.md`. Neither is a mutation.
