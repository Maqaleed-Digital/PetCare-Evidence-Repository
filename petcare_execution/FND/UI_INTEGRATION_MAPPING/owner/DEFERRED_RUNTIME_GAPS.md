# Owner Surface — Deferred Runtime Gaps

## Phase

PH-FND-4 · Gaps relative to PH-UI-2 read-only shell

## Status Key

| Status      | Meaning                                                         |
|-------------|-----------------------------------------------------------------|
| `BLOCKED`   | Backend service not yet implemented — gap cannot be closed yet  |
| `DEFERRED`  | Backend contract defined; integration work deferred to future phase |
| `WIRED`     | Already integrated (live data)                                  |

---

## Gap Registry

### GAP-OWN-01: owner-service not implemented

| Field        | Value                                                                     |
|--------------|---------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                 |
| Affects      | PetProfileCard, AppointmentCard                                           |
| Blocker      | `owner-service` has no PH-FND-2/3 skeleton — not yet in scope            |
| Impact       | Pet profile and appointments remain placeholder data                      |
| Resolution   | Implement owner-service in a future PH-FND iteration                     |

---

### GAP-OWN-02: clinical-service not implemented

| Field        | Value                                                                     |
|--------------|---------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                 |
| Affects      | HealthTimeline, VaccinationCard, VaccinationSummary                       |
| Blocker      | Clinical data storage service not in scope for current foundation phases  |
| Impact       | Health timeline and vaccinations remain placeholder data                  |
| Resolution   | Implement clinical-service in future phase; `clinical_signoff` contract is ready |

---

### GAP-OWN-03: Consent check not wired into Route Handler

| Field        | Value                                                                     |
|--------------|---------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                |
| Affects      | HealthTimeline, VaccinationCard (consent-gated components)               |
| Blocker      | None — `consent_registry` contract defined in PH-FND-3                   |
| Impact       | Consent gate is not enforced; data rendered unconditionally (placeholder) |
| Resolution   | Add consent pre-check in Route Handler before proxying clinical data     |

---

### GAP-OWN-04: QuickActions write operations disabled

| Field        | Value                                                                     |
|--------------|---------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                |
| Affects      | Book Appointment, Emergency Access, Consent Settings buttons             |
| Blocker      | None for Consent Settings (consent_registry live); owner-service needed for appointments |
| Impact       | All write flows blocked at UI — buttons render as `disabled`             |
| Resolution   | Enable incrementally as upstream services go live                        |

---

### GAP-OWN-05: Real-time appointment status updates

| Field        | Value                                                                     |
|--------------|---------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                |
| Affects      | AppointmentCard status badge                                              |
| Blocker      | WebSocket / polling not in scope for current UI phases                   |
| Impact       | Appointment status is static (placeholder)                               |
| Resolution   | Add polling or SSE in a future UI phase                                  |
