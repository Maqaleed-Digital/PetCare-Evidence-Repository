# ai_intake Runtime Module

Purpose
Provide governed runtime boundary where clinical and operational context enters assistive AI workflows.

Owns
- AI-ready clinical summary preparation boundary
- consultation context packaging reference
- pet profile inclusion reference
- timeline inclusion reference
- structured record inclusion reference
- privacy-safe AI input assembly boundary

Consumes
- pet_profile runtime
- timeline runtime
- structured_clinical_records runtime
- consultation_record_lifecycle runtime
- consent_registry sharing decisions
- identity_rbac authorization
- audit_ledger logging

Produces
- AI-ready clinical summary payload references
- packaged AI intake events
- privacy-checked AI input references

Does Not Own
- model inference hosting
- diagnosis authority
- treatment authority
- audit persistence

Dependencies
- pet_profile runtime
- timeline runtime
- structured_clinical_records runtime
- consultation_record_lifecycle runtime
- consent_registry
- identity_rbac
- audit_ledger

Gate Requirements
- G-A1 AI Governance Gate
- G-R1 Regulatory & Privacy Gate
- G-S1 Security Gate
- G-C1 Clinical Safety Gate

Evidence Expectations
- AI input packaging verification
- privacy-safe intake checks
- AI intake audit samples
