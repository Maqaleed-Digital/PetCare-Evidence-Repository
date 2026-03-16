CONSENT SERVICE SPEC

Purpose:
Manage consent state and purpose limitation enforcement for PetCare records access.

Required checks:
- consent exists
- requested purpose allowed
- tenant scope consistent
- audit event emitted for grant/revoke

Validation objectives:
- grant writes active consent
- revoke disables access
- purpose mismatch denied
