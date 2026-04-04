EXTERNAL_ACTIVATION_GATE_POLICY — DF30

PURPOSE

Define the mandatory gates that must be satisfied before any external candidate may be marked as admitted for activation review.

ACTIVATION GATES

1. G-E1 SOVEREIGNTY PRESERVATION GATE
- verifies no governance bypass
- verifies no hidden dependency creation
- verifies no standing access implication

2. G-E2 POLICY ALIGNMENT GATE
- verifies current policy version alignment
- verifies checksum lock consistency
- verifies no undeclared policy exceptions

3. G-E3 EVIDENCE INTEGRITY GATE
- verifies evidence completeness
- verifies manifest-backed traceability
- verifies reproducible explanation basis

4. G-E4 INTERACTION SCOPE GATE
- verifies declared category and intended scope
- verifies no uncontrolled execution surface
- verifies no live activation implied

5. G-E5 APPROVAL POSTURE GATE
- verifies named human approval requirement
- verifies review authority exists
- verifies fail-closed blocked state when approval is absent

ADMISSION STATES

- admitted_for_activation_review
- review_ready
- restricted
- blocked
- stale
- misaligned

RESTRICTIONS

Activation gate policy must not:
- grant live access
- generate credentials
- create automatic onboarding
- authorize runtime connectivity
- bypass local or federated controls
- weaken portfolio governance
- treat gate passage as activation

APPROVAL MODEL

An admission output is allowed only when:
- candidate declaration exists
- all required gates are satisfied
- source evidence is current
- policy version is aligned
- approval requirement is explicit
- federated, portfolio, and external boundary constraints remain satisfied

FAIL-CLOSED ENFORCEMENT

If any required gate fails:
- admission_state = blocked
- publication prohibited
- evidence record required

AUDIT REQUIREMENT

Each admission output must record:
- admission_output_id
- candidate_reference
- declared_scope
- satisfied_gates
- failed_gates
- policy_version
- evidence_references
- approval_requirement
- admission_state
- timestamp
