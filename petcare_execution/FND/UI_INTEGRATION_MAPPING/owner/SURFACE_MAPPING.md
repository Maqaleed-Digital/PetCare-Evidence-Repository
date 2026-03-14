# Owner Surface — UI Integration Mapping

## Phase

PH-FND-4 · Source UI: PH-UI-2 (`/owner`)

## Surface Overview

The Owner surface (`app/owner/page.tsx`) provides a pet owner with a dashboard showing
their pet's profile, upcoming appointments, health timeline, and vaccination records.
All actions (Book Appointment, View Records, Emergency Access, Consent Settings) are
currently disabled buttons — their target contracts are mapped below.

## Component → API Contract Map

### PetProfileCard

| Field              | Source (placeholder)            | Live API Target                              | Service      |
|--------------------|---------------------------------|----------------------------------------------|--------------|
| Pet name           | `luna`                          | `GET /v1/owner/pets/{pet_id}`  → `name`      | owner-service |
| Species / breed    | `Arabian Mau`, `Cat`            | → `species`, `breed`                         | owner-service |
| Age / weight       | `3y`, `4.2 kg`                  | → `age_years`, `weight_kg`                   | owner-service |
| Microchip ID       | `985112345678901`               | → `microchip_id`                             | owner-service |
| Primary vet        | `Dr. Khalid Al-Otaibi`          | → `primary_vet.display_name`                 | owner-service |
| Next appointment   | Derived from appointments list  | `GET /v1/owner/appointments?limit=1&status=upcoming` | owner-service |

**Consent required:** No (owner viewing own pet profile)

---

### AppointmentCard

| Field              | Live API Target                                             | Service       |
|--------------------|-------------------------------------------------------------|---------------|
| Appointment list   | `GET /v1/owner/appointments?status=upcoming&limit=10`       | owner-service |
| Appointment detail | `GET /v1/owner/appointments/{appointment_id}`               | owner-service |
| Cancel appointment | `POST /v1/owner/appointments/{id}/cancel` (**disabled**)   | owner-service |

**Consent required:** No

---

### HealthTimeline

| Field              | Live API Target                                             | Service         | Consent Scope      |
|--------------------|-------------------------------------------------------------|-----------------|--------------------|
| Timeline events    | `GET /v1/owner/pets/{pet_id}/timeline`                      | clinical-service | `cs-health-read`  |

**Consent required:** `cs-health-read` must be `granted` before rendering.
If not granted → render `ConsentRequiredBanner` with scope label "Health Record Access".

---

### VaccinationCard / VaccinationSummary

| Field              | Live API Target                                             | Service         | Consent Scope      |
|--------------------|-------------------------------------------------------------|-----------------|--------------------|
| Vaccination list   | `GET /v1/owner/pets/{pet_id}/vaccinations`                  | clinical-service | `cs-health-read`  |
| Overdue / due-soon | Computed client-side from `due_date` vs today               | —               | —                  |

**Consent required:** `cs-health-read`

---

### QuickActions (all currently disabled)

| Button               | Target Endpoint                                                   | Service            | Consent Required |
|----------------------|-------------------------------------------------------------------|--------------------|------------------|
| Book Appointment     | `POST /v1/owner/appointments`                                     | owner-service      | No               |
| View Records         | Navigate → vet surface with owner consent pre-check              | consent_registry   | `cs-health-read` |
| Emergency Access     | `POST /v1/emergency/alerts` with `owner_id`, `pet_id`, complaint | emergency-service  | No               |
| Consent Settings     | `GET /v1/consent/{owner_id}` → render scope list                  | consent_registry   | No               |
|                      | `POST /v1/consent/{owner_id}/{scope_id}/grant`                    | consent_registry   | No               |
|                      | `POST /v1/consent/{owner_id}/{scope_id}/revoke`                   | consent_registry   | No               |

## Route Handler Proxy Paths (petcare-web)

| Component          | Proxy Route                                   | Upstream                                 |
|--------------------|-----------------------------------------------|------------------------------------------|
| Pet profile        | `GET /api/owner/pets/[petId]`                 | `GET /v1/owner/pets/{petId}`             |
| Appointments       | `GET /api/owner/appointments`                 | `GET /v1/owner/appointments`             |
| Timeline           | `GET /api/owner/pets/[petId]/timeline`        | `GET /v1/owner/pets/{petId}/timeline`    |
| Vaccinations       | `GET /api/owner/pets/[petId]/vaccinations`    | `GET /v1/owner/pets/{petId}/vaccinations`|
| Consent check      | `GET /api/consent/[ownerId]/[scopeId]`        | `GET /v1/consent/{ownerId}/{scopeId}`    |
