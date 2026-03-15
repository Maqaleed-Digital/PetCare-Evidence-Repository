# Contract to Service Realization Map

Status: Runtime realization map  
Rule: Every contract group must have an owning runtime service

## Shared Conventions

Owner:
- platform shared runtime layer

Responsibility:
- request/response conventions
- error envelope handling
- authorization context propagation
- audit correlation propagation

## identity_rbac

Owning runtime service:
- identity_rbac

Consumed by:
- owner-service
- vet-service
- admin-service
- pharmacy-service
- emergency-service

## consent_registry

Owning runtime service:
- consent_registry

Consumed by:
- owner-service
- vet-service
- emergency-service
- AI runtime components
- evidence export boundaries

## audit_ledger

Owning runtime service:
- audit_ledger

Consumed by:
- all runtime services

## clinical_signoff

Owning runtime service:
- clinical_signoff

Consumed by:
- vet-service
- consultation runtime
- prescription issuance runtime
- emergency handoff runtime

## evidence_export

Owning runtime service:
- evidence_export

Consumed by:
- admin-service
- platform admin console boundary
- gate verification process
- release evidence process

## integration_index

Owning runtime service:
- platform integration index runtime

Consumed by:
- all surface services
- service dependency verification
- blocker registry maintenance

## Surface Runtime Ownership Map

owner surface contracts:
- owner-service

vet surface contracts:
- vet-service

admin surface contracts:
- admin-service

pharmacy surface contracts:
- pharmacy-service

emergency surface contracts:
- emergency-service

## Realization Rule

A contract group is not implementation-ready until:

- owning service is named
- dependency chain is declared
- gate requirements are attached
- evidence expectation is defined
