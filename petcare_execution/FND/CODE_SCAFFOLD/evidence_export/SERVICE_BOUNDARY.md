# Evidence Export — Service Boundary

## Service Identity

| Field        | Value                          |
|--------------|--------------------------------|
| Service Name | `evidence_export`              |
| Version      | `0.1.0-scaffold`               |
| Phase        | PH-FND-2                       |
| Owner        | Platform Foundation            |

## Responsibility

`evidence_export` produces governed, auditable export packages of platform data for regulatory,
compliance, and internal governance purposes. All exports are signed, time-limited, and tracked
in `audit_ledger`.

## Boundaries

### In scope
- Export request creation and validation
- Data collection from authorised sources (audit_ledger, consent_registry snapshots)
- Pseudonymisation of PII before export
- Export artifact signing (SHA-256 manifest + HMAC)
- TTL enforcement and automatic purge of expired artifacts
- Audit emission for export lifecycle events

### Out of scope
- Clinical data access → clinical services (not exposed by evidence_export)
- Role enforcement → `identity_rbac`
- Consent enforcement → `consent_registry`
- Long-term archival → separate archival pipeline

## Interfaces

| Direction | Protocol | Endpoint prefix        | Notes                              |
|-----------|----------|------------------------|------------------------------------|
| Inbound   | HTTP/1.1 | `/v1/export/`          | Admin role only                    |
| Outbound  | HTTP/1.1 | `audit_ledger /v1/events` | Emit export lifecycle events    |

## PDPL Constraints

- No raw PII in export artifacts; pseudonymisation required (PDPL Article 4).
- Cross-border exports require explicit SDAIA approval reference in export metadata.
- Export artifacts must be encrypted at rest (AES-256).
- Export access logs retained 3 years (PDPL Article 19).

## Dependencies

| Service                         | Purpose                                       |
|---------------------------------|-----------------------------------------------|
| `audit_ledger`                  | Source data and audit emission                |
| `consent_registry`              | Consent state snapshots for export            |
| `identity_rbac`                 | Caller authorisation                          |
| `shared/SERVICE_REGISTRY.json`  | Peer discovery                                |
