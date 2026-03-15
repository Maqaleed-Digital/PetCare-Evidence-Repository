# clinical_signoff_hookup Runtime Module

Purpose
Provide the runtime integration boundary that binds consultation completion to mandatory clinical sign-off enforcement.

Owns
- sign-off checkpoint invocation
- consultation completion handoff to clinical_signoff
- sign-off required state binding
- immutable-after-sign linkage to consultation records

Consumes
- consultation_record_lifecycle runtime
- clinical_signoff runtime
- identity_rbac authorization
- audit_ledger logging

Produces
- sign-off requested events
- sign-off completed events
- immutable consultation state references

Does Not Own
- diagnosis content generation
- sign-off policy semantics
- audit persistence

Dependencies
- consultation_record_lifecycle runtime
- clinical_signoff runtime
- identity_rbac
- audit_ledger

Gate Requirements
- G-C1 Clinical Safety Gate
- G-S1 Security Gate

Evidence Expectations
- sign-off checkpoint verification
- immutable-after-sign linkage tests
- sign-off audit samples
