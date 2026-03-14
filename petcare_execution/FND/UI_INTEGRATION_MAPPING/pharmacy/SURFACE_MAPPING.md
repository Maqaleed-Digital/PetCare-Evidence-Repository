# Pharmacy Surface — UI Integration Mapping

## Phase

PH-FND-4 · Source UI: PH-UI-5 (`/pharmacy`)

## Surface Overview

The Pharmacy surface provides pharmacy staff with prescription management, dispense workflow,
inventory status, medication safety alerts, cold chain monitoring, recall exceptions, and
fulfilment dispatch. All write operations (Dispense, Acknowledge Recall) are currently disabled.

## Component → API Contract Map

### PharmacyKpiStrip

| KPI                     | Live API Target                                          | Service            |
|-------------------------|----------------------------------------------------------|--------------------|
| Prescriptions pending   | `GET /v1/pharmacy/prescriptions?status=pending&count=true` | pharmacy-service |
| Active safety alerts    | `GET /v1/pharmacy/safety-alerts?status=active&count=true`  | pharmacy-service |
| Items out of stock      | `GET /v1/pharmacy/inventory?status=out_of_stock&count=true`| pharmacy-service |
| Cold chain warnings     | `GET /v1/pharmacy/cold-chain/readings?status=warning&count=true` | pharmacy-service |
| Recalls active          | `GET /v1/pharmacy/recalls?status=active&count=true`      | pharmacy-service |
| Dispatches today        | `GET /v1/pharmacy/dispatches?date={today}&count=true`    | pharmacy-service |

---

### PrescriptionQueue

| Field                | Live API Target                                            | Service            | Consent Scope   |
|----------------------|------------------------------------------------------------|--------------------|-----------------|
| Prescription list    | `GET /v1/pharmacy/prescriptions?status=pending`           | pharmacy-service   | `cs-pharmacy`   |
| Prescription detail  | `GET /v1/pharmacy/prescriptions/{id}`                     | pharmacy-service   | `cs-pharmacy`   |
| Mark as dispensed    | `POST /v1/pharmacy/prescriptions/{id}/dispense` (**disabled**) | pharmacy-service | `cs-pharmacy` |

**Consent required:** `cs-pharmacy` must be `granted`. Route Handler checks consent per
owner before fetching prescription data.

---

### DispenseWorkflowPreview

| Field                | Live API Target                                            | Service            |
|----------------------|------------------------------------------------------------|---------------------|
| Dispense steps       | `GET /v1/pharmacy/prescriptions/{id}/dispense-workflow`   | pharmacy-service    |
| Record step complete | `PATCH /v1/pharmacy/dispense/{workflow_id}/steps/{step}` (**disabled**) | pharmacy-service |

---

### InventoryStatusSummary

| Field                | Live API Target                                            | Service            |
|----------------------|------------------------------------------------------------|---------------------|
| Inventory items      | `GET /v1/pharmacy/inventory?limit=50`                     | pharmacy-service    |
| Update stock level   | `PATCH /v1/pharmacy/inventory/{item_id}` (**disabled**)   | pharmacy-service    |

---

### MedicationSafetyPanel

| Field                | Live API Target                                            | Service            |
|----------------------|------------------------------------------------------------|---------------------|
| Safety alerts        | `GET /v1/pharmacy/safety-alerts?status=active`            | pharmacy-service    |
| Interaction check    | `POST /v1/pharmacy/interactions/check` (**disabled**)     | pharmacy-service    |

---

### ColdChainMonitor

| Field                | Live API Target                                            | Service            |
|----------------------|------------------------------------------------------------|---------------------|
| Sensor readings      | `GET /v1/pharmacy/cold-chain/readings`                    | pharmacy-service    |
| Reading history      | `GET /v1/pharmacy/cold-chain/readings?sensor_id={id}&limit=100` | pharmacy-service |

**Note:** Cold chain data is polled every 60 seconds in production. Current shell renders
placeholder readings — a `ColdChainMonitor` specific override in `ERROR_RENDERING_MATRIX.md`
handles sensor unavailability.

---

### RecallExceptionsPanel

| Field                | Live API Target                                            | Service            |
|----------------------|------------------------------------------------------------|---------------------|
| Active recalls       | `GET /v1/pharmacy/recalls?status=active`                  | pharmacy-service    |
| Acknowledge recall   | `POST /v1/pharmacy/recalls/{id}/acknowledge` (**disabled**)| pharmacy-service  |

---

### FulfillmentDispatchSummary

| Field                | Live API Target                                            | Service            |
|----------------------|------------------------------------------------------------|---------------------|
| Dispatch records     | `GET /v1/pharmacy/dispatches?date={today}`                | pharmacy-service    |

---

## Route Handler Proxy Paths (petcare-web)

| Component               | Proxy Route                                    | Upstream                                         |
|-------------------------|------------------------------------------------|--------------------------------------------------|
| Prescription queue      | `GET /api/pharmacy/prescriptions`              | `GET /v1/pharmacy/prescriptions`                 |
| Inventory               | `GET /api/pharmacy/inventory`                  | `GET /v1/pharmacy/inventory`                     |
| Safety alerts           | `GET /api/pharmacy/safety-alerts`              | `GET /v1/pharmacy/safety-alerts`                 |
| Cold chain readings     | `GET /api/pharmacy/cold-chain`                 | `GET /v1/pharmacy/cold-chain/readings`           |
| Recalls                 | `GET /api/pharmacy/recalls`                    | `GET /v1/pharmacy/recalls`                       |
| Dispatches              | `GET /api/pharmacy/dispatches`                 | `GET /v1/pharmacy/dispatches`                    |
| Consent pre-check       | `GET /api/consent/[ownerId]/cs-pharmacy`       | `GET /v1/consent/{ownerId}/cs-pharmacy`          |
