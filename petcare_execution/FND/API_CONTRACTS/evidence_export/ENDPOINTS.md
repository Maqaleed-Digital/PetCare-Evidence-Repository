# Evidence Export — API Endpoints

## Service Prefix

`/v1/export`

## Endpoints

### Export Requests

#### POST /v1/export/requests
Create a new export request. Caller must have `admin` role with active `cs-evidence-export` scope.

| Auth     | `admin` + active `cs-evidence-export` consent |
|----------|------------------------------------------------|
| Body     | ExportRequest                                  |
| Response 201 | ExportRequestResponse (status: pending)    |
| Response 403 | `FORBIDDEN_CONSENT_REQUIRED` or `FORBIDDEN_INSUFFICIENT_ROLE` |
| Response 422 | `VALIDATION_REQUIRED_FIELD` or `VALIDATION_INVALID_ENUM` |

For `full_compliance` export type or >12 month range, a second admin approval is required.
The response will have status `awaiting_approval` until the second admin approves.

---

#### POST /v1/export/requests/{export_id}/approve
Second admin approves a dual-approval export request.

| Auth     | `admin` (different principal from requester) |
|----------|----------------------------------------------|
| Response 200 | ExportRequestResponse (status: processing) |
| Response 409 | `CONFLICT_SELF_APPROVAL` if same admin as requester |

---

#### GET /v1/export/requests/{export_id}
Get status and metadata of an export request.

| Auth     | `admin`                                |
|----------|----------------------------------------|
| Response 200 | ExportRequestResponse |
| Response 404 | `NOT_FOUND_RESOURCE` |

---

#### GET /v1/export/requests
List export requests for the caller's clinic.

| Auth     | `admin`                                |
|----------|----------------------------------------|
| Params   | `limit`, `cursor`, `filter[status]`, `filter[export_type]` |
| Response | Paginated ExportRequestResponse list   |

---

### Artifact Download

#### GET /v1/export/requests/{export_id}/download
Download the export artifact. Returns a pre-signed redirect URL (1-hour TTL).
Maximum 3 downloads per artifact lifetime.

| Auth     | `admin`                                |
|----------|----------------------------------------|
| Response 302 | Redirect to pre-signed download URL |
| Response 403 | `FORBIDDEN_DOWNLOAD_LIMIT_REACHED` if >3 downloads |
| Response 404 | `NOT_FOUND_RESOURCE` |
| Response 410 | `GONE_ARTIFACT_EXPIRED` if artifact TTL elapsed |

---

### Health

#### GET /v1/export/health
No auth required.

| Response 200 | `{ "status": "ok", "service": "evidence_export", "version": "0.1.0-scaffold" }` |
