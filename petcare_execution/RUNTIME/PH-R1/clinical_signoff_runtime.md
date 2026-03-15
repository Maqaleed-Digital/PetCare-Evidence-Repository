# clinical_signoff Runtime Module

Purpose
Enforce vet clinical approval and record immutability.

Owns

- clinical sign-off
- immutable-after-sign rule
- sign-off event generation

Does Not Own

- diagnosis logic
- consultation authoring
- medication rules

Interfaces

Consumes

- consultation record
- vet identity

Produces

- sign-off approval
- immutable state flag

Dependencies

identity_rbac
audit_ledger

Gate Requirements

G-C1 Clinical Safety Gate

Evidence Expectations

sign-off enforcement tests
immutable state verification
clinical audit samples
