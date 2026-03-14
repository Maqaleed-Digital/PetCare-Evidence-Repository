# Clinical Signoff — API Endpoints

## Service Prefix

`/v1/signoff`

## Endpoints

### Record Lifecycle

#### POST /v1/signoff/records
Create a new clinical record in DRAFT state.

| Auth     | `vet`                                  |
|----------|----------------------------------------|
| Body     | SignoffRecordCreateRequest             |
| Response 201 | SignoffRecord (state: DRAFT)       |
| Response 403 | `FORBIDDEN_CONSENT_REQUIRED` if owner consent not active |

---

#### GET /v1/signoff/records/{record_id}
Get a clinical record.

| Auth     | `vet` (assigned), `admin`             |
|----------|---------------------------------------|
| Response 200 | SignoffRecord |
| Response 404 | `NOT_FOUND_RESOURCE` |

---

#### PATCH /v1/signoff/records/{record_id}
Update a DRAFT record (only permitted in DRAFT state).

| Auth     | `vet` (creator)                        |
|----------|----------------------------------------|
| Body     | Partial SignoffRecord (DRAFT fields only) |
| Response 200 | Updated SignoffRecord |
| Response 409 | `CONFLICT_STATE_TRANSITION` if not in DRAFT |
| Response 422 | `VALIDATION_IMMUTABLE_FIELD` if attempt to patch sealed fields |

---

### State Transitions

#### POST /v1/signoff/records/{record_id}/submit
Submit a DRAFT record for vet review → PENDING.

| Auth     | `vet`                                  |
|----------|----------------------------------------|
| Response 200 | SignoffRecord (state: PENDING) |
| Response 409 | `CONFLICT_STATE_TRANSITION` if not in DRAFT |
| Response 422 | `VALIDATION_REQUIRED_FIELD` if required fields incomplete |

---

#### POST /v1/signoff/records/{record_id}/approve
Approve a PENDING record → APPROVED (sealed).

| Auth     | `vet` (license_status: active)         |
|----------|----------------------------------------|
| Response 200 | SignoffRecord (state: APPROVED, record_seal_hash set) |
| Response 409 | `CONFLICT_STATE_TRANSITION` if not in PENDING |

---

#### POST /v1/signoff/records/{record_id}/reject
Reject a PENDING record → REJECTED.

| Auth     | `vet`                                  |
|----------|----------------------------------------|
| Body     | `{ "reason": "..." }` (min 10 chars)   |
| Response 200 | SignoffRecord (state: REJECTED) |
| Response 422 | `VALIDATION_REQUIRED_FIELD` if reason too short |

---

#### POST /v1/signoff/records/{record_id}/supersede
Supersede an APPROVED record (admin only).

| Auth     | `admin`                                |
|----------|----------------------------------------|
| Body     | `{ "superseding_record_id": "...", "reason": "..." }` (min 20 chars) |
| Response 200 | SignoffRecord (state: SUPERSEDED) |

---

### Verification & History

#### GET /v1/signoff/records/{record_id}/verify
Verify seal hash of an APPROVED record.

| Auth     | `vet` (assigned), `admin`             |
|----------|---------------------------------------|
| Response | `{ "valid": true\|false, "expected_hash": "...", "actual_hash": "..." }` |

---

#### GET /v1/signoff/records/{record_id}/history
Full version chain for a record.

| Auth     | `admin`                               |
|----------|---------------------------------------|
| Response | List of SignoffRecord stubs with state and links |

---

### Health

#### GET /v1/signoff/health
No auth required.

| Response 200 | `{ "status": "ok", "service": "clinical_signoff", "version": "0.1.0-scaffold" }` |
