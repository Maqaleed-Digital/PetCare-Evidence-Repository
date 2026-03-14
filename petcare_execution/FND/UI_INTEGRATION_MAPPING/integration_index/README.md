# UI Integration Mapping — Integration Index

## Purpose

This directory is the canonical index of all UI-to-backend integration contracts for the
petcare-web frontend (PH-UI-1A through PH-UI-6). It provides a single lookup point for
which UI surface maps to which backend service and API contract.

## Phase

PH-FND-4 — UI Integration Contract Mapping

## Directory Structure

```
FND/UI_INTEGRATION_MAPPING/
├── shared/
│   ├── UI_INTEGRATION_PRINCIPLES.md    # 7 governing principles
│   ├── READ_WRITE_BOUNDARIES.md        # All read/write targets across surfaces
│   └── ERROR_RENDERING_MATRIX.md       # HTTP error → UI state map
├── owner/
│   ├── SURFACE_MAPPING.md              # Component → API mapping (PH-UI-2)
│   ├── CONTRACT_TOUCHPOINTS.json       # Machine-readable touchpoints
│   └── DEFERRED_RUNTIME_GAPS.md        # 5 gaps
├── vet/
│   ├── SURFACE_MAPPING.md              # Intended mapping (PH-UI-3 not yet built)
│   ├── CONTRACT_TOUCHPOINTS.json       # Machine-readable touchpoints
│   └── DEFERRED_RUNTIME_GAPS.md        # 5 gaps
├── admin/
│   ├── SURFACE_MAPPING.md              # Component → API mapping (PH-UI-4)
│   ├── CONTRACT_TOUCHPOINTS.json       # Machine-readable touchpoints
│   └── DEFERRED_RUNTIME_GAPS.md        # 5 gaps
├── pharmacy/
│   ├── SURFACE_MAPPING.md              # Component → API mapping (PH-UI-5)
│   ├── CONTRACT_TOUCHPOINTS.json       # Machine-readable touchpoints
│   └── DEFERRED_RUNTIME_GAPS.md        # 6 gaps
├── emergency/
│   ├── SURFACE_MAPPING.md              # Component → API mapping (PH-UI-6)
│   ├── CONTRACT_TOUCHPOINTS.json       # Machine-readable touchpoints
│   └── DEFERRED_RUNTIME_GAPS.md        # 7 gaps
└── integration_index/
    ├── README.md                        # This file
    └── UI_CONTRACT_REGISTRY.json        # Machine-readable surface registry
```

## Gap Summary

| Surface   | Total Gaps | BLOCKED | DEFERRED | WIRED |
|-----------|-----------|---------|----------|-------|
| owner     | 5         | 2       | 3        | 0     |
| vet       | 5         | 2       | 3        | 0     |
| admin     | 5         | 1       | 4        | 0     |
| pharmacy  | 6         | 2       | 4        | 0     |
| emergency | 7         | 1       | 6        | 0     |
| **total** | **28**    | **8**   | **20**   | **0** |

## Services Required (not yet in scope)

| Service            | Required by                            |
|--------------------|----------------------------------------|
| `owner-service`    | owner surface (PetProfileCard, AppointmentCard) |
| `vet-service`      | vet surface (VetPatientList, AppointmentSchedule) |
| `admin-service`    | admin surface (KPIs, appointments, vets, alerts, config) |
| `pharmacy-service` | pharmacy surface (all components)      |
| `emergency-service`| emergency surface (all components)     |

## Services Ready to Wire (from PH-FND-2/3)

| Service             | Ready Contracts                                    |
|---------------------|----------------------------------------------------|
| `audit_ledger`      | Admin AuditEventViewer                             |
| `consent_registry`  | All consent-gated components (when proxy created)  |
| `clinical_signoff`  | Vet SignoffQueue / SignoffApproveReject             |
| `evidence_export`   | Admin EvidenceExportPanel                          |
