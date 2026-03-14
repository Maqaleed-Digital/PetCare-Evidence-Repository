# Clinical Signoff — Signoff Guards

## Purpose

Signoff guards are pre-conditions that must pass before a state transition is permitted.
Guards are evaluated in the order listed; the first failure halts evaluation and returns
the corresponding error.

## Guard Evaluation Order

### submit (DRAFT → PENDING)

| # | Guard                                    | Failure Response                                      |
|---|------------------------------------------|-------------------------------------------------------|
| 1 | `record.state == "DRAFT"`               | `409 CONFLICT_STATE_TRANSITION`                       |
| 2 | `identity_rbac.can(caller, "sign", record)` → ALLOW | `403 FORBIDDEN_INSUFFICIENT_ROLE`          |
| 3 | `consent_registry.check(owner_id, "cs-health-write", "vet", "veterinary_care")` → allowed | `403 FORBIDDEN_CONSENT_REQUIRED` |
| 4 | `record.content_hash` present and non-empty | `422 VALIDATION_REQUIRED_FIELD`                   |

---

### approve (PENDING → APPROVED)

| # | Guard                                    | Failure Response                                      |
|---|------------------------------------------|-------------------------------------------------------|
| 1 | `record.state == "PENDING"`             | `409 CONFLICT_STATE_TRANSITION`                       |
| 2 | `identity_rbac.can(caller, "sign", record)` → ALLOW | `403 FORBIDDEN_INSUFFICIENT_ROLE`          |
| 3 | `caller.license_status == "active"`     | `403 FORBIDDEN_LICENCE_INACTIVE`                      |
| 4 | Self-signoff check: `caller.id != record.created_by` OR `clinic.allows_self_signoff == true` | `403 FORBIDDEN_SELF_SIGNOFF` |
| 5 | `consent_registry.check(owner_id, "cs-health-write", "vet", "veterinary_care")` → allowed | `403 FORBIDDEN_CONSENT_REQUIRED` |

---

### reject (PENDING → REJECTED)

| # | Guard                                    | Failure Response                                      |
|---|------------------------------------------|-------------------------------------------------------|
| 1 | `record.state == "PENDING"`             | `409 CONFLICT_STATE_TRANSITION`                       |
| 2 | `identity_rbac.can(caller, "sign", record)` → ALLOW | `403 FORBIDDEN_INSUFFICIENT_ROLE`          |
| 3 | `body.reason.length >= 10`              | `422 VALIDATION_REQUIRED_FIELD`                       |

---

### supersede (APPROVED → SUPERSEDED)

| # | Guard                                    | Failure Response                                      |
|---|------------------------------------------|-------------------------------------------------------|
| 1 | `record.state == "APPROVED"`            | `409 CONFLICT_STATE_TRANSITION`                       |
| 2 | `identity_rbac.can(caller, "update", record)` with role `admin` → ALLOW | `403 FORBIDDEN_INSUFFICIENT_ROLE` |
| 3 | `superseding_record.state == "APPROVED"` | `422 VALIDATION_REQUIRED_FIELD`                      |
| 4 | `body.reason.length >= 20`              | `422 VALIDATION_REQUIRED_FIELD`                       |

---

## Immutability Guards (PATCH)

PATCH requests on any record in a non-DRAFT state are rejected:

```
409 CONFLICT_STATE_TRANSITION: Record is not in DRAFT state — mutations not permitted.
```

Additionally, the following fields are immutable even in DRAFT:

| Field           | Immutable from  |
|-----------------|-----------------|
| `record_id`     | Creation        |
| `owner_id`      | Creation        |
| `pet_id`        | Creation        |
| `created_by`    | Creation        |
| `created_at`    | Creation        |
| `record_seal_hash` | Set on approve |
| `approved_by`   | Set on approve  |
| `approved_at`   | Set on approve  |

Attempt to PATCH any of these fields returns:
`422 VALIDATION_IMMUTABLE_FIELD`.
