# PETCARE EP-01 AND EP-02 IMPLEMENTATION BASELINE

Pack ID: PETCARE-EP01-EP02-IMPLEMENTATION-BASELINE
Predecessor Commit: 6cc8e3647ca2e21f87960f30f23ec4398d4c77e1
Scope: EP-01 Identity, Access, Consent Baseline and EP-02 UPHR Core
Status: Implementation Ready Baseline

## 1. Objective

Create the implementation-ready baseline for the first two PHASE 1 epics:

- EP-01 Identity, Access, Consent Baseline
- EP-02 Unified Pet Health Record Core

This pack does not claim that runtime implementation is complete.
This pack defines the governed implementation baseline required for deterministic repo-native build execution.

## 2. Scope locked

### EP-01
- PHASE 1 role matrix
- RBAC boundary and least-privilege model
- Consent capture and revoke baseline
- Purpose limitation baseline
- Audit taxonomy for EP-01 actions

### EP-02
- UPHR domain data model baseline
- Timeline and versioning model
- Auditable CRUD baseline
- Secure attachment and document handling baseline
- Prompt-safe redaction baseline for AI usage of UPHR content

## 3. Protected zones

The following semantics are protected and may not be changed in this pack:
- consent scopes and enforcement meaning
- RBAC role semantics
- audit event taxonomy semantics
- clinical sign-off immutability semantics
- escalation semantics

## 4. Implementation baseline outputs

This pack must produce:
- role matrix specification
- consent scope specification
- audit event taxonomy
- UPHR data model baseline
- API contract baseline
- UI surface mapping baseline
- evidence and hard-gate mapping
- notion-ready update
- emergent-ready prompt
- manifest with SHA-256

## 5. Delivery use

The next implementation run after this pack should use these artifacts as the authoritative design baseline for:
- schema creation
- service contract creation
- API route definition
- UI route and component planning
- test and evidence preparation

## 6. Entry criteria for next code-build wave

The next code-build wave may proceed only if:
- this pack is committed and pushed
- protected-zone semantics remain unchanged
- EP-01 and EP-02 files are accepted as authoritative
- the executor is selected
- evidence expectations are frozen

## 7. Stop condition

Stop only if implementation requires changing the meaning of:
- who can access what
- what consent authorizes
- what must be audited
- how clinical approval semantics work
- how escalation meaning is enforced

If triggered, create STOP_REPORT.md and stop.
