# PETCARE — EP-09 DEPENDENCY MAP

Status: LOCKED

## Upstream Dependency Baseline

EP-07 Dependencies
- partner onboarding and verified partner status
- contract and SLA context
- pricing and settlement preparation context
- order and execution visibility context

EP-08 Dependencies
- settlement package model
- approval-controlled instruction model
- execution record scaffold
- payout structure
- invoice scaffold baseline
- append-only ledger trace
- reconciliation mismatch detection
- non-autonomous export boundary
- locked financial invariants registry
- closure seal confirming controlled_financial_execution_non_autonomous

## Internal Dependency Groups

D-01 Invoice Operations
Depends on:
- settlement identity
- partner identity
- deterministic totals
- approval lineage
- timestamps and audit events

D-02 Payment Status Tracking
Depends on:
- exported instruction reference
- external reference placeholder model
- audit trail
- review queue model

D-03 Reconciliation Workflow
Depends on:
- expected totals from EP-08 instruction layer
- actual totals input model
- variance registry
- reviewer resolution model

D-04 Dispute Lifecycle
Depends on:
- invoice identity
- partner statement identity
- evidence attachment metadata
- resolution record model

D-05 Financial Visibility
Depends on:
- invoice state timestamps
- reconciliation state timestamps
- dispute state timestamps
- partner exposure aggregation rules

## Guardrail Dependencies

Must Not Change
- EP-08 invariants
- live payment rails disabled
- AI execution authority false
- detect-only reconciliation at EP-08 foundation layer

Can Extend
- operational state machines
- visibility and review workflows
- dispute and statement lifecycle
- external status recording model
