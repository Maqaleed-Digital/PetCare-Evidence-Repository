# Vet Surface — Deferred Runtime Gaps

## Phase

PH-FND-4 · Source UI: PH-UI-3 (not yet built)

---

## Gap Registry

### GAP-VET-01: Vet surface UI components not built

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                  |
| Affects      | All vet-surface components                                                 |
| Blocker      | PH-UI-3 is a future delivery; no React components exist yet               |
| Impact       | Entire vet surface is a placeholder (`/vet` route)                        |
| Resolution   | Build PH-UI-3 components following the SURFACE_MAPPING contract           |

---

### GAP-VET-02: vet-service not implemented

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                  |
| Affects      | VetPatientList, AppointmentSchedule                                        |
| Blocker      | `vet-service` not in PH-FND-2 scope; no API contract yet                 |
| Impact       | Patient list and schedule data unavailable                                |
| Resolution   | Add vet-service to service registry in a future PH-FND iteration         |

---

### GAP-VET-03: clinical_signoff ready but not proxied

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | PatientRecordViewer, SignoffQueue, SignoffApproveReject                    |
| Blocker      | None — `clinical_signoff` contract defined in PH-FND-3                   |
| Impact       | Signoff workflow cannot be used; no Route Handlers created yet            |
| Resolution   | Create `/api/vet/signoff/*` Route Handlers when PH-UI-3 is built         |

---

### GAP-VET-04: Self-signoff policy not surfaced in UI

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | SignoffApproveReject component                                             |
| Blocker      | Clinic-level `allows_self_signoff` flag not yet configurable in admin UI  |
| Impact       | Self-signoff guard (`GAP-VET-04` from SIGNOFF_GUARDS.md) cannot be shown |
| Resolution   | Expose clinic config flag in Admin surface; propagate to signoff UI       |

---

### GAP-VET-05: Consent status indicator per patient

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | VetPatientList — consent status column                                    |
| Blocker      | Requires `consent_registry` check per patient in list → N+1 risk         |
| Impact       | Consent status shown as "unknown" until batch consent API is available   |
| Resolution   | Add batch consent check endpoint to `consent_registry` in future phase   |
