# PETCARE — EP-09 FINANCIAL OPERATIONS MASTER SPEC

Status: ACTIVE EXECUTION SPEC
Phase: PETCARE-PHASE-1-BUILD-EP09-FINANCIAL-OPERATIONS-AND-RECONCILIATION
Source Commit Anchor: 4e24c28087283058b3ebc4b3d6971376aef9a67e

## Objective

Introduce the operational finance layer above EP-08 controlled financial execution, including invoice lifecycle, payment status tracking, reconciliation operations, dispute workflows, partner statements, financial visibility, and EP-09-scoped audit events.

## Locked Scope

Included:
- invoice lifecycle state machine
- payment status tracking model
- reconciliation workflow with human resolution
- dispute lifecycle
- partner statement generation
- financial visibility aggregation
- EP-09 audit event scaffolding
- tests
- evidence pack generator

Excluded:
- live bank rails
- autonomous payout release
- autonomous dispute resolution
- autonomous reconciliation resolution
- ERP write-back execution
- AI financial decision authority
- weakening EP-08 invariants

## Governance Invariants Carried Forward

1. live_payment_rails_enabled = false
2. ai_execution_authority = false
3. reconciliation_auto_resolution_enabled = false
4. export_mode remains non_autonomous_export_only
5. ledger trace remains append-only at the EP-08 foundation layer
6. all EP-09 transitions are deterministic and auditable
7. dispute outcomes require human authority
8. variance resolution requires human authority
9. external statuses may be recorded but may not autonomously move money

## All-Waves Scope

WAVE-01
Invoice lifecycle domain model

WAVE-02
Payment status tracking model

WAVE-03
Reconciliation workflow and variance review model

WAVE-04
Dispute lifecycle model

WAVE-05
Partner statement generation scaffold

WAVE-06
Financial visibility aggregation scaffold

WAVE-07
EP-09 audit event scaffolding

WAVE-08
Tests and evidence pack

## Stop Condition

Stop only if protected semantics outside EP-09 must be modified:
- EP-08 locked invariants
- consent semantics
- RBAC semantics
- audit taxonomy outside EP-09 scope
