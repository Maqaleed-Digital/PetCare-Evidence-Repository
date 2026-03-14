# Consent Registry — Service Boundary

## Service Identity

| Field        | Value                          |
|--------------|--------------------------------|
| Service Name | `consent_registry`             |
| Version      | `0.1.0-scaffold`               |
| Phase        | PH-FND-2                       |
| Owner        | Platform Foundation            |

## Responsibility

`consent_registry` is the single source of truth for data-subject consent under the Saudi
Personal Data Protection Law (PDPL). It stores, enforces, and audits all consent grants
and revocations for petcare data subjects (pet owners).

## Boundaries

### In scope
- Consent grant and revocation lifecycle
- Purpose-limitation enforcement (consent scope vs. requested access)
- Consent status reads by authorised services
- Consent audit trail (all state transitions logged)

### Out of scope
- Role-based access enforcement → `identity_rbac`
- Clinical data storage → external clinical services
- Evidence packaging → `evidence_export`

## Interfaces

| Direction | Protocol | Endpoint prefix         | Notes                                    |
|-----------|----------|-------------------------|------------------------------------------|
| Inbound   | HTTP/1.1 | `/v1/consent/`          | Internal cluster only                    |
| Outbound  | HTTP/1.1 | `audit_ledger /v1/events` | Append consent state-change events     |

## PDPL Constraints

- Article 5: consent must be freely given, specific, informed, and unambiguous.
- Article 17: data subject may withdraw consent at any time; revocation processed ≤ 72 h.
- Article 19: consent records retained for minimum 3 years post-expiry.
- No cross-border transfer of consent records without explicit SDAIA approval.

## Dependencies

| Service                         | Purpose                             |
|---------------------------------|-------------------------------------|
| `audit_ledger`                  | Emit consent-change audit events    |
| `identity_rbac`                 | Validate caller authorisation       |
| `shared/SERVICE_REGISTRY.json`  | Peer discovery                      |
