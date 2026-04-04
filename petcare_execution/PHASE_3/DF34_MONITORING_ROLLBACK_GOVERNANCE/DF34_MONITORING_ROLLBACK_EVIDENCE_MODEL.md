DF34 — MONITORING AND ROLLBACK EVIDENCE MODEL

REQUIRED RECORD FIELDS

- monitoring_output_id
- partner_reference
- monitoring_state
- signal_references
- rollback_reference
- killswitch_reference
- escalation_reference
- evidence_references
- validator_result
- timestamp

RULES

- every live monitoring output must identify rollback reference
- every live monitoring output must identify kill-switch authority
- every blocked output must still produce evidence
- no output may imply autonomous remediation
