# Vet Surface — petcare-web (PH-UI-3)

## Scope

The Vet portal (`/vet`) is a read-only shell placeholder delivered in PH-UI-1A
and frozen at PH-UI-3. Full vet workflow delivery is out of scope for the
current phase. The surface exists to satisfy navigation completeness.

## Planned Components (future phases)

| Component              | Purpose                                              |
|------------------------|------------------------------------------------------|
| `PatientQueue`         | Today's patient list with appointment status         |
| `MedicalRecordViewer`  | Read-only medical history per patient                |
| `PrescriptionSummary`  | Active and past prescriptions                        |
| `VaccinationWorksheet` | Vaccination due/administered checklist               |
| `ClinicalNotePanel`    | Free-text note entry (future — not in read-only shell) |
| `LabResultsViewer`     | Lab report attachments and values                    |

## Current State

- Route: `/vet` — static prerender, placeholder copy
- No data binding
- No mutations
- Navigation visible via `Sidebar`

## Constraints

- No backend mutation in any vet-facing surface.
- PDPL consent must be verified before any patient record is displayed.
- Clinical notes entry is a future interactive phase — not present in PH-UI shell.
