# scheduling_lifecycle Runtime Module

Purpose
Provide governed runtime boundary for appointment and scheduling lifecycle handling.

Owns
- booking request lifecycle
- reschedule lifecycle
- cancel lifecycle
- conflict rule enforcement boundary
- schedule state transitions

Consumes
- identity_rbac authorization
- owner-service appointment requests
- admin-service scheduling configuration
- vet-service consultation capacity signals
- audit_ledger logging

Produces
- booking events
- reschedule events
- cancellation events
- schedule state references

Does Not Own
- consultation clinical notes
- diagnosis logic
- prescription issuance
- audit persistence

Dependencies
- identity_rbac
- audit_ledger
- owner-service
- admin-service
- vet-service

Gate Requirements
- G-S1 Security Gate
- G-O1 Operational Readiness Gate

Evidence Expectations
- scheduling conflict rule verification
- booking/reschedule/cancel state transition tests
- scheduling audit samples
