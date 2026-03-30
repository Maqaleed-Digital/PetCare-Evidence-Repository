# PETCARE — EP-10 DEPENDENCY MAP

Status: LOCKED

## Upstream Dependency Baseline

EP-07 Dependencies
- verified partner context
- contract and SLA context
- order and execution visibility context

EP-08 Dependencies
- settlement package model
- approval-controlled instruction model
- execution record scaffold
- payout structure
- append-only ledger trace
- non-autonomous export boundary
- locked financial invariants registry
- closure seal confirming controlled_financial_execution_non_autonomous

EP-09 Dependencies
- invoice lifecycle state machine
- payment status tracking model
- reconciliation workflow model
- dispute lifecycle
- partner statements
- financial visibility aggregation
- EP-09 scoped audit events
- locked operational finance invariants registry
- closure seal confirming financial_operations_layer_non_autonomous

## Internal Dependency Groups

D-01 Integration Contracts
Depends on:
- instruction identifiers
- settlement identifiers
- invoice identifiers
- external reference mapping rules
- trust-bound payload model

D-02 Queue Operations
Depends on:
- reviewable finance entities
- deterministic prioritization model
- operator assignment model
- queue state audit trail

D-03 Human Execution Layer
Depends on:
- actor identity
- action taxonomy
- decision outcome model
- escalation model
- attribution records

D-04 External Signal Governance
Depends on:
- webhook ingestion record
- signal classification model
- trust outcome model
- human review marker
- non-autonomous handoff rules

D-05 Operational Visibility
Depends on:
- queue states
- action timestamps
- escalation states
- SLA markers
- exception counters

## Guardrail Dependencies

Must Not Change
- EP-08 invariants
- EP-09 invariants
- live payment rails disabled
- AI execution authority false
- non-autonomous export boundary
- human resolution requirements

Can Extend
- passive adapter contracts
- operator queues and dashboards
- external signal trust workflows
- action traceability models
- operational visibility models
