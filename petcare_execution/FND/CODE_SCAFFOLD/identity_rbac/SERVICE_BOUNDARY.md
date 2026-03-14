# Identity RBAC — Service Boundary

## Service Identity

| Field        | Value                          |
|--------------|--------------------------------|
| Service Name | `identity_rbac`                |
| Version      | `0.1.0-scaffold`               |
| Phase        | PH-FND-2                       |
| Owner        | Platform Foundation            |

## Responsibility

`identity_rbac` is the authoritative source for role-based access control decisions across the
petcare platform. It issues and validates identity tokens and enforces role assignments for every
authenticated principal (owner, vet, admin, pharmacy_staff, emergency_responder).

## Boundaries

### In scope
- Principal authentication (JWT issuance and validation)
- Role assignment CRUD (admin-only mutation)
- Access decision evaluation (`can(principal, action, resource)`)
- Audit emission for all access-denial events

### Out of scope
- Consent lifecycle → `consent_registry`
- Clinical data storage → external clinical services
- Evidence packaging → `evidence_export`

## Interfaces

| Direction | Protocol | Endpoint prefix       | Notes                       |
|-----------|----------|-----------------------|-----------------------------|
| Inbound   | HTTP/1.1 | `/v1/identity/`       | Internal cluster only       |
| Inbound   | gRPC     | `IdentityService`     | For high-throughput callers |
| Outbound  | HTTP/1.1 | `audit_ledger /v1/events` | Append access events    |

## PDPL Constraints

- No PII stored beyond `principal_id` (opaque UUID).
- Role matrix contains no personal data.
- All access decisions logged immutably via `audit_ledger`.

## Dependencies

| Service          | Purpose                            |
|------------------|------------------------------------|
| `audit_ledger`   | Emit access-denial audit events    |
| `shared/SERVICE_REGISTRY.json` | Peer discovery      |
