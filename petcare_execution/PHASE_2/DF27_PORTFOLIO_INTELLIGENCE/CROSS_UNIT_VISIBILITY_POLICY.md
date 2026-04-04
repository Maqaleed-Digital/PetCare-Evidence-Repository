CROSS_UNIT_VISIBILITY_POLICY — DF27

PURPOSE

Define what may be seen across units, under what conditions, and with what governance constraints.

VISIBILITY CATEGORIES

1. PORTFOLIO HEALTH
- unit status summary
- baseline alignment status
- validation completion state
- evidence presence state

2. CONTROL ALIGNMENT
- policy version alignment
- contract compliance status
- federated validation outcomes
- exception counts

3. OPERATING SIGNALS
- approved KPI snapshots
- governed outcome summaries
- controlled risk indicators
- ratified readiness posture

4. ASSURANCE SIGNALS
- evidence completeness
- resilience attestation state
- certification posture
- governed escalation presence

RESTRICTIONS

Cross-unit visibility must not expose:
- hidden implementation dependencies
- unauthorized operational detail
- uncontrolled data sharing
- policy internals beyond approved visibility scope
- any execution surface
- any automated action path

APPROVAL MODEL

Visibility is allowed only when:
- source unit evidence exists
- approved schema is used
- federated contract allows the visibility type
- portfolio policy version is aligned
- provenance chain is intact

VISIBILITY STATES

- visible
- restricted
- blocked
- stale
- misaligned

FAIL-CLOSED ENFORCEMENT

If visibility approval conditions are not satisfied:
- status = blocked
- publication prohibited
- evidence record required

AUDIT REQUIREMENT

Every portfolio visibility output must record:
- output_id
- source_units
- visibility_category
- policy_version
- contract_reference
- evidence_references
- publication_state
- timestamp
