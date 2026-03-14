# Vet Surface — UI Integration Mapping

## Phase

PH-FND-4 · Source UI: PH-UI-3 (`/vet`) — placeholder shell

## Surface Overview

The Vet surface is a placeholder shell defined in `docs/VET_SURFACE.md`. No components
have been built yet (PH-UI-3 is a future delivery). This mapping documents the intended
integration contracts so that the component build phase can proceed directly to wiring.

## Intended Component Set

| Component                  | Purpose                                              |
|----------------------------|------------------------------------------------------|
| `VetPatientList`           | List of assigned patients with consent status        |
| `PatientRecordViewer`      | Read clinical record for a specific patient          |
| `SignoffQueue`             | List of records awaiting vet signoff (PENDING state) |
| `SignoffApproveReject`     | Approve or reject a pending clinical record          |
| `AppointmentSchedule`      | Vet's daily/weekly appointment schedule              |
| `PrescriptionCreator`      | Draft a new prescription (disabled in shell)         |

---

## Component → API Contract Map

### VetPatientList

| Field             | Live API Target                                              | Service            | Consent Scope      |
|-------------------|--------------------------------------------------------------|--------------------|--------------------|
| Assigned patients | `GET /v1/vet/patients?vet_id={id}`                          | vet-service        | None (role-scoped) |
| Consent status    | `GET /v1/consent/{owner_id}/cs-health-read` per patient     | consent_registry   | N/A (admin check)  |

**Consent required:** No — vet is reading their assigned patient list, not clinical data.
Consent status is shown as an indicator (green/amber/red) per patient row.

---

### PatientRecordViewer

| Field             | Live API Target                                              | Service            | Consent Scope      |
|-------------------|--------------------------------------------------------------|--------------------|--------------------|
| Clinical records  | `GET /v1/signoff/records?pet_id={id}`                       | clinical_signoff   | `cs-health-read`  |
| Record detail     | `GET /v1/signoff/records/{record_id}`                        | clinical_signoff   | `cs-health-read`  |

**Consent required:** `cs-health-read` must be `granted`. Route Handler checks consent
before fetching records; returns `ConsentRequiredBanner` if not granted.

---

### SignoffQueue

| Field             | Live API Target                                              | Service            |
|-------------------|--------------------------------------------------------------|--------------------|
| Pending records   | `GET /v1/signoff/records?state=PENDING&assigned_vet={id}`   | clinical_signoff   |

**Identity check:** `identity_rbac.can(vet, "read", "clinical_signoff")` → ALLOW required.

---

### SignoffApproveReject (disabled in shell)

| Action    | Live API Target                                              | Service            | Guard                                    |
|-----------|--------------------------------------------------------------|--------------------|------------------------------------------|
| Approve   | `POST /v1/signoff/records/{id}/approve`                     | clinical_signoff   | vet role + active license + consent      |
| Reject    | `POST /v1/signoff/records/{id}/reject` + `{ "reason": "..." }` | clinical_signoff | vet role + reason ≥ 10 chars             |

Both emit `signoff_approved` / `signoff_rejected` to `audit_ledger` (synchronous, fail-secure).

---

### AppointmentSchedule

| Field            | Live API Target                                                | Service       |
|------------------|----------------------------------------------------------------|---------------|
| Vet schedule     | `GET /v1/vet/appointments?vet_id={id}&date={date}`            | vet-service   |

---

## Route Handler Proxy Paths (petcare-web — planned)

| Component             | Proxy Route                                   | Upstream                                        |
|-----------------------|-----------------------------------------------|-------------------------------------------------|
| Patient list          | `GET /api/vet/patients`                       | `GET /v1/vet/patients`                          |
| Clinical records      | `GET /api/vet/records/[petId]`                | `GET /v1/signoff/records?pet_id={petId}`        |
| Signoff queue         | `GET /api/vet/signoff/queue`                  | `GET /v1/signoff/records?state=PENDING`         |
| Approve record        | `POST /api/vet/signoff/[recordId]/approve`    | `POST /v1/signoff/records/{recordId}/approve`   |
| Reject record         | `POST /api/vet/signoff/[recordId]/reject`     | `POST /v1/signoff/records/{recordId}/reject`    |
| Consent pre-check     | `GET /api/consent/[ownerId]/cs-health-read`   | `GET /v1/consent/{ownerId}/cs-health-read`      |
