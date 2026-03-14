# Admin Surface — UI Integration Mapping

## Phase

PH-FND-4 · Source UI: PH-UI-4 (`/admin`)

## Surface Overview

The Admin surface provides clinic administrators with KPIs, appointment load, vet availability,
alerts, audit event viewer, evidence export panel, and clinic configuration. All write
operations are currently disabled buttons.

## Component → API Contract Map

### AdminKpiStrip

| KPI                    | Live API Target                              | Service        |
|------------------------|----------------------------------------------|----------------|
| Total appointments     | `GET /v1/admin/kpis`                         | admin-service  |
| Active vets            | → aggregated field                           | admin-service  |
| Pending prescriptions  | `GET /v1/pharmacy/prescriptions?status=pending&count=true` | pharmacy-service |
| Open alerts            | `GET /v1/admin/alerts?status=open&count=true`| admin-service  |
| PDPL compliance rate   | `GET /v1/admin/governance/summary`           | admin-service  |
| System health          | `GET /api/proxy/health`                      | petcare-web proxy (wired) |

---

### ClinicOperationsOverview / AppointmentLoadBoard

| Field              | Live API Target                                               | Service        |
|--------------------|---------------------------------------------------------------|----------------|
| Appointment slots  | `GET /v1/admin/appointments?date={date}&limit=50`            | admin-service  |
| Slot status        | → `status` field per slot                                    | admin-service  |

---

### VetAvailabilityPanel

| Field              | Live API Target                                               | Service        |
|--------------------|---------------------------------------------------------------|----------------|
| Vet list + status  | `GET /v1/admin/vets/availability`                            | admin-service  |
| Update availability| `PATCH /v1/admin/vets/{vet_id}/availability` (**disabled**)  | admin-service  |

---

### AlertsEscalationsPanel

| Field              | Live API Target                                               | Service        |
|--------------------|---------------------------------------------------------------|----------------|
| Alert list         | `GET /v1/admin/alerts?status=open`                           | admin-service  |
| Alert detail       | `GET /v1/admin/alerts/{alert_id}`                            | admin-service  |

---

### AuditEventViewer

| Field              | Live API Target                                               | Service        | Auth         |
|--------------------|---------------------------------------------------------------|----------------|--------------|
| Audit events       | `GET /v1/audit/events?clinic_id={id}`                        | audit_ledger   | `admin` role |
| Filter by type     | `?filter[event_type][in]=consent_granted,access_denied`       | audit_ledger   | `admin` role |
| Cursor pagination  | `?cursor={token}&limit=50`                                   | audit_ledger   | `admin` role |

**Identity check:** `identity_rbac.can(admin, "read", "audit_log")` → ALLOW required.
**Consent:** `cs-audit-admin` is default `granted` per CONSENT_SCOPE_MAP.json.

---

### EvidenceExportPanel (all disabled in shell)

| Action                  | Live API Target                                      | Service          | Guard                  |
|-------------------------|------------------------------------------------------|------------------|------------------------|
| Create audit_log export | `POST /v1/export/requests` `export_type: audit_log`  | evidence_export  | admin + cs-evidence-export |
| Create full_compliance  | `POST /v1/export/requests` `export_type: full_compliance` | evidence_export | dual-approval required |
| List past exports       | `GET /v1/export/requests`                            | evidence_export  | admin                  |
| Download export         | `GET /v1/export/requests/{id}/download`              | evidence_export  | admin + ≤3 downloads   |

---

### ClinicConfigurationSummary

| Field              | Live API Target                                               | Service        |
|--------------------|---------------------------------------------------------------|----------------|
| Clinic config      | `GET /v1/admin/clinic/configuration`                         | admin-service  |
| Update config      | `PATCH /v1/admin/clinic/configuration` (**disabled**)        | admin-service  |

---

## Route Handler Proxy Paths (petcare-web)

| Component            | Proxy Route                             | Upstream                                      |
|----------------------|-----------------------------------------|-----------------------------------------------|
| KPIs                 | `GET /api/admin/kpis`                   | `GET /v1/admin/kpis`                          |
| Appointments         | `GET /api/admin/appointments`           | `GET /v1/admin/appointments`                  |
| Vet availability     | `GET /api/admin/vets/availability`      | `GET /v1/admin/vets/availability`             |
| Alerts               | `GET /api/admin/alerts`                 | `GET /v1/admin/alerts`                        |
| Audit events         | `GET /api/admin/audit`                  | `GET /v1/audit/events`                        |
| Export requests      | `POST /api/admin/export`                | `POST /v1/export/requests`                    |
| Export list          | `GET /api/admin/export`                 | `GET /v1/export/requests`                     |
| Export download      | `GET /api/admin/export/[exportId]/dl`   | `GET /v1/export/requests/{exportId}/download` |
| Clinic config        | `GET /api/admin/clinic/config`          | `GET /v1/admin/clinic/configuration`          |
