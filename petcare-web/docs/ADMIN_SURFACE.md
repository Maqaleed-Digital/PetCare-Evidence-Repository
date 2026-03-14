# Admin Surface — petcare-web (PH-UI-4)

## Scope

PH-UI-4 delivers the read-only Admin Clinic Control surface. All data is
placeholder/mock. No mutations. No real backend calls from this surface.

## Components

| Component                   | File                                              | Purpose                                             |
|-----------------------------|---------------------------------------------------|-----------------------------------------------------|
| `AdminKpiStrip`             | `components/admin/AdminKpiStrip.tsx`              | Row of KPI cards (patients, appointments, vets, alerts) |
| `ClinicOperationsOverview`  | `components/admin/ClinicOperationsOverview.tsx`   | Capacity + appointment completion with progress bars |
| `AppointmentLoadBoard`      | `components/admin/AppointmentLoadBoard.tsx`       | Today's appointment schedule table with status       |
| `VetAvailabilityPanel`      | `components/admin/VetAvailabilityPanel.tsx`       | Live-status list of vets (available/busy/break/off)  |
| `AlertsEscalationsPanel`    | `components/admin/AlertsEscalationsPanel.tsx`     | Severity-sorted alerts (critical/warning/info)       |
| `AuditEventViewer`          | `components/admin/AuditEventViewer.tsx`           | Append-only audit log table                          |
| `EvidenceExportPanel`       | `components/admin/EvidenceExportPanel.tsx`        | Export option grid (all disabled — read-only shell)  |
| `ClinicConfigurationSummary`| `components/admin/ClinicConfigurationSummary.tsx` | Clinic config key-value table (locked fields shown)  |

## Types (`types/admin.ts`)

- `AdminKpi` — label, value, unit, trend, variant
- `ClinicOperations` — name, status, capacity used/total, appointments
- `AppointmentSlot` — time, patient, pet, vet, reason, status
- `VetAvailability` — name, specialisation, status, current patient, remaining
- `Alert` — severity (`info`/`warning`/`critical`), category, raised at, acknowledged
- `AuditEvent` — actor, role, action, resource, outcome, timestamp
- `ExportOption` — label, format (`json`/`csv`/`pdf`), scope
- `ClinicConfiguration` — clinic ID, timezone, retention, PDPL version, entries

## Constraints

- No backend mutation — all `EvidenceExportPanel` buttons are `disabled`.
- No real API calls from the admin page — data passed as mock constants.
- Audit log is append-only display only; no delete/patch controls rendered.
- PDPL: no PII transmitted; all data is mock.
