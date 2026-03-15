# vet-service Runtime Module

Purpose
Clinical operations runtime service.

Owns
- consultation lifecycle
- clinical notes
- diagnosis recording
- treatment planning
- prescription initiation

Consumes
- identity_rbac vet authorization
- clinical_signoff approval
- audit_ledger logging

Produces
- consultation events
- treatment records
- prescription events

Does Not Own
- pharmacy dispensing
- drug interaction engine
