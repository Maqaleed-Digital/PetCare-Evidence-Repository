CROSS_UNIT_OPTIMIZATION_CONTROL_POLICY — DF28

PURPOSE

Define the governance controls for portfolio-level optimization across units.

OPTIMIZATION CONTROL CATEGORIES

1. PRIORITY ALIGNMENT
- identify where portfolio attention should be directed
- informational only
- no direct execution effect

2. CAPACITY BALANCING SIGNALS
- identify governed balancing opportunities
- no automatic reallocation
- must remain recommendation-only

3. EXCEPTION RESPONSE COORDINATION
- identify units requiring coordinated review
- no cross-unit command authority
- requires human escalation

4. READINESS SEQUENCING
- recommend review order for governed action candidates
- sequencing does not authorize action
- local gates remain required

5. PORTFOLIO EFFICIENCY OBSERVATIONS
- summarize recurring coordination friction
- cannot modify process automatically
- requires separate governance process for change

RESTRICTIONS

Optimization controls must not:
- reassign ownership automatically
- modify local schedules automatically
- bypass approval chains
- imply mandatory compliance beyond policy baseline
- create hidden unit-to-unit dependencies
- expose unapproved operational detail
- rank units without cited criteria and evidence

APPROVAL MODEL

Optimization output is allowed only when:
- all contributing signals are approved
- source evidence is current
- policy version is aligned
- optimization rule is declared
- required human review status is explicit
- federated constraints remain satisfied

OUTPUT STATES

- recommended
- restricted
- blocked
- stale
- misaligned

FAIL-CLOSED ENFORCEMENT

If any approval condition fails:
- output_state = blocked
- optimization publication prohibited
- evidence record required

AUDIT REQUIREMENT

Each optimization output must record:
- optimization_output_id
- optimization_category
- contributing_signal_ids
- policy_version
- rule_reference
- evidence_references
- approval_requirement
- output_state
- timestamp
