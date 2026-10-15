# MVC-EPC-D-001 v1.5 — Lane D unit D2p: CO-06 pre-visit intake with photos

```
UNIT=D2p   AUTHORITY=R21.4 (remaining owner screens, ledger order), R18.4   BASE=origin/main 51fcccd
SCREEN=CO-06 "Pre-visit intake with photos" (no journey links CO-06 — tagged @S:CO-06 only)
```

## What is built
- `previsit_intake.py`: one intake per consultation booking, insert-only — reason (1..500), symptoms since (not after submission),
  eating normally (YES/NO/UNSURE), current medications (<=500), up to **5 photos**, images only (JPEG/PNG/HEIC), each photo with
  an explicit `position` (attachment order).
- Migration **0062** (additive): `pre_visit_intake` (UNIQUE booking_id -> consultation_booking) and `pre_visit_intake_photo`
  (UNIQUE storage_key, UNIQUE (intake_id, position)); PostgreSQL repository writes the intake and its photo rows in ONE
  transaction, after the photo objects are stored (the CO-11 / FR-14 order). The PG test harness truncates the new tables with
  `consultation_booking` (PostgreSQL truncates a referenced table only with its referencing tables).
- Served routes: `POST /api/bookings/{id}/intake` (owner of an UPCOMING BOOKED booking only; every field and photo validated
  before any object is stored; a second intake 409 INTAKE_ALREADY_SUBMITTED); `GET /api/bookings/{id}/intake` and
  `GET …/intake/photos/{photo_id}` (the booking's owner or a veterinarian of the clinic; other owner / other tenant 404, other roles
  403; photos as `application/octet-stream` attachments). All audited. `served_routes.json` regenerated (+3); no FR state change.
- Web: `/owner/appointments/[bookingId]/intake` (form -> read-only submitted view with photo downloads), linked from each
  upcoming appointment (`appointment-intake`). Photos are stored in the governed document store (local mode in the full stack,
  as CO-11 — no provider involved); the production object store binding remains GATE_CREDENTIAL_ENTRY, untouched.

## Defect found and fixed in this unit (one fix attempt)
Run 1 of the full-stack spec FAILED on en-mobile and ar-mobile: the veterinarian read the photos in the wrong order. All photos of
an intake share one upload instant, so PostgreSQL ordered them by the random photo id. Desktop runs passed by chance. Fix: an
explicit `position` column (0..n-1, unique per intake) and `ORDER BY position`; the PG test now gives both photos the same instant
and ids that sort AGAINST attachment order (perturbation P-D2P-CO06-PG-PHOTO-ORDER-BY-ID is ARMED). Run-1 results of all four
projects, pre-fix, are kept in `evidence/replay/2026-10-16-epc-d-d2p/prefix-run1/`.

## Full-stack acceptance after the fix (each project separately, one worker, no concurrent backend run)
| PROJECT | CO-06 `@S:CO-06` | J-O5 regression (appointments page changed; run before the backend-only fix) |
|---|---|---|
| en-desktop | PASS | PASS |
| ar-desktop | PASS | PASS |
| en-mobile | PASS | PASS |
| ar-mobile | PASS | PASS |

The spec: owner home -> my appointments -> intake; reason, since, eating NO, medications, two photos (PNG, JPEG); submitted view
with 2 photos, PNG bytes downloaded intact; reload keeps it (server-held); second submission 409; the clinic veterinarian reads
the same reason and photos in attachment order; Arabic: no untranslated copy.

## Evidence
| Check | Result |
|---|---|
| backend, CI command | **1307 passed, 0 failed** |
| D2p served API tests · PostgreSQL control | 7 passed · 1 passed, 0 skipped (added to the CI PostgreSQL list) |
| tsc · web vitest | clean · **47 files / 245 passed** (J-O5 booking page tests unchanged and passing) |
| perturbations (`perturb_epc_d_d2p_co06.py`) | **13 ARMED / 0 VACUOUS** (a "no explicit transaction" perturbation was not included: a pool connection rolls the block back on error anyway, so it would be vacuous by construction) |
| migration invariants · register status | 14 passed |
| prohibited-literal / secret / evidence bundles | 0 / CLEAN / 32 bundles FAILED=0 |

## Counting
CO-06 counts when `report.mjs` reports it PASS in all four projects from the CI full-stack run of this PR's head; matrices are
taken from that run, not edited. No journey is tagged. No ledger X-row closes.
