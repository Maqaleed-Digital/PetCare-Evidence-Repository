# consultation_record_lifecycle Runtime Module

Purpose
Provide runtime boundary for consultation record creation, progression, completion, and linkage to shared clinical records.

Owns
- consultation open state
- in-progress consultation state
- completed consultation state
- consultation-to-pet record linkage
- consultation record lifecycle transitions

Consumes
- scheduling_lifecycle runtime
- pet_profile runtime
- timeline runtime
- structured_clinical_records runtime
- identity_rbac authorization
- vet-service consultation operations
- audit_ledger logging

Produces
- consultation lifecycle events
- consultation-linked structured record updates
- timeline-linked consultation references

Does Not Own
- sign-off immutability enforcement
- pharmacy fulfillment
- emergency routing decisions
- audit persistence

Dependencies
- scheduling_lifecycle runtime
- pet_profile runtime
- timeline runtime
- structured_clinical_records runtime
- identity_rbac
- audit_ledger
- vet-service

Gate Requirements
- G-C1 Clinical Safety Gate
- G-S1 Security Gate
- G-R1 Regulatory & Privacy Gate

Evidence Expectations
- consultation lifecycle transition verification
- consultation-to-pet linkage checks
- consultation audit samples
