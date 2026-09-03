# Notion Authority Sync — MyVetiCare

**AUTHORITY_SYNC_DATE:** 2026-09-03
**NOTION_LIVE_SYNC:** AVAILABLE
**AUTHORITY_SYNC_STATUS:** COMPLETE — three material contradictions found

First execution of the permanent Phase-0 rule. It earned itself immediately:
Notion holds primary evidence that the repository does not.

## Authority chain reconciled

| Field | Value | Source |
|---|---|---|
| `CURRENT_CLOUD_AUTHORITY` | **AWS** | Handoff 1 Sep 2026 — "AWS is current cloud authority. GCP is legacy/historical provenance only." CONFIRMED |
| `CANONICAL_REPOSITORY` | petcare-evidence-repository | MVC-GOV-CANON-001 (this repo) |
| `PORT_SOURCE` | petcare-platform | "Implementation B (`petcare-platform`) = LEGACY PORT SOURCE" CONFIRMED |
| `CURRENT_SCOPE_AUTHORITY` | **`REQUIREMENTS_TOTAL=499`** | Handoff 1 Sep 2026 |
| `CP-1` | Taken, ratified, immutable lock 2026-08-31 | Handoff |
| `CP-2` | Taken — engineering authorization, **NON-PRODUCTION ONLY**; conformance NOT certified | Handoff |

## CONTRADICTION 1 — the requirement denominator is 499, not 106

Notion records `REQUIREMENTS_TOTAL=499`, with the prior 129 incomplete
population reconciled exactly: BUILD_TESTABLE 37 + A4 17 + CONSTITUTIONAL 39 +
GATE3 32 + RESIDUE 4 = 129, zero overlaps.

Everything this lane has treated as a denominator — the 106-row register — is
**Implementation B's local register**, not the programme requirement estate. The
106 is not wrong; it is a different and much smaller object. Any traceability
presenting 106 as the product denominator understates scope roughly fourfold.

`SPECIFICATION_CONTENT_COMPLETE=YES` (499) · `BUILD_ACCEPTANCE_CONTRACT_COMPLETE=YES` (37/37)
`GOVERNANCE_VERIFICATION_COMPLETE=NO` (71 Gate-3) · `A4_OUTCOME_COMPLETE=NO` (17)
`FULL_CONFORMANCE_CERTIFIED=NO`

## CONTRADICTION 2 — the vulnerable serving layer WAS deployed and active

`PH5.1 — FULL UI BUILD + GCP WEB ACTIVATION` (2026-04-06) records:

```
SYSTEM STATE: PRODUCTION_ACTIVE (WEB + API)
API  (Cloud Run): petcare-api-prod-232802712581.me-central2.run.app
Web  (Cloud Run): petcare-web-prod-232802712581.me-central2.run.app
Gate PASS: UI contract validation, Web deployment, Web /api/health,
           API /health, Audit probe, Load balancer setup
External HTTPS Load Balancer + Serverless NEG -> petcare-web-prod (me-central2)
Project: prj-maq-petcare-prod   Project number: 232802712581
```

`PETCARE-PHASE-6.2 — First Real User Journey Validation` (2026-04-06) records
journeys run against those same endpoints.

This deployment **predates W0-A by five months** (W0-A landed 2026-09-01), so the
serving API carried `os.getenv("SECRET_KEY", "dev-secret-change-in-prod")` unless
`SECRET_KEY` was set in that service's environment.

`VULNERABLE_IMAGE_EXECUTED` therefore moves **UNKNOWN → YES (evidenced)**.

**`PUBLICLY_REACHABLE` remains UNKNOWN, and that is now the whole question.** A
Cloud Run `.run.app` endpoint is public only if the service carries an `allUsers`
invoker binding; `API /health PASS` could equally be an authenticated call. The
custom domain was *not* live — DNS was PENDING and the managed certificate was
PROVISIONING, not ACTIVE. Resolving this needs one read of the Cloud Run service
IAM policy, which is credential-gated.

### CP-2 exclusion 2 is cloud-agnostic and still armed

Verbatim from the 1 Sep handoff:

> "Binding CP-2 exclusion 2 is cloud-agnostic: if deployment evidence from ANY
> cloud shows the vulnerable serving layer was publicly reachable, that finding
> supersedes Wave-0 ordering... **Retiring GCP as current target does not retire
> this trigger.**"

The trigger requires *publicly reachable*, which is not proven, so it has **not**
fired: `CP2_EXCLUSION_2_TRIGGERED=NO`. But the residual is no longer "perhaps it
was never deployed". It is now precisely one unread IAM binding. Notion's own
fields agree: `CLOUD_AGNOSTIC_PUBLIC_EXPOSURE_TRIGGER=ACTIVE_NOT_FIRED`, and
"Do not claim global `PROVEN_NONE` without historical GCP evidence."

## CONTRADICTION 3 — PF-33 remote state is stale

Notion (1 Sep) states `PUSH=NOT_CONFIGURED_ZERO_REMOTES` and "Connected GitHub
search found no dedicated MyVetiCare repository."

Primary implementation reality contradicts both: this repository has a
configured origin on the Maqaleed-Digital PetCare-Evidence-Repository, and
petcare-platform has a configured origin on a private PetCare-Platform
repository with SSH working and remote tip `ec53458d`.

Under the precedence rule, **git wins on implementation reality** — remotes
exist. It does not follow that either is the *authorised* PF-33 custody
destination; that remains a Sponsor designation.

## Aligned, not contradicted

- Historical GCP image is `UNRESOLVED_HISTORICAL`, not `PROVEN_NONE` — matches
  this lane's `CLASS_G6_INDETERMINATE`.
- Wave-0 ordering precondition "W0-A landed first" — matches the A-before-B
  invariant enforced and guarded here.
- Notion reported Wave 0 delivered 2/10; this lane has since integrated five
  (W0-E, A, B, C, D) into the canonical branch.

## Standing instruction carried forward

> "STOP agent implementation before large W0-F serving-layer replacement and
> prepare `MVC-W0F-ENGINEERING-HANDOFF-001` for engineering-team implementation."

**W0-F is not agent work.** No lane should implement the serving-layer
replacement; it produces a handoff pack instead.

## Numbers marked RELAYED

Not independently measured in this run: 499, the 129 decomposition, 71 Gate-3,
17 A4, 37/37 build-acceptance. Each carries `RELAYED` until measured.
