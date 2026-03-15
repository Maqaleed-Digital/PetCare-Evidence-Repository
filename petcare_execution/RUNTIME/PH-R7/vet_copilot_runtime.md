# vet_copilot Runtime Module

Purpose
Provide governed runtime boundary for assistive vet-facing AI support.

Owns
- symptom summarization assist boundary
- consultation note assistance boundary
- medication safety hint boundary
- emergency flag hint boundary
- assistive suggestion reference generation

Consumes
- ai_intake runtime
- prompt_output_logging runtime
- ai_override_workflow runtime
- ai_evaluation_harness runtime
- consultation_record_lifecycle runtime
- structured_clinical_records runtime
- identity_rbac authorization
- audit_ledger logging

Produces
- assistive AI suggestion events
- consultation-linked AI suggestion references
- safety hint references
- emergency hint references

Does Not Own
- diagnosis authority
- treatment decision authority
- prescription authority
- clinical sign-off authority
- audit persistence

Dependencies
- ai_intake runtime
- prompt_output_logging runtime
- ai_override_workflow runtime
- ai_evaluation_harness runtime
- consultation_record_lifecycle runtime
- structured_clinical_records runtime
- identity_rbac
- audit_ledger

Gate Requirements
- G-A1 AI Governance Gate
- G-C1 Clinical Safety Gate
- G-S1 Security Gate
- G-R1 Regulatory & Privacy Gate

Evidence Expectations
- assistive-only boundary verification
- no-authority constraint checks
- vet copilot audit samples
