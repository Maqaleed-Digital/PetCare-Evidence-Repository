# Audit Ledger — Service Boundary

## Service Identity

| Field        | Value                          |
|--------------|--------------------------------|
| Service Name | `audit_ledger`                 |
| Version      | `0.1.0-scaffold`               |
| Phase        | PH-FND-2                       |
| Owner        | Platform Foundation            |

## Responsibility

`audit_ledger` provides an append-only, tamper-evident log of all material events across the
petcare platform. It is the single source of truth for compliance, incident investigation, and
regulatory reporting.

## Boundaries

### In scope
- Accepting audit event appends from authorised services
- Hash-chain maintenance (each event links to previous event hash)
- Audit event reads (with cursor-based pagination)
- Integrity verification endpoint (`/v1/audit/verify`)
- Event retention and archival scheduling

### Out of scope
- Access control enforcement → `identity_rbac`
- Consent lifecycle → `consent_registry`
- Evidence packaging → `evidence_export`
- Real-time alerting → separate alerting pipeline

## Interfaces

| Direction | Protocol | Endpoint prefix   | Notes                                      |
|-----------|----------|-------------------|--------------------------------------------|
| Inbound   | HTTP/1.1 | `/v1/audit/`      | Write: service accounts only               |
| Inbound   | HTTP/1.1 | `/v1/audit/`      | Read: admin and evidence_export roles only |

## PDPL Constraints

- Article 19: audit records retained for minimum 3 years.
- Audit events must not be deleted or modified after append.
- Audit events containing PII must be pseudonymised before any external export.

## Dependencies

| Service                         | Purpose                          |
|---------------------------------|----------------------------------|
| `shared/SERVICE_REGISTRY.json`  | Peer discovery                   |

## Callers (write)

| Caller Service      | Event Categories Emitted                           |
|---------------------|----------------------------------------------------|
| `identity_rbac`     | access_denied, role_assigned, role_revoked         |
| `consent_registry`  | consent_granted, consent_revoked, consent_checked  |
| `clinical_signoff`  | signoff_requested, signoff_approved, signoff_rejected |
| `evidence_export`   | export_created, export_downloaded, export_expired  |
