# owner-service Runtime Module

Purpose
Owner-facing operational service for pet owners.

Owns
- pet profiles
- owner contact information
- appointment requests
- consent capture initiation
- owner medical record viewing

Consumes
- identity_rbac authorization
- consent_registry consent decisions
- audit_ledger logging

Produces
- owner interaction events
- appointment request events

Does Not Own
- clinical diagnosis
- prescriptions
- audit persistence
