# Identity RBAC — API Endpoints

## Service Prefix

`/v1/identity`

## Endpoints

### Authentication

#### POST /v1/identity/token
Issue a JWT for a verified principal.

| Field        | Value                                |
|--------------|--------------------------------------|
| Auth         | None (credential exchange)           |
| Body         | `{ "principal_id": "...", "credential_hash": "..." }` |
| Response 200 | `{ "token": "<jwt>", "expires_at": "..." }` |
| Response 401 | `UNAUTHORIZED_INVALID_CREDENTIALS`   |

---

#### POST /v1/identity/token/refresh
Refresh a non-expired JWT.

| Field        | Value                                |
|--------------|--------------------------------------|
| Auth         | Bearer JWT (current)                 |
| Body         | None                                 |
| Response 200 | `{ "token": "<jwt>", "expires_at": "..." }` |

---

#### DELETE /v1/identity/token
Revoke current JWT (logout).

| Field        | Value                                |
|--------------|--------------------------------------|
| Auth         | Bearer JWT                           |
| Response 204 | No content                           |

---

### Role Management

#### GET /v1/identity/roles
List all defined roles.

| Auth     | `admin`                  |
|----------|--------------------------|
| Response | Paginated list of role objects |

---

#### GET /v1/identity/principals/{principal_id}/roles
Get roles assigned to a principal.

| Auth     | `admin` or self          |
|----------|--------------------------|
| Response | `{ "principal_id": "...", "roles": [...] }` |

---

#### POST /v1/identity/principals/{principal_id}/roles
Assign a role to a principal.

| Auth     | `admin`                  |
|----------|--------------------------|
| Body     | `{ "role": "vet", "clinic_id": "..." }` |
| Response 201 | Role assignment object |
| Response 409 | `CONFLICT_ROLE_ALREADY_ASSIGNED` |

---

#### DELETE /v1/identity/principals/{principal_id}/roles/{role}
Revoke a role from a principal.

| Auth     | `admin`                  |
|----------|--------------------------|
| Response 204 | No content           |
| Response 404 | `NOT_FOUND_ROLE_ASSIGNMENT` |

---

### Access Decisions

#### POST /v1/identity/access/check
Evaluate an access decision without side effects.

| Auth     | Any service account (`service_internal` role) |
|----------|-----------------------------------------------|
| Body     | `{ "principal_id": "...", "action": "read", "resource_type": "health_timeline", "context": {...} }` |
| Response 200 | `{ "allowed": true\|false, "reason": "..." }` |

---

### Health

#### GET /v1/identity/health
Service liveness check. No auth required.

| Response 200 | `{ "status": "ok", "service": "identity_rbac", "version": "0.1.0-scaffold" }` |
