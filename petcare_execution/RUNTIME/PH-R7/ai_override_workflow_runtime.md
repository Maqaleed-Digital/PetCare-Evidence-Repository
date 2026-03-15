# ai_override_workflow Runtime Module

Purpose
Provide governed runtime boundary for clinician override, rejection, and safety flagging of AI assistive outputs.

Owns
- override action boundary
- reject AI suggestion boundary
- unsafe output flag boundary
- override reason reference
- clinician authority preservation boundary

Consumes
- vet_copilot runtime
- prompt_output_logging runtime
- consultation_record_lifecycle runtime
- identity_rbac authorization
- audit_ledger logging

Produces
- override events
- reject events
- unsafe output flag events
- clinician reason-linked audit references

Does Not Own
- clinical diagnosis logic
- prescription execution
- model retraining
- audit persistence

Dependencies
- vet_copilot runtime
- prompt_output_logging runtime
- consultation_record_lifecycle runtime
- identity_rbac
- audit_ledger

Gate Requirements
- G-A1 AI Governance Gate
- G-C1 Clinical Safety Gate
- G-S1 Security Gate

Evidence Expectations
- override workflow verification
- unsafe output flag checks
- override audit samples
