IDENTITY SERVICE SPEC

Purpose:
Provide authorization, role enforcement, and tenant isolation for PetCare runtime modules.

Hard requirements:
- role matrix enforcement
- tenant boundary enforcement
- deterministic authorization responses
- audit compatibility

Validation objectives:
- unauthorized action denied
- cross-tenant action denied
- permitted action allowed
- explicit reason codes emitted
