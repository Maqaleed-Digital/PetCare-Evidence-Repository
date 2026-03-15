# Runtime Service Implementation Order

Status: Authoritative build order for runtime start  
Rule: Earlier layers must be ready before later layers begin

## Order 0 — Shared Governance Controls

These services must be runtime-ready before all others:

1. identity_rbac
2. consent_registry
3. audit_ledger
4. clinical_signoff
5. evidence_export

Reason:
These services enforce access, consent, auditability, clinical immutability, and evidence generation across all later modules.

## Order 1 — Surface Boundary Runtime Modules

These boundary modules formalize runtime ownership for the already-mapped UI surfaces:

1. owner-service
2. vet-service
3. admin-service
4. pharmacy-service
5. emergency-service

Reason:
PH-FND-4 identified service blockers at the surface-to-contract layer. Runtime ownership must be defined here before deeper feature logic begins.

## Order 2 — Shared Clinical Record Runtime

1. pet profile runtime
2. timeline runtime
3. document/media access boundary
4. structured allergy/medication/vaccination/lab record handling

Reason:
The Unified Pet Health Record is the shared system-of-record foundation for consultation, pharmacy, and emergency continuity.

## Order 3 — Consultation & Care Delivery Runtime

1. scheduling lifecycle runtime
2. consultation record lifecycle runtime
3. clinical sign-off enforcement hook-up
4. prescription issuance trigger boundary
5. escalation trigger boundary

Reason:
Clinical operations depend on identity, consent, audit, sign-off, and UPHR readiness.

## Order 4 — Pharmacy Runtime

1. prescription intake and status lifecycle
2. medication safety checks
3. dispense state handling
4. cold-chain tagging boundary
5. recall workflow boundary

Reason:
Pharmacy workflows depend on consultation outputs, patient records, and audit enforcement.

## Order 5 — Emergency Runtime

1. red-flag escalation realization
2. clinic availability boundary
3. pre-arrival packet generation
4. handoff continuity logging

Reason:
Emergency workflows depend on consultation signals, patient record availability, and consent-aware summary generation.

## Order 6 — AI Governance Runtime

1. prompt/output logging realization
2. override reason capture
3. evaluation harness boundary
4. AI intake runtime
5. vet copilot runtime

Reason:
AI runtime must sit on top of shared controls and domain workflows, never before them.

## Order 7 — Partner / Marketplace / External Runtime

1. partner onboarding boundary
2. partner SLA configuration boundary
3. catalog ingestion boundary
4. pricing and settlement boundary
5. external integration adapter realization

Reason:
Externalized workflows must come after internal core flows are stable and auditable.

## Stop Rule

No service may move to implementation until all predecessor orders are marked Ready.
