PH7 INCIDENT AND SLA REGISTER

INCIDENT REQUIRED FIELDS
- incident_id
- detected_at_utc
- clinic_id
- role_impacted
- journey_or_workflow_step
- severity
- description
- owner
- mitigation_action
- resolved_at_utc
- status
- evidence_reference
- notes

SEVERITY MODEL
- SEV-1 critical patient safety or total workflow block
- SEV-2 major role or workflow degradation
- SEV-3 partial issue with workaround
- SEV-4 minor issue or cosmetic instability

SLA / OPERATIONS REQUIRED FIELDS
- service_check_id
- checked_at_utc
- route_or_workflow
- expected_behavior
- observed_behavior
- status
- follow_up_required
- notes

RULES
- every operational issue must be logged
- every severe issue must have owner and mitigation
- no hidden incident suppression
- governance exceptions must be recorded explicitly
