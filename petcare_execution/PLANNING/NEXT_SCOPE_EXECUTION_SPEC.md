# NEXT SCOPE EXECUTION SPEC

## Epic

EP-06 Emergency Network

## Execution Identifier

PETCARE-PHASE-1-BUILD-EP06

## Objective

Build the governed emergency network foundation that supports clinic availability visibility, SLA-aware routing, explainable emergency selection, and pre-arrival packet readiness without introducing autonomous clinical decision authority.

## Authoritative Stories

S-01 Partner availability sync
S-02 Emergency routing algorithm

## Build Order

### WAVE-01
Emergency partner availability model

Deliver:
- partner clinic availability entity
- capacity status
- open/close state
- ETA representation
- failover eligibility fields

### WAVE-02
Availability repository and query surfaces

Deliver:
- repository
- deterministic query layer
- filtering by status, capacity, and emergency readiness
- test coverage

### WAVE-03
Emergency routing service

Deliver:
- routing inputs
- candidate selection rules
- ranked route output
- explainability fields
- non-autonomous decision classification

### WAVE-04
Pre-arrival packet assembly contract

Deliver:
- packet schema
- required content checklist
- summary linkage to UPHR, meds, allergies, last notes
- consent verification hook

### WAVE-05
API and transport surface

Deliver:
- read-only emergency routing endpoints
- packet preview surface
- error contracts
- no mutation outside authorized emergency workflow

### WAVE-06
Governance, evidence, and closure

Deliver:
- EP-06 hard-gate evidence support
- operational readiness checks
- closure plan

## Non-Negotiable Constraints

- no autonomous triage decision
- no autonomous emergency dispatch
- no mutation of EP-03 escalation semantics
- no mutation of EP-04 lifecycle behavior
- no mutation of EP-05 governance chain
- routing output must be explainable
- emergency packet content must be traceable
- consent and purpose limitation remain enforced
- clinical authority remains human-only

## Proposed File Families

Domain:
- emergency_availability models
- emergency_routing service
- prearrival_packet contract

Persistence:
- emergency repository
- emergency query

API:
- routes_ep06_waveXX
- contracts
- registry

Tests:
- tests/ep06/

Migrations:
- emergency partner availability
- emergency routing records if needed
- packet contract schema if needed

## Hard Gate Expectations

G-C1 Clinical Safety Gate
Pass conditions:
- routing logic is explainable
- no autonomous clinical decisioning
- emergency packet uses trusted governed inputs only

G-O1 Operational Readiness Gate
Pass conditions:
- availability and failover logic deterministic
- ETA and readiness surfaced
- operational alerts and failover behavior testable

## Stop Conditions

Stop only if execution requires semantic mutation of:
- consent rules
- escalation authority
- clinical sign-off immutability
- assistive-only AI boundary

## Planning Conclusion

EP-06 should start at:
PETCARE-PHASE-1-BUILD-EP06-WAVE-01
