# Pharmacy Surface — Deferred Runtime Gaps

## Phase

PH-FND-4 · Source UI: PH-UI-5

---

## Gap Registry

### GAP-PHR-01: pharmacy-service not implemented

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                  |
| Affects      | All pharmacy components                                                    |
| Blocker      | `pharmacy-service` not in PH-FND-2 scope                                 |
| Impact       | All pharmacy data remains placeholder (prescriptions, inventory, recalls, cold chain) |
| Resolution   | Add pharmacy-service to service registry in a future PH-FND iteration     |

---

### GAP-PHR-02: Consent check not enforced for prescription data

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | PrescriptionQueue                                                          |
| Blocker      | None — `consent_registry` contract defined; `cs-pharmacy` scope defined  |
| Impact       | Prescription data rendered without consent gate (placeholder only)       |
| Resolution   | Add consent pre-check in `/api/pharmacy/prescriptions` Route Handler     |

---

### GAP-PHR-03: Cold chain real-time polling not implemented

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | ColdChainMonitor                                                           |
| Blocker      | Server-sent events or polling not in scope for PH-UI-5 shell             |
| Impact       | Cold chain data is static placeholder; sensor warnings not live          |
| Resolution   | Add 60s polling in ColdChainMonitor using `useEffect` + `setInterval`    |

---

### GAP-PHR-04: Dispense workflow step tracking not wired

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | DispenseWorkflowPreview — 6-step workflow                                 |
| Blocker      | pharmacy-service not implemented; dispense workflow endpoint not defined  |
| Impact       | Workflow steps shown as static list; no step completion tracking         |
| Resolution   | Define dispense workflow API in pharmacy-service; wire to UI             |

---

### GAP-PHR-05: Class II recall acknowledgement disabled

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `DEFERRED`                                                                 |
| Affects      | RecallExceptionsPanel — "Acknowledge" button                              |
| Blocker      | pharmacy-service not implemented                                          |
| Impact       | Recall acknowledgement cannot be recorded from UI                        |
| Resolution   | Enable when pharmacy-service recall endpoint is live                     |

---

### GAP-PHR-06: Medication interaction check not implemented

| Field        | Value                                                                      |
|--------------|----------------------------------------------------------------------------|
| Status       | `BLOCKED`                                                                  |
| Affects      | MedicationSafetyPanel — interaction check capability                     |
| Blocker      | Interaction check requires drug database not yet in scope                |
| Impact       | Interactions shown as static placeholder (cyclosporine + NSAIDs example) |
| Resolution   | Integrate drug interaction database in a future phase                    |
