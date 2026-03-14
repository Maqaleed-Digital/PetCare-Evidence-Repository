# Audit Ledger — Audit Trigger Rules

## Principle

Every service that mutates state or makes an access decision **must** emit an audit event
to `audit_ledger` before returning a response to its caller. Failure to emit is treated
as a policy violation equivalent to a security incident.

## Mandatory Trigger Table

| Source Service      | Triggering Condition                         | Event Type               | Outcome Field  |
|---------------------|----------------------------------------------|--------------------------|----------------|
| `identity_rbac`     | JWT issued                                   | *(not audited)*          | —              |
| `identity_rbac`     | JWT revoked                                  | `access_denied`          | `deny`         |
| `identity_rbac`     | Role assigned                                | `role_assigned`          | `allow`        |
| `identity_rbac`     | Role revoked                                 | `role_revoked`           | `allow`        |
| `identity_rbac`     | Access check → DENY                          | `access_denied`          | `deny`         |
| `consent_registry`  | Consent granted                              | `consent_granted`        | `allow`        |
| `consent_registry`  | Consent revoked                              | `consent_revoked`        | `allow`        |
| `consent_registry`  | Consent check performed (any outcome)        | `consent_checked`        | `allow`/`deny` |
| `clinical_signoff`  | Record submitted for review                  | `signoff_requested`      | `allow`        |
| `clinical_signoff`  | Record approved                              | `signoff_approved`       | `allow`        |
| `clinical_signoff`  | Record rejected                              | `signoff_rejected`       | `deny`         |
| `clinical_signoff`  | Record superseded                            | `signoff_superseded`     | `allow`        |
| `evidence_export`   | Export artifact created                      | `export_created`         | `allow`        |
| `evidence_export`   | Export artifact downloaded                   | `export_downloaded`      | `allow`        |
| `evidence_export`   | Export artifact expired and purged           | `export_expired`         | `allow`        |

## Emission Timing

Audit events must be emitted **synchronously** before the HTTP response is returned to the
caller. The sequence is:

```
1. Validate request
2. Perform action (state mutation or access decision)
3. POST /v1/audit/events  ← synchronous
4. If audit_ledger returns non-2xx → rollback action, return 502 UPSTREAM_AUDIT_LEDGER
5. Return response to caller
```

This guarantees that every committed action has a corresponding audit record.

## Fail-Secure Rule

If `audit_ledger` is unavailable:
- State mutations are **rolled back**.
- Access decisions are **denied**.
- The caller receives `502 UPSTREAM_AUDIT_LEDGER`.

Silently proceeding without an audit record is **never permitted**.

## PII in Audit Events

Audit events must not contain raw PII. Permitted identifiers:
- `principal_id` (opaque UUID)
- `resource_id` (opaque UUID)
- `clinic_id`, `pharmacy_id` (opaque UUIDs)

Prohibited in `detail` object:
- Owner names, pet names, phone numbers, email addresses, physical addresses.
