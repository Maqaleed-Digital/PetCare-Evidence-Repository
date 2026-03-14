# Identity RBAC — Access Decision Rules

## Overview

Access decisions are evaluated using a `can(principal, action, resource, context)` function.
The decision engine applies rules in strict priority order: **Deny > Allow > Default-Deny**.

## Decision Algorithm

```
function can(principal, action, resource, context):
  1. If principal is suspended or inactive → DENY (no further evaluation)
  2. For each role in principal.roles:
       If role_matrix[role] has (resource, action) with scope satisfied by context:
         grant = True
  3. If grant is True → ALLOW
  4. Default → DENY
  5. Emit audit event {principal_id, action, resource, decision, ts_utc}
```

## Scope Resolution

| Scope      | Resolution Rule                                                                 |
|------------|---------------------------------------------------------------------------------|
| `own`      | `context.owner_id == principal.id`                                              |
| `assigned` | `context.pet_id` in `principal.assigned_pets` OR `context.appointment_id` in `principal.assigned_appointments` |
| `clinic`   | `context.clinic_id == principal.clinic_id`                                      |
| `pharmacy` | `context.pharmacy_id == principal.pharmacy_id`                                  |
| `emergency` | `principal` has `emergency_responder` role AND duty-status is `on_call`        |

## Denial Escalation

| Denial Type          | Audit Level | Notification           |
|----------------------|-------------|------------------------|
| Inactive principal   | WARN        | None                   |
| Scope violation      | ERROR       | Admin alert            |
| Privilege escalation | CRITICAL    | Admin alert + incident |

## Cross-Service Trust

Services within the cluster may call `identity_rbac` via service-account token with role
`service_internal`. Service accounts are granted **read-only** access to the role matrix
and **no** access to pet or clinical resources.

## PDPL Notes

- Consent must be `ACTIVE` before any `vet` action on `health_timeline` or `vaccination`.
- `identity_rbac` does not check consent directly; callers must verify via `consent_registry`
  before invoking clinical resources.
- All DENY events are retained for 3 years in `audit_ledger` per PDPL Article 19.
