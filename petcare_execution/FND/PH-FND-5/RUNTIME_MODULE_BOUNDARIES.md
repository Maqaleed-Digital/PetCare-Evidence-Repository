# Runtime Module Boundaries

Status: Authoritative boundary definition for runtime start

## Shared Runtime Controls

### identity_rbac
Owns:
- authentication and authorization enforcement
- role resolution
- permission checks
- session security policy boundary

Does not own:
- clinical decisions
- consent policy semantics
- audit storage

### consent_registry
Owns:
- consent capture state
- consent revocation state
- purpose limitation decision boundary
- consent sharing scope evaluation

Does not own:
- UI behavior
- audit persistence
- clinical record mutation

### audit_ledger
Owns:
- immutable audit event persistence
- correlation ids
- actor / action / timestamp accountability

Does not own:
- authorization decisions
- business workflow state

### clinical_signoff
Owns:
- sign-off required states
- immutable-after-sign enforcement
- sign-off event generation

Does not own:
- consultation authoring UX
- diagnosis logic
- prescription logic beyond sign-off checkpoint

### evidence_export
Owns:
- evidence package generation boundary
- governed export orchestration
- audit-linked export references

Does not own:
- clinical workflow execution
- runtime authorization policy definition

## Surface Services

### owner-service
Owns:
- owner-facing health timeline retrieval
- appointments lifecycle boundary
- consent interaction boundary
- owner-visible emergency context

### vet-service
Owns:
- consultation queue runtime
- consultation record lifecycle
- prescription issuance orchestration
- sign-off handoff to clinical_signoff

### admin-service
Owns:
- platform admin console runtime boundary
- governed configuration read models
- audit viewer access boundary
- evidence export request boundary

### pharmacy-service
Owns:
- prescription queue runtime
- dispense state machine
- pharmacy safety workflow orchestration
- inventory integration boundary

### emergency-service
Owns:
- escalation state handling
- emergency summary generation
- partner clinic handoff boundary
- emergency continuity events

## Boundary Rule

No runtime module may absorb another module's governance responsibility.
