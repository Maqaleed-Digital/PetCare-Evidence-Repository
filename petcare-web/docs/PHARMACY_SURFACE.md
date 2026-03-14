# Pharmacy Surface — petcare-web (PH-UI-5)

## Scope

PH-UI-5 delivers the read-only Pharmacy Operations surface. All data is
placeholder/mock. No mutations. No real backend calls.

## Route

`/pharmacy` — static prerender, server component, mock data passed as constants.

## Components

| Component                  | File                                               | Purpose                                              |
|----------------------------|----------------------------------------------------|------------------------------------------------------|
| `PharmacyKpiStrip`         | `components/pharmacy/PharmacyKpiStrip.tsx`         | KPI strip (prescriptions, dispenses, alerts, recalls)|
| `PrescriptionQueue`        | `components/pharmacy/PrescriptionQueue.tsx`        | Active prescription list with status and urgency     |
| `DispenseWorkflowPreview`  | `components/pharmacy/DispenseWorkflowPreview.tsx`  | Step-by-step dispense workflow for one prescription  |
| `InventoryStatusSummary`   | `components/pharmacy/InventoryStatusSummary.tsx`   | Medication inventory table sorted by criticality     |
| `MedicationSafetyPanel`    | `components/pharmacy/MedicationSafetyPanel.tsx`    | Drug interaction / contraindication alerts           |
| `ColdChainMonitor`         | `components/pharmacy/ColdChainMonitor.tsx`         | Temperature sensor cards with visual bar             |
| `RecallExceptionsPanel`    | `components/pharmacy/RecallExceptionsPanel.tsx`    | Active product recalls with severity and batch info  |
| `FulfillmentDispatchSummary`| `components/pharmacy/FulfillmentDispatchSummary.tsx`| Dispatch/delivery tracking table                   |

## Types (`types/pharmacy.ts`)

- `PharmacyKpi` — label, value, unit, variant, sub
- `Prescription` / `PrescriptionItem` / `PrescriptionStatus`
- `DispenseStep` / `DispenseStepStatus`
- `InventoryItem` / `InventoryStatus`
- `MedicationSafetyAlert` / `SafetyAlertLevel`
- `ColdChainReading` / `ColdChainStatus`
- `RecallException` / `RecallSeverity` / `RecallStatus`
- `FulfillmentDispatch` / `DispatchStatus`

## Cold Chain Target Ranges

| Storage Requirement | Target Range |
|---------------------|-------------|
| Ambient             | 15–25°C     |
| Refrigerated        | 2–8°C       |
| Frozen              | −20–−10°C   |

## Recall Severity Classification

| Class     | Meaning                                      |
|-----------|----------------------------------------------|
| Class I   | Serious adverse health risk or death         |
| Class II  | Temporary/reversible adverse health effect   |
| Class III | Unlikely to cause adverse health effect      |

## Constraints

- No backend mutations — all actions are display-only.
- No dispensing actions are interactive in PH-UI-5.
- PDPL: all data is mock; no PII transmitted.
- Cold chain sensor readings are static mock — no WebSocket/polling in this phase.
