PORTFOLIO_ORCHESTRATION_RULE_CATALOG — DF28

PURPOSE

Define the approved orchestration rules that may be used to generate portfolio optimization guidance.

RULE MODEL

Each rule must include:
- rule_id
- rule_name
- purpose
- input_signals
- constraint_reference
- output_type
- explanation_requirement
- approval_requirement
- publication_rule

APPROVED RULES

1. portfolio_priority_alignment
purpose: identify the most governance-relevant optimization opportunities across units
input_signals:
- unit_governance_alignment
- governed_exception_summary
- resilience_posture_summary
constraint_reference: portfolio sovereignty preserved
output_type: priority recommendation
explanation_requirement: must explain why signals justify ordering
approval_requirement: human review required
publication_rule: block if any input signal lacks provenance

2. contract_health_coordination
purpose: identify coordination needs where interoperability contract health affects portfolio readiness
input_signals:
- interoperability_contract_health
- cross_unit_policy_alignment
constraint_reference: no implicit coupling allowed
output_type: coordination recommendation
explanation_requirement: must cite contract references explicitly
approval_requirement: human review required
publication_rule: block if contract references are stale or missing

3. evidence_completeness_attention
purpose: identify units or interactions needing evidence remediation review
input_signals:
- unit_evidence_completeness
- governed_exception_summary
constraint_reference: evidence chain is mandatory
output_type: remediation recommendation
explanation_requirement: must map recommendation to missing evidence points
approval_requirement: human review required
publication_rule: block if evidence references cannot be traced

4. resilience_review_sequencing
purpose: recommend review sequencing for resilience follow-up based on current validated posture
input_signals:
- resilience_posture_summary
- governed_exception_summary
constraint_reference: sequencing does not authorize action
output_type: review sequencing recommendation
explanation_requirement: must explain ordering basis
approval_requirement: human review required
publication_rule: block if resilience evidence is stale

5. policy_alignment_attention
purpose: identify where portfolio attention is needed to preserve checksum-locked alignment
input_signals:
- cross_unit_policy_alignment
- unit_governance_alignment
constraint_reference: no policy drift tolerated
output_type: alignment recommendation
explanation_requirement: must cite affected alignment references
approval_requirement: human review required
publication_rule: block if policy version or checksum reference is incomplete

PROHIBITED RULES

- automatic resource transfer
- automatic execution routing
- autonomous exception response
- hidden dependency optimization
- uncited portfolio scoring
- policy override generation
- any rule without explicit approval requirement
