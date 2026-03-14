# Clinical Signoff — Service Boundary

## Service Identity

| Field        | Value                          |
|--------------|--------------------------------|
| Service Name | `clinical_signoff`             |
| Version      | `0.1.0-scaffold`               |
| Phase        | PH-FND-2                       |
| Owner        | Platform Foundation            |

## Responsibility

`clinical_signoff` enforces the requirement that clinical records (diagnoses, treatment plans,
prescriptions) are reviewed and approved by a licensed veterinarian before they take effect.
It manages the signoff state machine and provides immutability guarantees for approved records.

## Boundaries

### In scope
- Signoff request creation and routing to the responsible vet
- State machine transitions (DRAFT → PENDING → APPROVED | REJECTED)
- Approved-record immutability enforcement
- Rejection reason capture and re-submission flow
- Audit event emission for all state transitions

### Out of scope
- Clinical data storage → external clinical services
- Prescription fulfilment → pharmacy services
- Access control → `identity_rbac`
- Consent enforcement → `consent_registry`

## Interfaces

| Direction | Protocol | Endpoint prefix       | Notes                                      |
|-----------|----------|-----------------------|--------------------------------------------|
| Inbound   | HTTP/1.1 | `/v1/signoff/`        | Internal cluster only                      |
| Outbound  | HTTP/1.1 | `audit_ledger /v1/events` | Emit signoff state-change events       |

## PDPL Constraints

- Clinical records must only be accessible to vets with active consent from the pet owner.
- Approved records are sealed: no mutation permitted post-approval.
- Rejection reasons must not contain PII beyond the `record_id` reference.

## Dependencies

| Service                         | Purpose                                       |
|---------------------------------|-----------------------------------------------|
| `audit_ledger`                  | Emit signoff audit events                     |
| `identity_rbac`                 | Validate vet role before permitting sign       |
| `consent_registry`              | Verify owner consent before vet access        |
| `shared/SERVICE_REGISTRY.json`  | Peer discovery                                |
