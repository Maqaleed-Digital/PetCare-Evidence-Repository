# MVC-EPC-D-001 v1.5 — Lane D unit D2q: CO-10 visit summary and care plan

```
UNIT=D2q   AUTHORITY=R21.4 (remaining owner screens, ledger order), R18.4   BASE=origin/main d729fc3
SCREEN=CO-10 "Visit summary and care plan" (no journey links CO-10 — tagged @S:CO-10 only)
```

## What is assembled, and what is deliberately not
The owner's summary of ONE completed consultation is built only from records the platform already holds FOR THAT consultation:
the consultation (date, mode, veterinarian, pet), the FR-06 outcome its veterinarian recorded, and the FR-14 prescriptions whose
`session_id` is this consultation AND whose pet is this consultation's pet (the session link on a prescription is not validated
at issue, so the pet is checked too). Medical records and care-due items carry no consultation link and are NOT attached to a
visit by time window or guesswork.

## What is built
- `care_plan.py`: the **care plan** — one per consultation, insert-only: home-care instructions (1..2000) and an optional follow-up
  date (not before the recording date on the Asia/Riyadh calendar). `visit_summary()` assembles the owner view.
- Migration **0063** (additive): `consultation_care_plan` (PRIMARY KEY session_id -> consultation). PG repository; harness deletes it
  before `consultation`.
- Served routes: `POST /api/consultations/{id}/care-plan` — only the consultation's veterinarian with live practitioner authority,
  only after the outcome (409 VISIT_NOT_COMPLETED), once (409 CARE_PLAN_ALREADY_RECORDED); `GET /api/owner/consultations/{id}/summary`
  — the owner's own consultation only (another owner/tenant 404; staff 403), 409 until completed. Both audited.
  `served_routes.json` regenerated (+2); no FR state change.
- Web: `/owner/consultations/[sessionId]/summary` (ar/en) — outcome as written, this visit's prescriptions, care plan and follow-up;
  states when there is no care plan or prescription; linked from each COMPLETED consultation (`consultation-open-summary`).

## Finding (recorded, not changed here)
CONSULT-READ-NOT-PARTICIPANT-SCOPED: the existing `GET /api/consultations/{session_id}` (FR-06) checks only the tenant, not that the
caller is a participant, so any role of the clinic can read any consultation of the clinic. The new owner summary route is
participant-scoped; the FR-06 route is unchanged (its scope is a Sponsor/ledger decision, not part of this screen).

## Full-stack acceptance (each project separately, one worker, no concurrent backend run) — first run, no retries
| PROJECT | CO-10 `@S:CO-10` | J-O6 chat regression (consultations list changed) |
|---|---|---|
| en-desktop | PASS | PASS |
| ar-desktop | PASS | PASS |
| en-mobile | PASS | PASS |
| ar-mobile | PASS | PASS |

The spec: the seeded veterinarian starts two consultations, completes one (outcome), prescribes under it (SQ-3 step-up) and records
the care plan (a care plan on the open one is 409); owner home -> my consultations -> only the completed one offers a summary ->
outcome, veterinarian, the one prescription with its dosing, instructions and follow-up date; the open visit shows "not completed";
an unknown visit is 404; Arabic: `dir=rtl`, no untranslated copy.

## Evidence
| Check | Result |
|---|---|
| backend, CI command | **1313 passed, 0 failed** |
| D2q served API tests · PostgreSQL control | 6 passed · 1 passed, 0 skipped (added to the CI PostgreSQL list) |
| tsc · web vitest | clean · **48 files / 249 passed** (J-O6 consultations page tests unchanged and passing) |
| perturbations (`perturb_epc_d_d2q_co10.py`) | **12 ARMED / 0 VACUOUS** |
| migration invariants · register status | 14 passed |
| prohibited-literal / secret / evidence bundles | 0 / CLEAN / 32 bundles FAILED=0 |

## Counting
CO-10 counts when `report.mjs` reports it PASS in all four projects from the CI full-stack run of this PR's head; matrices are taken
from that run, not edited. No journey is tagged. No ledger X-row closes.
