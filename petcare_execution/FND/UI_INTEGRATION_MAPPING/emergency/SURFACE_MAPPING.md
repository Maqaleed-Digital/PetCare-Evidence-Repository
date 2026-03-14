# Emergency Surface — UI Integration Mapping

## Phase

PH-FND-4 · Source UI: PH-UI-6 (`/emergency`)

## Surface Overview

The Emergency Coordination surface provides emergency responders with live alert queue,
triage board, clinic availability, pre-arrival packets, case timeline, handoff status,
and governance summary. All write operations (Acknowledge, Dispatch, Create Handoff) are
currently disabled. The P1 banner animates in the shell via Tailwind `animate-pulse`.

## Component → API Contract Map

### EmergencyKpiStrip

| KPI                  | Live API Target                                              | Service              |
|----------------------|--------------------------------------------------------------|----------------------|
| Active cases         | `GET /v1/emergency/summary`                                  | emergency-service    |
| P1 critical count    | → aggregated field                                           | emergency-service    |
| Avg response time    | → aggregated field                                           | emergency-service    |
| Clinics open         | `GET /v1/emergency/clinics/availability?count=true`          | emergency-service    |
| Handoffs today       | `GET /v1/emergency/handoffs?date={today}&count=true`         | emergency-service    |
| SLA compliance       | `GET /v1/emergency/governance/summary`                       | emergency-service    |

---

### EmergencyAlertsQueue

| Field              | Live API Target                                              | Service              |
|--------------------|--------------------------------------------------------------|----------------------|
| Alert list         | `GET /v1/emergency/alerts?status=open&sort=-severity`        | emergency-service    |
| Acknowledge alert  | `POST /v1/emergency/alerts/{id}/acknowledge` (**disabled**)  | emergency-service    |
| Dispatch alert     | `POST /v1/emergency/alerts/{id}/dispatch` (**disabled**)     | emergency-service    |

Alerts must be sorted P1→P4 on retrieval. `sort=-severity` maps to priority order.
Severity polling interval: **15 seconds** (critical for emergency surface).

---

### TriageEscalationSummary

| Field              | Live API Target                                              | Service              |
|--------------------|--------------------------------------------------------------|----------------------|
| Triage cases       | `GET /v1/emergency/triage-cases`                            | emergency-service    |
| Update triage case | `PATCH /v1/emergency/triage-cases/{id}` (**disabled**)      | emergency-service    |

Elapsed time column is computed client-side from `arrivalTime` vs `Date.now()`.

---

### ClinicAvailabilityBoard

| Field              | Live API Target                                              | Service              |
|--------------------|--------------------------------------------------------------|----------------------|
| Clinic availability| `GET /v1/emergency/clinics/availability`                    | emergency-service    |
| Update availability| `PATCH /v1/emergency/clinics/{id}/availability` (**disabled**) | emergency-service |

---

### PreArrivalPacketPanel

| Field              | Live API Target                                              | Service              | Consent Scope    |
|--------------------|--------------------------------------------------------------|----------------------|------------------|
| Packet for case    | `GET /v1/emergency/cases/{case_id}/pre-arrival-packet`      | emergency-service    | `cs-emergency`   |

**Consent required:** `cs-emergency` must be `granted` OR emergency auto-grant applies
(cs-emergency has 72h TTL from the alert raised timestamp per PURPOSE_LIMITATION_RULES.md).

**PDPL Note:** Pre-arrival packet contains PII (owner name, phone, allergies, vitals).
Route Handler must verify `cs-emergency` consent before returning packet. No PII cached
client-side beyond the active session.

---

### EmergencyTimeline

| Field              | Live API Target                                              | Service              |
|--------------------|--------------------------------------------------------------|----------------------|
| Timeline events    | `GET /v1/emergency/cases/{case_id}/timeline`                | emergency-service    |

---

### HandoffStatusPanel

| Field              | Live API Target                                              | Service              |
|--------------------|--------------------------------------------------------------|----------------------|
| Handoff records    | `GET /v1/emergency/handoffs`                                | emergency-service    |
| Create handoff     | `POST /v1/emergency/handoffs` (**disabled**)                | emergency-service    |

---

### EmergencyGovernanceSummary

| Field              | Live API Target                                              | Service              |
|--------------------|--------------------------------------------------------------|----------------------|
| Governance entries | `GET /v1/emergency/governance/summary`                      | emergency-service    |

---

## Route Handler Proxy Paths (petcare-web)

| Component               | Proxy Route                                    | Upstream                                              |
|-------------------------|------------------------------------------------|-------------------------------------------------------|
| Alert queue             | `GET /api/emergency/alerts`                    | `GET /v1/emergency/alerts`                            |
| Acknowledge alert       | `POST /api/emergency/alerts/[id]/acknowledge`  | `POST /v1/emergency/alerts/{id}/acknowledge`          |
| Dispatch alert          | `POST /api/emergency/alerts/[id]/dispatch`     | `POST /v1/emergency/alerts/{id}/dispatch`             |
| Triage cases            | `GET /api/emergency/triage`                    | `GET /v1/emergency/triage-cases`                      |
| Clinic availability     | `GET /api/emergency/clinics`                   | `GET /v1/emergency/clinics/availability`              |
| Pre-arrival packet      | `GET /api/emergency/cases/[caseId]/packet`     | `GET /v1/emergency/cases/{caseId}/pre-arrival-packet` |
| Case timeline           | `GET /api/emergency/cases/[caseId]/timeline`   | `GET /v1/emergency/cases/{caseId}/timeline`           |
| Handoffs                | `GET /api/emergency/handoffs`                  | `GET /v1/emergency/handoffs`                          |
| Governance summary      | `GET /api/emergency/governance`                | `GET /v1/emergency/governance/summary`                |
| Consent check           | `GET /api/consent/[ownerId]/cs-emergency`      | `GET /v1/consent/{ownerId}/cs-emergency`              |
