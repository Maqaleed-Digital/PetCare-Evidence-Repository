# Emergency Surface — Deferred Runtime Gaps

## Phase

PH-FND-4 · Source UI: PH-UI-6

---

## Gap Registry

### GAP-EMG-01: emergency-service not implemented

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                  |
| Affects      | All emergency components                                                   |
| Blocker      | `emergency-service` not in PH-FND-2 scope                                |
| Impact       | All emergency data remains placeholder (alerts, triage, clinics, handoffs)|
| Resolution   | Add emergency-service to service registry in a future PH-FND iteration    |

---

### GAP-EMG-02: Real-time alert polling not implemented

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | EmergencyAlertsQueue — 15s polling requirement                            |
| Blocker      | Polling interval not wired in current shell; emergency-service not live   |
| Impact       | Alert queue is static placeholder; new P1 alerts not surfaced             |
| Resolution   | Add 15s polling via `useEffect` + `setInterval` in `EmergencyAlertsQueue`|

---

### GAP-EMG-03: Alert acknowledge and dispatch disabled

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | EmergencyAlertsQueue — Acknowledge, Dispatch buttons                     |
| Blocker      | emergency-service acknowledge/dispatch endpoints not defined              |
| Impact       | Emergency responders cannot act on alerts from the UI                    |
| Resolution   | Enable when emergency-service is live; SLA compliance requires < 2min ACK |

---

### GAP-EMG-04: Pre-arrival packet consent gate not enforced

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | PreArrivalPacketPanel — PII display                                       |
| Blocker      | None — `consent_registry` and `cs-emergency` scope defined               |
| Impact       | PII rendered without consent gate in placeholder shell (no real data)    |
| Resolution   | Add consent pre-check in `/api/emergency/cases/[caseId]/packet` Route Handler; enforce cs-emergency grant or 72h auto-window |

---

### GAP-EMG-05: Handoff creation disabled

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | HandoffStatusPanel — "Create Handoff" action                              |
| Blocker      | emergency-service handoff creation endpoint not defined                   |
| Impact       | Inter-clinic transfers cannot be initiated from UI                       |
| Resolution   | Enable when emergency-service handoff API is live                        |

---

### GAP-EMG-06: SLA governance summary is static

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | EmergencyGovernanceSummary — 7 governance entries                        |
| Blocker      | Real SLA data requires live alert timestamps; emergency-service not live |
| Impact       | Governance entries (83% SLA, 2 failures) are hard-coded placeholder     |
| Resolution   | Wire `GET /v1/emergency/governance/summary` when emergency-service live  |

---

### GAP-EMG-07: WebSocket / SSE for live triage updates

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | TriageEscalationSummary, EmergencyAlertsQueue                            |
| Blocker      | WebSocket / SSE infrastructure out of scope for current phase            |
| Impact       | Triage and alert state updates require full page refresh                 |
| Resolution   | Add WebSocket or SSE in a future phase; polling is acceptable short-term |
