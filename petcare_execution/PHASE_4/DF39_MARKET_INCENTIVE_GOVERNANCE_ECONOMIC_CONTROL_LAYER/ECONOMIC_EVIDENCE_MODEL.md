DF39 Economic Evidence Model

Purpose

Define the minimum auditable record required for economic governance actions.

Evidence Objects

1. proposal record
Captures owner, objective, cohort, mechanism, requested dates, and justification

2. approval record
Captures approver identity, approval reference, approved limits, and approval timestamp

3. fairness record
Captures comparison class, fairness rationale, constraint check result, and reviewer identity

4. activation record
Captures activation time, active controls, validity window, and rollback posture

5. monitoring record
Captures observed effect, exception count, escalation flags, and review timestamp

6. rollback or expiry record
Captures end state, reason, restored baseline, and linked evidence

Mandatory Fields

incentive_id
owner
pricing_governance_mode
revenue_share_model_ref
fairness_ruleset_ref
approval_id
objective
affected_population
bounded_mechanism
valid_from
valid_to
rollback_rule
audit_trace_id
status

Statuses

BLOCKED
CONTROLLED
ACTIVE_GOVERNED
SUSPENDED
ROLLED_BACK
EXPIRED

Evidence Integrity

All evidence bundles must include:
1. deterministic file listing
2. git head
3. manifest json
4. manifest sha256

Review Cadence

1. activation review at launch
2. periodic review during active window
3. end-of-window review on expiry or rollback
