DF37 — TRUST AND TIER RULE CATALOG

PURPOSE

Define the approved rules for governed trust posture and partner tier assignment.

RULE MODEL

Each rule must include:
- rule_id
- rule_name
- purpose
- input_references
- constraint_reference
- output_type
- explanation_requirement
- approval_requirement
- publication_rule

APPROVED RULES

1. trust_basis_completeness_check
purpose: verify that partner trust posture is based on approved and current evidence
input_references:
- trust basis references
- activation evidence references
- monitoring evidence references
constraint_reference: trust must be evidence-backed
output_type: trust validation
explanation_requirement: must cite why trust basis is sufficient or blocked
approval_requirement: human review required
publication_rule: block if trust basis is incomplete or stale

2. trust_state_assignment_check
purpose: verify that trust state assignment is explainable, reversible, and policy-aligned
input_references:
- trust framework references
- evidence references
- policy version references
constraint_reference: no automatic trust elevation
output_type: trust state assignment
explanation_requirement: must explain why assigned state is justified
approval_requirement: human review required
publication_rule: block if policy alignment is missing

3. tier_assignment_eligibility_check
purpose: verify that tier assignment is justified by trust posture and evidence maturity
input_references:
- partner tier policy reference
- trust state reference
- evidence maturity references
constraint_reference: tiering must not imply unrestricted privilege
output_type: tier eligibility validation
explanation_requirement: must cite why tier posture is justified or blocked
approval_requirement: human review required
publication_rule: block if tier basis is incomplete

4. trust_restriction_check
purpose: verify when partner trust or tier posture must be restricted due to evidence gaps, unresolved control issues, or stale validation
input_references:
- exception references
- monitoring references
- evidence references
constraint_reference: trust drift is not tolerated
output_type: restriction validation
explanation_requirement: must cite why restriction is required
approval_requirement: human review required
publication_rule: block publication of elevated trust states when unresolved issues exist

5. trust_reversibility_check
purpose: verify that trust and tier posture remain reversible and governed
input_references:
- trust state references
- tier references
- governance boundary references
constraint_reference: trust must remain reversible
output_type: reversibility validation
explanation_requirement: must cite preserved control boundaries
approval_requirement: human review required
publication_rule: block if reversibility posture is missing

PROHIBITED RULES

- automatic trust elevation
- uncited trust scoring
- permanent trust without review
- privilege expansion through tier only
- hidden favoritism logic
- any rule without explicit human approval requirement
