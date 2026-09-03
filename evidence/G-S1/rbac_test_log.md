# G-S1 — RBAC Protected Routes + 403 Audit Status

## Pre-existing state (before P02)

| Route | Role guard | 403 emits audit? |
|-------|-----------|-----------------|
| `GET /api/auth/me` | `get_current_user` (401 only) | No |
| All other routes | None defined | N/A |

## Post-P02 state

`require_role(*roles)` in `auth_dependencies.py` now:
1. Calls `get_current_user` (HTTP 401 if not authenticated)
2. If role not in allowed roles → calls `emit_audit('access.denied', {...})` **before** raising
3. Raises HTTP 403

Every 403 from role mismatch now produces an `access.denied` audit event with:
- `user_id`
- `role` (the role the user actually has)
- `attempted_resource` (URL path)
- `correlation_id` (UUID — for log correlation)

## Routes with require_role in place after P02

| Route | Allowed roles |
|-------|--------------|
| `PATCH /api/consultations/{id}` | veterinarian, clinic_admin |
| `POST /api/consultations` | veterinarian, clinic_admin |
| `POST /api/consultations/{id}/sign` | veterinarian |
| `GET /api/consultations/{id}/verify` | all authenticated |
| `POST /api/adverse-events` | veterinarian, clinic_admin, platform_admin |
| `PATCH /api/adverse-events/{id}/status` | platform_admin |

## Fix-F3: admin_hub.viewed alias

Location: caller code emits aliased events per role.

```python
if user.role == 'clinic_admin':
    emit_audit('clinic_admin.viewed', {...})
elif user.role == 'platform_admin':
    emit_audit('platform_admin.viewed', {...})
emit_audit('admin_hub.viewed', {...})  # DEPRECATED alias — remove in v2.0
```

Both the role-specific event AND the backward-compat alias are always emitted.
