# PETCARE — EP-12 DEPENDENCY MAP

Status: LOCKED

## Upstream Dependency Baseline

EP-08 Dependencies
- settlement control semantics
- approval and execution boundaries
- append-only ledger trace
- locked financial invariants registry

EP-09 Dependencies
- invoice lifecycle
- payment tracking
- reconciliation workflow
- disputes
- partner statements
- financial visibility
- locked operational finance invariants registry

EP-10 Dependencies
- external signal trust boundary
- deterministic queues
- human action attribution
- exception and escalation workflow
- operational control visibility
- locked integration and control invariants registry

EP-11 Dependencies
- controlled execution authorization
- treasury sufficiency
- governed rail dispatch
- safeguards
- settlement finalization
- locked payment activation invariants registry

## Internal Dependency Groups

D-01 Signal Intelligence
Depends on:
- payment events
- reconciliation events
- dispute events
- queue events
- execution lifecycle events

D-02 Risk Scoring
Depends on:
- partner history
- transaction attributes
- exception history
- dispute history
- delay patterns

D-03 Recommendations
Depends on:
- anomaly outputs
- risk score outputs
- current operational state
- configured recommendation policies
- visible explanation contract

D-04 Operational Optimization
Depends on:
- queue backlog
- task ownership state
- exception counts
- SLA timers
- deterministic prioritization inputs

D-05 Explainability and Trace
Depends on:
- recommendation id
- signal provenance
- rationale text
- operator response record
- audit linkage

## Guardrail Dependencies

Must Not Change
- EP-08 invariants
- EP-09 invariants
- EP-10 invariants
- EP-11 invariants
- ai_execution_authority = false
- human authorization requirements
- deterministic queue control without visible acceptance

Can Extend
- advisory intelligence
- score generation
- operator recommendations
- explanation surfaces
- recommendation acceptance or rejection capture
