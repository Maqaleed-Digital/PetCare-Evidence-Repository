# PETCARE — EP-10 INTEGRATION AND OPERATIONAL CONTROL MASTER SPEC

Status: ACTIVE EXECUTION SPEC
Phase: PETCARE-PHASE-1-BUILD-EP10-INTEGRATION-AND-OPERATIONAL-CONTROL
Source Commit Anchor: ece60cb6c1de3edb12dc2dc2ea0baedfb2ef7928

## Objective

Introduce the real-world operability layer above EP-09 operational finance, including passive integration contracts, external signal governance, deterministic operational queues, human action attribution, exception and escalation workflows, operational visibility, and EP-10-scoped audit events.

## Locked Scope

Included:
- integration contract domain model
- external signal and trust boundary model
- deterministic operational queue model
- human action and task assignment model
- exception and escalation workflow model
- operational visibility aggregation
- EP-10 scoped audit events
- tests
- evidence pack generator

Excluded:
- live bank rails
- autonomous payout release
- autonomous callback processing
- autonomous approval release
- autonomous dispute closure
- autonomous reconciliation closure
- ERP write-back execution
- AI execution authority
- weakening EP-08 or EP-09 invariants

## Governance Invariants Carried Forward

1. live_payment_rails_enabled = false
2. ai_execution_authority = false
3. reconciliation_auto_resolution_enabled = false
4. adapters remain passive or instruction-only
5. external signals may be ingested but may not autonomously trigger execution
6. all human actions must be attributable and auditable
7. queue ordering and selection rules are deterministic
8. exception paths are reviewable and traceable
9. no external system bypasses PetCare governance gates
10. EP-08 and EP-09 invariant registries remain authoritative

## All-Waves Scope

WAVE-01
Integration contract domain model

WAVE-02
Webhook ingestion and trust boundary model

WAVE-03
Operational queue model

WAVE-04
Human action and task assignment model

WAVE-05
Exception and escalation workflow model

WAVE-06
Operational visibility aggregation model

WAVE-07
EP-10 audit event scaffolding

WAVE-08
Tests and evidence pack

## Stop Condition

Stop only if protected semantics outside EP-10 must be modified:
- EP-08 locked invariants
- EP-09 locked invariants
- consent semantics
- RBAC semantics
- audit taxonomy outside EP-10 scope
