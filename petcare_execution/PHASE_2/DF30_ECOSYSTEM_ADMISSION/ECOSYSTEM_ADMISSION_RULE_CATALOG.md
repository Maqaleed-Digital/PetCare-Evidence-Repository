ECOSYSTEM_ADMISSION_RULE_CATALOG — DF30

PURPOSE

Define the approved rules for evaluating external candidate admission and activation gate readiness.

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

1. candidate_scope_declaration_check
purpose: verify that the external candidate and intended interaction scope are explicitly declared under governance
input_references:
- candidate declaration reference
- external boundary policy reference
- interaction scope reference
constraint_reference: admission requires declared scope
output_type: declaration validation
explanation_requirement: must cite why the declared scope is sufficient or blocked
approval_requirement: human review required
publication_rule: block if candidate scope is missing or ambiguous

2. evidence_integrity_admission_check
purpose: verify that admission posture is supported by complete, current, and traceable evidence
input_references:
- manifest references
- evidence directory references
- prior readiness references
constraint_reference: immutable evidence chain required
output_type: evidence validation
explanation_requirement: must cite evidence completeness and integrity basis
approval_requirement: human review required
publication_rule: block if manifest or evidence references are incomplete

3. policy_alignment_admission_check
purpose: verify that the candidate admission posture preserves policy alignment and checksum lock integrity
input_references:
- policy version references
- checksum references
- federated governance references
constraint_reference: no policy drift tolerated
output_type: alignment validation
explanation_requirement: must cite preserved alignment basis
approval_requirement: human review required
publication_rule: block if policy version or checksum reference is missing

4. activation_gate_completeness_check
purpose: verify that all required admission gates are explicitly satisfied before activation review is considered
input_references:
- gate policy reference
- gate satisfaction references
- approval posture references
constraint_reference: gate passage is required before review-ready or admitted posture
output_type: gate completeness validation
explanation_requirement: must cite satisfied and failed gates explicitly
approval_requirement: human review required
publication_rule: block if any required gate is unsatisfied or undeclared

5. sovereignty_safe_admission_check
purpose: verify that the candidate admission posture preserves sovereignty, fail-closed governance, and no-bypass control
input_references:
- federated governance references
- portfolio orchestration references
- external boundary references
constraint_reference: no sovereignty loss, no governance bypass
output_type: sovereignty preservation validation
explanation_requirement: must cite preserved control boundaries
approval_requirement: human review required
publication_rule: block if any governance boundary reference is missing

PROHIBITED RULES

- automatic activation
- automatic credential issuance
- autonomous onboarding
- live connectivity authorization through admission output
- uncited trust admission
- policy exception generation
- any rule without explicit human approval requirement
