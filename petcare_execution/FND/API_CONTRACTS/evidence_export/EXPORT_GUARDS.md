# Evidence Export — Export Guards

## Guard Evaluation (POST /v1/export/requests)

Guards are evaluated in strict order. First failure halts and returns the listed response.

| # | Guard                                                                 | Failure Response                              |
|---|-----------------------------------------------------------------------|-----------------------------------------------|
| 1 | `identity_rbac.can(caller, "create", "evidence_export")` → ALLOW     | `403 FORBIDDEN_INSUFFICIENT_ROLE`             |
| 2 | `consent_registry.check(caller.clinic_id, "cs-evidence-export", "admin", "regulatory_compliance")` → allowed | `403 FORBIDDEN_CONSENT_REQUIRED` |
| 3 | `caller.is_active == true`                                            | `403 FORBIDDEN_PRINCIPAL_SUSPENDED`           |
| 4 | `scope.from_date < scope.to_date`                                     | `422 VALIDATION_REQUIRED_FIELD`               |
| 5 | Date range ≤ 24 months                                                | `422 VALIDATION_DATE_RANGE_TOO_LARGE`         |
| 6 | If `cross_border == true`: `sdaia_approval_ref` present and non-empty | `422 VALIDATION_REQUIRED_FIELD`               |
| 7 | If `export_type == "full_compliance"` or range > 12 months: dual-approval required | Set `status = awaiting_approval`, return 201 |
| 8 | `pseudonymised` forced to `true` (no override permitted)             | N/A — enforced server-side                    |

## Dual-Approval Guard (POST /v1/export/requests/{id}/approve)

| # | Guard                                                | Failure Response                     |
|---|------------------------------------------------------|--------------------------------------|
| 1 | `export_request.status == "awaiting_approval"`       | `409 CONFLICT_STATE_TRANSITION`      |
| 2 | `caller.id != export_request.requested_by`           | `409 CONFLICT_SELF_APPROVAL`         |
| 3 | `identity_rbac.can(caller, "create", "evidence_export")` → ALLOW | `403 FORBIDDEN_INSUFFICIENT_ROLE` |

## Download Guard (GET /v1/export/requests/{id}/download)

| # | Guard                                                | Failure Response                     |
|---|------------------------------------------------------|--------------------------------------|
| 1 | `export_request.status == "ready"`                   | `410 GONE_ARTIFACT_EXPIRED` if expired, else `422` |
| 2 | `export_request.expires_at > now()`                  | `410 GONE_ARTIFACT_EXPIRED`          |
| 3 | `export_request.download_count < 3`                  | `403 FORBIDDEN_DOWNLOAD_LIMIT_REACHED` |
| 4 | `identity_rbac.can(caller, "read", "evidence_export")` → ALLOW | `403 FORBIDDEN_INSUFFICIENT_ROLE` |

## Pseudonymisation Enforcement

`evidence_export` applies pseudonymisation unconditionally before packaging:

```
raw field → pseudonymised value
owner name → OWNER-{sha256(owner_id)[:8]}
pet name   → PET-{sha256(pet_id)[:8]}
vet name   → VET-{sha256(vet_id)[:8]}
phone      → REDACTED
```

Any attempt to disable pseudonymisation via request body is silently ignored.
The `pseudonymised: true` flag is always set in the response.

## Prohibited Export Patterns

| Pattern                                               | Enforcement                            |
|-------------------------------------------------------|----------------------------------------|
| Raw PII in any export type                            | Hard block — pseudonymisation applied  |
| Clinical notes or prescription content                | Not included in any export type        |
| Cross-border without SDAIA ref                        | `422 VALIDATION_REQUIRED_FIELD`        |
| Exports by suspended principal                        | `403 FORBIDDEN_PRINCIPAL_SUSPENDED`    |
| Single admin approving dual-approval request          | `409 CONFLICT_SELF_APPROVAL`           |
| Downloading after TTL                                 | `410 GONE_ARTIFACT_EXPIRED`            |
