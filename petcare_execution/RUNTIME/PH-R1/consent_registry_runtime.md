# consent_registry Runtime Module

Purpose
Provide owner consent capture and enforcement.

Owns

- consent capture
- consent revocation
- sharing scope evaluation
- purpose limitation rules

Does Not Own

- UI consent forms
- audit persistence
- clinical decisions

Interfaces

Consumes
- owner identity
- request purpose

Produces
- consent allowed/denied decision

Dependencies

identity_rbac

Gate Requirements

G-R1 Regulatory & Privacy Gate

Evidence Expectations

consent audit samples
revocation flow verification
purpose limitation enforcement tests
