# PETCARE — EP-11 CONTROLLED PAYMENT ACTIVATION MASTER SPEC

Status: ACTIVE EXECUTION SPEC
Phase: PETCARE-PHASE-1-BUILD-EP11-CONTROLLED-PAYMENT-ACTIVATION
Source Commit Anchor: 657519cc76eaad00a6ceab9e8bedfec726fe9f25

## Objective

Introduce the controlled payment activation layer above EP-10 integration and operational control, including execution authorization, treasury sufficiency checks, governed rail dispatch contracts, execution safeguard state handling, settlement finalization, and EP-11-scoped audit events.

## Locked Scope

Included:
- execution authorization domain model
- treasury sufficiency and limit model
- payment rail connector contract and dispatch model
- execution safeguard state machine
- pause / cancel / retry / failure workflow
- settlement finalization model
- EP-11 scoped audit events
- tests
- evidence pack generator

Excluded:
- AI payment authorization
- silent payment release
- uncontrolled autonomous dispatch
- weakening EP-08, EP-09, or EP-10 invariants
- ungated external callback finalization
- non-audited money movement

## Governance Invariants Carried Forward

1. ai_execution_authority = false
2. explicit human authorization required before dispatch
3. treasury sufficiency check required before dispatch
4. dual control enforced where configured
5. every execution action attributable and timestamped
6. pause, cancel, retry, and failure paths remain explicit
7. external rails operate only through governed connector contracts
8. callbacks cannot autonomously finalize settlement
9. finalization must preserve reconciliation and ledger trace obligations
10. EP-08, EP-09, and EP-10 invariant registries remain authoritative

## All-Waves Scope

WAVE-01
Execution authorization domain model

WAVE-02
Treasury sufficiency and limit model

WAVE-03
Payment rail connector contract and dispatch model

WAVE-04
Execution safeguard state machine

WAVE-05
Pause / cancel / retry / failure workflow

WAVE-06
Settlement finalization model

WAVE-07
EP-11 scoped audit event scaffolding

WAVE-08
Tests and evidence pack

## Stop Condition

Stop only if protected semantics outside EP-11 must be modified:
- EP-08 locked invariants
- EP-09 locked invariants
- EP-10 locked invariants
- consent semantics
- RBAC semantics
- audit taxonomy outside EP-11 scope
