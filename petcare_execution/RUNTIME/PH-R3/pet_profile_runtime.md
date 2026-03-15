# pet_profile Runtime Module

Purpose
Provide the shared runtime boundary for longitudinal pet identity and core profile state.

Owns
- pet identity record
- species, breed, age, sex profile attributes
- owner-to-pet association boundary
- baseline profile lifecycle state

Consumes
- identity_rbac authorization
- owner-service profile requests
- audit_ledger logging

Produces
- pet profile events
- profile update events
- identity-linked record references

Does Not Own
- consultation diagnosis
- prescription fulfillment
- emergency triage classification
- audit persistence

Dependencies
- identity_rbac
- audit_ledger

Gate Requirements
- G-S1 Security Gate
- G-R1 Regulatory & Privacy Gate

Evidence Expectations
- profile access authorization tests
- profile update audit samples
- owner-to-pet association verification
