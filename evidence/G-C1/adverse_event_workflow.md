# G-C1 — Adverse Event Workflow

## Model: `AdverseEvent` (models.py → `adverse_events` table)

| Field | Type | Notes |
|-------|------|-------|
| id | Integer PK | Auto-increment |
| consultation_id | Integer FK (nullable) | Links to consultations |
| reported_by | String | PilotUser.id of reporter |
| event_type | String | e.g. "medication_reaction", "procedure_complication" |
| description | Text | Free text |
| severity | String | e.g. "mild", "moderate", "severe" |
| status | String | open → investigating → resolved |
| created_at | DateTime(UTC) | Immutable on creation |
| resolved_at | DateTime(UTC, nullable) | Set when status=resolved |

## Status Lifecycle

```
open  ──→  investigating  ──→  resolved
  └──────────────────────────────────→
```

- `open`: newly reported, awaiting triage
- `investigating`: under review by clinical team
- `resolved`: root cause identified, corrective action taken

## Endpoints

| Method | Route | Role | Action |
|--------|-------|------|--------|
| POST | `/api/adverse-events` | vet, clinic_admin, platform_admin | Create event |
| PATCH | `/api/adverse-events/{id}/status` | platform_admin only | Update status |

## Audit events emitted

- `adverse_event.reported` — on creation
- `adverse_event.status_updated` — on status change

## File: `app/backend/routes/adverse_event_routes.py`
