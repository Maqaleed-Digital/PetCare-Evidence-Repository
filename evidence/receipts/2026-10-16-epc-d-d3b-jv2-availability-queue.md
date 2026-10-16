# MVC-EPC-D-001 v1.5 — Lane D unit D3b: J-V2 availability and queue (CV-02, CV-03)

```
UNIT=D3b   AUTHORITY=R21.4 (D3 veterinarian journeys, ledger order), R18.4   BASE=origin/main 26b6edf
JOURNEY=J-V2 "availability, queue" (D0 inventory: missing/missing; no external dependency)   TAGS=[J-V2] @S:CV-02 @S:CV-03
```

## What is built
- `availability.py`: a veterinarian publishes a WEEKLY schedule — windows (weekday 0=Monday..6=Sunday, opens, closes) on the
  Asia/Riyadh clock, on the 30-minute grid, non-overlapping within a day. Insert-only and versioned: the latest plan is in force.
  A plan with no window offers no slots.
- `bookings.py`: slots and `is_bookable_instant` now take the veterinarian's windows. **Assumption recorded
  (D3B-DEFAULT-HOURS-FALLBACK):** a veterinarian who has NEVER published keeps the clinic default hours (D2E-DEFAULT-HOURS,
  09:00-17:00), so a clinic is bookable before its veterinarians publish; the bookings.py docstring said J-V2 "replaces" the
  defaults — it does, per veterinarian, once they publish. Existing bookings are never moved or cancelled by a new plan.
- Booking and rescheduling validate the slot against THAT veterinarian's schedule (reschedule: the booking's veterinarian).
- Migration **0065** (additive): `vet_availability_plan`, `vet_availability_window` (plan + windows in one transaction).
  `BookingRepository.list_for_veterinarian` (memory + PostgreSQL).
- Served routes: `PUT/GET /api/vet/availability` (veterinarian only; publish is audited), `GET /api/vet/queue` — the
  veterinarian's OWN upcoming BOOKED appointments (with pet, owner, reason, whether a CO-06 pre-visit intake was sent) and their
  consultations without an outcome. `served_routes.json` regenerated (+3); no FR state change.
- Web: `/vet/availability` (CV-02) and `/vet/queue` (CV-03), linked from `/vet`; `/vet` itself is unchanged in behaviour (its
  PORT-08 empty-queue surface tests are pinned and pass).

## Full-stack acceptance (each project separately, one worker, no concurrent backend run) — first run, no retries
| PROJECT | [J-V2] @S:CV-02 @S:CV-03 | J-O5 + CO-06 regression (slot logic changed) |
|---|---|---|
| en-desktop | PASS | PASS (2/2) |
| ar-desktop | PASS | PASS (2/2) |
| en-mobile | PASS | PASS (2/2) |
| ar-mobile | PASS | PASS (2/2) |

The spec: the seeded veterinarian signs in through /signin -> /vet -> availability: one working day, one project-specific hour,
published; the owner's slots for that day are exactly that hour's two slots; a 09:00 booking is refused; a booking inside is
accepted -> /vet/queue shows it with the pet and the owner's name; Arabic: no untranslated copy on both screens. Because the CI
run serves all four projects from one stack, the spec ends by republishing a full 09:00-17:00 week (the booking is unchanged).

## Evidence
| Check | Result |
|---|---|
| backend, CI command | **1325 passed, 0 failed** |
| D3b served API tests · PostgreSQL control | 10 passed · 1 passed, 0 skipped (added to the CI PostgreSQL list) |
| tsc · web vitest | clean · **49 files / 253 passed** (PORT-08 /vet surface and FR-09 language tests unchanged and passing) |
| perturbations (`perturb_epc_d_d3b_jv2.py`) | **13 ARMED / 0 VACUOUS** |
| migration invariants · register status | 14 passed |
| prohibited-literal / secret / evidence bundles | 0 / CLEAN / 32 bundles FAILED=0 |

## Counting
J-V2, CV-02 and CV-03 count when `report.mjs` reports them PASS in all four projects from the CI full-stack run of this PR's head;
matrices are taken from that run, not edited. No ledger X-row closes.
