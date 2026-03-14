# Identity RBAC — API Authorization Rules

## Caller Matrix

| Endpoint                                          | Permitted Callers                   |
|---------------------------------------------------|-------------------------------------|
| `POST /v1/identity/token`                         | Unauthenticated (credential exchange) |
| `POST /v1/identity/token/refresh`                 | Any valid JWT holder                |
| `DELETE /v1/identity/token`                       | Any valid JWT holder                |
| `GET /v1/identity/roles`                          | `admin`                             |
| `GET /v1/identity/principals/{id}/roles`          | `admin`, or principal matching `id` |
| `POST /v1/identity/principals/{id}/roles`         | `admin`                             |
| `DELETE /v1/identity/principals/{id}/roles/{role}`| `admin`                             |
| `POST /v1/identity/access/check`                  | `service_internal`                  |
| `GET /v1/identity/health`                         | Unauthenticated                     |

## Self-Access Rule

A principal with any role may read their own role assignments:

```
GET /v1/identity/principals/{id}/roles
```

Where `id == jwt.sub`. An `admin` may read any principal's roles.

## Role Elevation Prohibition

An `admin` may not grant a role higher than their own. Specifically:
- Admins cannot grant `service_internal`.
- Admins cannot grant `admin` without a platform-level approval (two-admin rule).

## Audit Events Emitted

| Action                  | Audit Event Type   |
|-------------------------|--------------------|
| Role assigned           | `role_assigned`    |
| Role revoked            | `role_revoked`     |
| Access check → DENY     | `access_denied`    |
| Token revoked           | `access_denied` (outcome: revoke) |

All `access_denied` events include `principal_id`, `action`, `resource_type`, and `ts_utc`.
They are emitted to `audit_ledger` synchronously before returning the 403 response.
If `audit_ledger` is unavailable, the request is **rejected** (fail-secure) rather than
silently allowed without an audit record.

## Rate Limiting (Token Endpoint)

`POST /v1/identity/token` is rate-limited to 10 requests per principal per minute.
Exceeded → `429 RATE_LIMITED_TOKEN_ISSUANCE` with `Retry-After` header.
