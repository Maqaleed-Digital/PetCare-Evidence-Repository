# Admin Surface — Deferred Runtime Gaps

## Phase

PH-FND-4 · Source UI: PH-UI-4

---

## Gap Registry

### GAP-ADM-01: admin-service not implemented

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                  |
| Affects      | AdminKpiStrip, AppointmentLoadBoard, VetAvailabilityPanel, AlertsEscalationsPanel, ClinicConfigurationSummary |
| Blocker      | `admin-service` not in PH-FND-2 scope                                    |
| Impact       | All admin KPI, appointment, vet, alert, and config data remain placeholder |
| Resolution   | Add admin-service to service registry in a future PH-FND iteration        |

---

### GAP-ADM-02: AuditEventViewer not wired to audit_ledger

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | AuditEventViewer component                                                |
| Blocker      | None — `audit_ledger` contract defined in PH-FND-3                       |
| Impact       | Audit events shown as placeholder; no real trail rendered                 |
| Resolution   | Create `/api/admin/audit` Route Handler proxying `GET /v1/audit/events`   |

---

### GAP-ADM-03: EvidenceExportPanel write operations disabled

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | EvidenceExportPanel — all 4 export type buttons                           |
| Blocker      | None — `evidence_export` contract fully defined in PH-FND-3              |
| Impact       | No export can be created or downloaded from the UI                       |
| Resolution   | Wire Route Handlers; enable buttons behind feature flag                  |

---

### GAP-ADM-04: Dual-approval flow not surfaced

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | EvidenceExportPanel — full_compliance and >12-month exports              |
| Blocker      | Requires second-admin approval UI (notification + approve button)        |
| Impact       | Dual-approval exports cannot be triggered even after backend is live     |
| Resolution   | Add pending-approval notification banner and second-admin approve action |

---

### GAP-ADM-05: PDPL compliance alert (critical) has no resolution path in UI

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | AlertsEscalationsPanel — `severity: critical` PDPL gap alert             |
| Blocker      | Alert acknowledgement write endpoint not yet wired                       |
| Impact       | PDPL gap alert shown as read-only; no dismiss or escalation action       |
| Resolution   | Enable alert acknowledge action when admin-service is live               |
