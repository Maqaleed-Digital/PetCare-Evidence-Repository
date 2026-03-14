# UI Integration Mapping — Read/Write Boundaries

## Phase

PH-FND-4 · All petcare-web surfaces (PH-UI-1A through PH-UI-6)

## Summary

In the current phase (PH-UI shell), every write action is **disabled** at the UI layer.
This document specifies the boundary between what is currently read (rendered from
placeholder data), what will be read from live API, and what write operations are
deferred to future phases.

---

## Read Boundaries (Current Shell → Live API Target)

| Surface    | Component                    | Data Rendered          | Target API Endpoint                              | Status     |
|------------|------------------------------|------------------------|--------------------------------------------------|------------|
| Home       | `ApiHealthIndicator`         | Health/ready status    | `GET /api/proxy/health`, `GET /api/proxy/ready`  | Wired (proxy) |
| Owner      | `PetProfileCard`             | Pet profile            | `GET /v1/owner/pets/{pet_id}`                    | Deferred   |
| Owner      | `AppointmentCard`            | Upcoming appointments  | `GET /v1/owner/appointments?status=upcoming`     | Deferred   |
| Owner      | `HealthTimeline`             | Health events          | `GET /v1/owner/pets/{pet_id}/timeline`           | Deferred   |
| Owner      | `VaccinationCard`            | Vaccination records    | `GET /v1/owner/pets/{pet_id}/vaccinations`       | Deferred   |
| Vet        | Pet records panel            | Assigned pet records   | `GET /v1/signoff/records?pet_id={id}`            | Deferred   |
| Admin      | `AdminKpiStrip`              | Clinic KPIs            | `GET /v1/admin/kpis`                             | Deferred   |
| Admin      | `AuditEventViewer`           | Audit log              | `GET /v1/audit/events?clinic_id={id}`            | Deferred   |
| Admin      | `ClinicOperationsOverview`   | Appointment load       | `GET /v1/admin/clinic/operations`                | Deferred   |
| Admin      | `VetAvailabilityPanel`       | Vet schedule           | `GET /v1/admin/vets/availability`                | Deferred   |
| Admin      | `AlertsEscalationsPanel`     | Active alerts          | `GET /v1/admin/alerts`                           | Deferred   |
| Pharmacy   | `PrescriptionQueue`          | Prescription queue     | `GET /v1/pharmacy/prescriptions?status=pending`  | Deferred   |
| Pharmacy   | `InventoryStatusSummary`     | Inventory levels       | `GET /v1/pharmacy/inventory`                     | Deferred   |
| Pharmacy   | `ColdChainMonitor`           | Sensor readings        | `GET /v1/pharmacy/cold-chain/readings`           | Deferred   |
| Pharmacy   | `RecallExceptionsPanel`      | Active recalls         | `GET /v1/pharmacy/recalls?status=active`         | Deferred   |
| Emergency  | `EmergencyAlertsQueue`       | Live alert queue       | `GET /v1/emergency/alerts?status=open`           | Deferred   |
| Emergency  | `TriageEscalationSummary`    | Triage board           | `GET /v1/emergency/triage-cases`                 | Deferred   |
| Emergency  | `ClinicAvailabilityBoard`    | Clinic capacity        | `GET /v1/emergency/clinics/availability`         | Deferred   |
| Emergency  | `HandoffStatusPanel`         | Transfer status        | `GET /v1/emergency/handoffs`                     | Deferred   |

---

## Write Boundaries (Disabled in Current Phase → Future Activation)

| Surface    | UI Element                   | Action             | Target API Endpoint                                        |
|------------|------------------------------|--------------------|------------------------------------------------------------|
| Owner      | "Book Appointment" button    | Create appointment | `POST /v1/owner/appointments`                              |
| Owner      | "View Records" link          | Navigate to records| Route to vet surface with consent check                    |
| Owner      | "Emergency Access" button    | Raise emergency    | `POST /v1/emergency/alerts`                                |
| Owner      | "Consent Settings" button    | Manage consent     | `POST /v1/consent/{owner_id}/{scope_id}/grant` or `/revoke`|
| Vet        | Signoff "Approve" button     | Approve record     | `POST /v1/signoff/records/{id}/approve`                    |
| Vet        | Signoff "Reject" button      | Reject with reason | `POST /v1/signoff/records/{id}/reject`                     |
| Admin      | "Export Evidence" button     | Create export      | `POST /v1/export/requests`                                 |
| Admin      | "Assign Vet" control         | Update availability| `PATCH /v1/admin/vets/{vet_id}/availability`               |
| Pharmacy   | "Dispense" button            | Record dispense    | `POST /v1/pharmacy/prescriptions/{id}/dispense`            |
| Pharmacy   | "Acknowledge Recall" button  | Acknowledge recall | `POST /v1/pharmacy/recalls/{id}/acknowledge`               |
| Emergency  | "Acknowledge Alert" button   | Acknowledge alert  | `POST /v1/emergency/alerts/{id}/acknowledge`               |
| Emergency  | "Dispatch" button            | Dispatch responder | `POST /v1/emergency/alerts/{id}/dispatch`                  |
| Emergency  | "Create Handoff" button      | Initiate handoff   | `POST /v1/emergency/handoffs`                              |
