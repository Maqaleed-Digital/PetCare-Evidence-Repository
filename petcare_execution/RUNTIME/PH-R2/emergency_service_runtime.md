# emergency-service Runtime Module

Purpose
Emergency triage and rapid response coordination.

Owns
- emergency intake
- triage priority classification
- rapid vet assignment
- emergency case tracking

Consumes
- identity_rbac access control
- vet-service clinical escalation
- audit_ledger logging

Produces
- emergency events
- triage classification events

Does Not Own
- pharmacy dispensing
- clinic administration
