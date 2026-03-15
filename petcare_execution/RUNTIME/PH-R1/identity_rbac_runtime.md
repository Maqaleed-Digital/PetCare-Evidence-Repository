# identity_rbac Runtime Module

Purpose
Provide platform authentication and role-based authorization enforcement.

Owns

- role matrix
- permission evaluation
- session authorization checks
- service identity verification

Does Not Own

- consent semantics
- clinical decisions
- audit persistence

Interfaces

Consumes
- request actor context

Produces
- authorization decision
- role resolution

Dependencies

none (first runtime service)

Gate Requirements

G-S1 Security Gate

Evidence Expectations

authorization test cases
access denial audit entries
