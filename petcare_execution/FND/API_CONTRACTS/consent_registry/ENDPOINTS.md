# Consent Registry — API Endpoints

## Service Prefix

`/v1/consent`

## Endpoints

### Consent Grant & Revocation

#### GET /v1/consent/{owner_id}
List all consent records for an owner.

| Auth     | `admin`, `vet` (assigned scope only), or owner matching `owner_id` |
|----------|---------------------------------------------------------------------|
| Response | Paginated list of ConsentRecord objects |

---

#### GET /v1/consent/{owner_id}/{scope_id}
Get a specific consent scope for an owner.

| Auth     | `admin`, or owner matching `owner_id` |
|----------|---------------------------------------|
| Response 200 | ConsentRecord |
| Response 404 | `NOT_FOUND_CONSENT_SCOPE` |

---

#### POST /v1/consent/{owner_id}/{scope_id}/grant
Grant a consent scope.

| Auth     | Owner matching `owner_id` |
|----------|---------------------------|
| Body     | `{ "purpose": "veterinary_care", "acknowledged_at": "..." }` |
| Response 201 | ConsentRecord |
| Response 409 | `CONFLICT_ALREADY_GRANTED` |

---

#### POST /v1/consent/{owner_id}/{scope_id}/revoke
Revoke a consent scope.

| Auth     | Owner matching `owner_id` |
|----------|---------------------------|
| Body     | `{ "revocation_reason": "..." }` (optional) |
| Response 200 | ConsentRecord (state: revoked) |
| Response 404 | `NOT_FOUND_CONSENT_SCOPE` |
| Response 409 | `CONFLICT_ALREADY_REVOKED` |

---

### Consent Checks (Service-to-Service)

#### POST /v1/consent/check
Check whether a consent scope is active for a given owner/purpose combination.
Called by downstream services before accessing owner data.

| Auth     | `service_internal` |
|----------|--------------------|
| Body     | `{ "owner_id": "...", "scope_id": "...", "caller_role": "vet", "purpose": "veterinary_care" }` |
| Response 200 | `{ "allowed": true\|false, "reason": "...", "expires_at": "...\|null" }` |

---

### History

#### GET /v1/consent/{owner_id}/history
Full audit trail of consent state changes for an owner.

| Auth     | `admin`, or owner matching `owner_id` |
|----------|---------------------------------------|
| Response | Paginated list of ConsentHistoryEntry objects |

---

### Health

#### GET /v1/consent/health
No auth required.

| Response 200 | `{ "status": "ok", "service": "consent_registry", "version": "0.1.0-scaffold" }` |
