# Audit Ledger — API Endpoints

## Service Prefix

`/v1/audit`

## Endpoints

### Event Append (Write)

#### POST /v1/audit/events
Append a single audit event to the ledger. Caller must have role `service_internal`.

| Auth     | `service_internal` JWT                |
|----------|---------------------------------------|
| Body     | AuditEventRequest                     |
| Response 201 | AuditEventResponse (with sequence_no and hashes) |
| Response 422 | `VALIDATION_REQUIRED_FIELD` (missing mandatory fields) |
| Response 502 | `UPSTREAM_AUDIT_LEDGER` (if replica write fails) |

Note: append operations are synchronous. The 201 response confirms the event is durably
persisted on both primary and replica before returning.

---

#### POST /v1/audit/events/batch
Append up to 100 events atomically (all succeed or all fail).

| Auth     | `service_internal` JWT                |
|----------|---------------------------------------|
| Body     | `{ "events": [ AuditEventRequest, ... ] }` |
| Response 201 | `{ "appended": <int>, "first_sequence_no": <int> }` |
| Response 422 | If any event fails validation — entire batch rejected |

---

### Event Read

#### GET /v1/audit/events
List audit events with cursor pagination and filtering.

| Auth     | `admin` or `evidence_export` service account |
|----------|----------------------------------------------|
| Params   | `limit`, `cursor`, `filter[event_type]`, `filter[principal_id]`, `filter[ts_utc][gte]`, `filter[ts_utc][lte]` |
| Response | Paginated AuditEventResponse list |

---

#### GET /v1/audit/events/{event_id}
Get a single event by ID.

| Auth     | `admin` or `evidence_export` service account |
|----------|----------------------------------------------|
| Response 200 | AuditEventResponse |
| Response 404 | `NOT_FOUND_RESOURCE` |

---

### Integrity Verification

#### GET /v1/audit/verify
Verify hash chain integrity over a sequence range.

| Auth     | `admin`                               |
|----------|---------------------------------------|
| Params   | `from_sequence` (default 0), `to_sequence` (default latest) |
| Response | `{ "valid": true\|false, "checked": <int>, "broken_at_sequence": <int>\|null }` |

---

### Health

#### GET /v1/audit/health
No auth required.

| Response 200 | `{ "status": "ok", "service": "audit_ledger", "version": "0.1.0-scaffold", "sequence_head": <int> }` |
