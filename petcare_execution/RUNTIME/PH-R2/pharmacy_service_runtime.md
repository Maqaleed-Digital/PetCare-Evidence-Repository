# pharmacy-service Runtime Module

Purpose
Medication and pharmacy operations service.

Owns
- prescription fulfillment
- medication inventory
- dispensing records
- medication labeling

Consumes
- identity_rbac pharmacist authorization
- vet-service prescription events
- audit_ledger logging

Produces
- dispensing events
- inventory adjustments

Does Not Own
- clinical diagnosis
- consultation records
