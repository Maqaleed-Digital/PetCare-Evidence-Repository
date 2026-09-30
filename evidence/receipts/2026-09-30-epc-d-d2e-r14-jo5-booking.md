# MVC-EPC-D-001 v1.5 — Lane D unit D2e: R14 post-D2d record closure; J-O5 consultation booking (CO-05, CO-07); X-26

```
PROGRAMME=MVC-EXTERNAL-PRODUCTION-CLOSURE-001   INSTRUMENT=MVC-EPC-D-001 v1.5   UNIT=D2e
BRANCH=lane-d/d2e-r14-jo5-booking   START_HEAD=2f9a3c6ae27598cb950a85124262e5db566bb7d6 (= origin/main = D2d merge, PR #87)
AUTHORITY: MVC-EPC-D-001 v1.5 [SPONSOR] + rulings R11, R13 (partial custody) + R14 and R15 (2026-09-30, custodied verbatim —
  evidence/receipts/2026-09-30-epc-d-rulings-register.md)
ACCEPTANCE_COUNTS=UNCHANGED — requirements/acceptance/** and governance/** byte-identical to base; every registered test
  node id unchanged; no existing evidence/receipts/* or evidence/replay/<dir>/** file changed
```

## Preflight (R14 §0)
```
PR=87 STATE=MERGED HEAD=62dff27eddcd3a43dfbcef6daad344e98dd9412d MERGE_SHA=2f9a3c6ae27598cb950a85124262e5db566bb7d6 (gh pr view)
ORIGIN_MAIN=2f9a3c6ae27598cb950a85124262e5db566bb7d6 (= expected)   ANCESTOR=YES   AUTHORITY_CHECK=PASS
R14_ALREADY_ISSUED=NO (see rulings register)
```

## R14.0 — post-D2d record closure
- Ledger segment s7 (`2026-09-30-epc-d-ledger-s7.md`) chains to s6 by sha256 and records PR #87's merge; s6 is not edited.
- **X-25 CLOSED** in the canonical ledger (Notion, 2026-09-30) with closure evidence naming merge
  `2f9a3c6ae27598cb950a85124262e5db566bb7d6`. Its required evidence — "Dispatch refuses without active consent; test + ARMED
  perturbation" — is met by the merged D2d tests, seven ARMED P-D2D consent perturbations and J-O10. The row states that this is
  an engineering consent control and **not a PDPL lawful-basis or legal-compliance conclusion**.
- R13 citations: `R13_CITATION_CHECK=NOT_VERIFIABLE`, `R13_CITATION_CORRECTION=NONE` (register §R13).

## R14.1 — X-27 and the CP1 denominator
```
EXPECTED_CP1_ROWS_TOTAL=14   CP1_ROWS_TOTAL=14 (measured: Notion Gap Ledger, Closure point = CP1, 2026-09-30)
CP1_ROWS=X-01 X-02 X-03 X-04 X-05 X-07 X-10 X-11 X-22 X-23 X-24 X-25 X-26 X-27   FINDING=NONE (no CP1_COUNT_MISMATCH)
```
X-27 stays OPEN (owned by J-O6/J-V3). **Finding D2E-X27-FROZEN-TEST-PRECONDITION:** closing X-27 means refusing a
consultation `pet_id` that is not the selected owner's pet. Frozen FR-01 tests
(`test_fr01_session_identity.py::test_client_actor_header_is_ignored_on_appointments_and_consultations`,
`::test_appointment_and_consultation_records_are_tenant_scoped`) create consultations with the placeholder `pet_id "p1"`,
which no owner owns. The X-27 fix will therefore need either a precondition-only amendment of those tests (the R13 method) or
a Sponsor ruling. This is recorded now so that J-O6 does not discover it late.

## R14.2 — bounded scratch PostgreSQL cleanup
The host was restarted at 2026-09-30 14:15 +03 (`uptime` 26 min at 14:41). Measured before any action:

| D2d item | PID | Data directory | Port | Present now | Action |
|---|---|---|---|---|---|
| (a) pytest `…/pytest-16/test_the_harness_marks_its_clu0/petcare-pg-ky0_w1rr` | not running | not found under /private/var/folders | — | NO | none |
| (b) `$TMPDIR/petcare-pg-i4xopchu` | not running | not found (`$TMPDIR/petcare-pg-*` = no match) | — | NO | none |
| (c) `$TMPDIR/petcare-pg-s2o2qsl0` | not running | not found | — | NO | none |
| (d) `$TMPDIR/petcare-pg-lxhd2yku` | not running | not found | — | NO | none |

The only running postmaster is PID 1525, Homebrew `postgresql@16` (`-D /usr/local/var/postgresql@16`), which is
NOT_HARNESS_OWNED and was not touched.
```
R12_PROBABLE_STOPPED=0/4 (none stopped by this runner: all four were already absent after the host restart; the
  mismatch is recorded, nothing was touched)
R12_DIRS_DELETED=0
```

## R14.3 — X-22 evidence package (no fix)
```
X22_STATUS=OPEN   TZ_OVERRIDE=NO
PRODUCT_FILE_LINES=
  petcare_api/routers/auth.py:487   now = datetime.now(timezone.utc)
  petcare_api/routers/auth.py:516   if licence_expiry < now.date():            -> LICENCE_EXPIRED   (UTC calendar)
  petcare_api/licences.py:92        if lic.expires_on < today:                  today = submitted_at.date() (UTC),
  petcare_api/licences.py:118 / petcare_api/postgres_repositories.py:1374        validate_licence(lic, today=lic.submitted_at.date())
  petcare_api/licences.py:71-72     expires_at(): lapses at the start of the next UTC day (used by main.py:3903 clinical-act
                                    recheck and main.py:3927 authority grant expires_at)
U10_FILE_LINES= (petcare_api/tests/test_fr05_licence.py, sha256 0682c259ff44b9aece72a3fddf05a3df628d68516bed5d7238ee13a6701325b0,
  last changed by U10 59682ab)
  :77   expired, _e2, code2 = _register_vet(T_A, expires_on=(date.today() - timedelta(days=1)).isoformat())   (host-local calendar)
  :78   assert expired.status_code == 400 and expired.json()["detail"]["error"] == "LICENCE_EXPIRED"
CONTROLLED_CLOCK_EVIDENCE=evidence/replay/2026-09-29-epc-d/x22_controlled_clock.py (sha256
  3e439b7830de57ab0d2aa795e439867249ae876ff2944575878ce2d9f9d202db): WINDOW 2026-09-29T22:30Z (= 01:30 Riyadh) FAIL
  `assert (201 == 400)`; CONTROL 2026-09-30T09:00Z PASS (D2d receipt; not re-run here)
ROOT_CAUSE_VERIFIED_FROM_SOURCE=YES — the frozen U10 test derives "yesterday" from the host-local calendar (:77) while the
  product judges licence dates on the UTC calendar (auth.py:487/516). Between 00:00 and 03:00 Riyadh, local "yesterday" equals
  the UTC "today", so the licence is not yet expired to the product and registration succeeds (201).
```
**Sponsor decision package (not selected here):**
- **OPTION_A — fixture/test date-basis correction.** Change only U10 line 77 so that "yesterday" is taken from the product's
  governed basis (`datetime.now(timezone.utc).date() - timedelta(days=1)`). The assertion at :78 is unchanged. This needs an
  authority that overrides R13.7 ("never edit U10") for this line only. Before sha256 `0682c259…25b0`; the after-hash is
  computed if and when this is authorised. Other `date.today()` uses (:29, :147, :165) do not fail in the window: a local date
  that is ahead of the UTC date is never "expired" to the product.
- **OPTION_B — change licence-date business semantics to the Asia/Riyadh calendar.** Dependent consequences:
  (1) auth.py:516 and validate_licence (licences.py:92, via :118 and postgres_repositories.py:1374) move to the Riyadh date;
  (2) for consistency, `VetLicence.expires_at()` (licences.py:72) would lapse at Riyadh midnight (21:00Z) instead of 00:00Z.
  That changes main.py:3903 (clinical-act recheck) and main.py:3927 (grant expires_at), and it breaks frozen U10 assertions
  test_fr05_licence.py:142 (`expires_at.startswith(<FUTURE+1>)`) and :166 (`expired at <UTC midnight>`), so B also needs a
  frozen-test ruling; (3) scoping B to registration only would leave registration (Riyadh) and expiry (UTC) inconsistent for
  three hours a day; (4) persisted `vet_licence.expires_on` values are unchanged — only their interpretation moves.

## R14.4 — CI initdb
**Fixed in this unit.** verify.yml now puts the runner image's PostgreSQL server binaries on PATH, and installs them if they
are absent. It also names `test_epc_d2d_scratch_ownership.py` in the "PostgreSQL controls must not be skipped" step, so the
real-cluster R12 test fails CI if it is skipped. CI proof is PENDING (no CI run exists: the push was refused); R14.4 stays an
open engineering finding until the CI log shows that step green with the test run.

## J-O5 / X-26 — what was built
- **Server (new routes):** `GET /api/booking/veterinarians`, `GET /api/booking/slots`, `POST /api/bookings`,
  `GET /api/bookings`, `POST /api/bookings/{id}/reschedule`, `POST /api/bookings/{id}/cancel`, all owner-only.
  - The owner, tenant and actor come from the session.
  - The body only selects a pet (it must be the caller's own pet in the session tenant, else 404) and a veterinarian (it
    must be a veterinarian identity of the session tenant, else 400).
  - A slot (future, on the default-hours grid, within 14 days) is held by one live booking per veterinarian (409
    SLOT_TAKEN). The database enforces this too, with the partial unique index in migration 0058.
  - Video is refused while its SQ-2 switch is off.
  - Every write is audited (`consultation.booking.created/rescheduled/cancelled`).
  - Another owner's booking is 404.
- **X-26 (R11, option "derives the owner from the session only"):** legacy `POST /api/appointments` now stores the session
  owner (owner role) or no owner (admin session). The body's `owner_id` is accepted for compatibility and ignored. The route
  is kept because eight frozen identity/session tests use it as their generic protected route; none asserts the stored owner.
  No historical perturbation anchors on the changed lines, so nothing was moved to EXCLUSIONS.md.
- **Web (petcare_web):**
  - CO-05 `/owner/book` offers the served pets, veterinarians of the clinic and free slots, with a reschedule mode.
  - CO-07 `/owner/appointments` lists the bookings; cancellation needs a confirmation.
  - The owner home now links to both screens, replacing the D2d "not available yet" disclosure. The mocked
    `e2e/pilot-path.spec.ts` badge assertion was updated because /owner no longer has a deferred card; that test is not
    registered evidence.
- **Assumption D2E-DEFAULT-HOURS (safe, reversible, recorded under R15.13):** until J-V2 (veterinarian availability, D3)
  exists, bookable slots are the clinic default hours: 30-minute slots, 09:00–17:00 Asia/Riyadh, next 14 days.

## Evidence
| Check | Result |
|---|---|
| new backend tests `test_epc_d2e_booking.py` | 10 passed |
| new PostgreSQL control `test_epc_d2e_booking_postgres.py` (real cluster) | 1 passed (+ D2 consent control 2 passed alongside) |
| D2e perturbations `evidence/replay/2026-09-30-epc-d/perturb_epc_d_d2e.py` | **16 ARMED / 0 VACUOUS** (after D2E-FIRST-ATTEMPT-VACUOUS, below) |
| tsc | clean |
| web vitest | 42 files / **220** passed |
| full stack J-O5, ar/en × 1280/390 | **4/4** |
| backend (CI command `pytest tests petcare_runtime/tests petcare_api/tests`, TZ unset, head 04995af) | **1215 passed, 0 failed, 0 skipped** (first run: 1214 + 1 failed = D2E-CI-PG-GUARD, fixed) |
| full-stack suite (Playwright → petcare_web → main:app → PostgreSQL), ar/en × 1280/390, head 04995af | **40/40**; journeys **8/53** (J-00, J-O1, J-O2, J-O3, J-O4, J-O5, J-O10, J-O11); screens **9/107** (PUB-01, PUB-07, CO-01, CO-02, CO-03, CO-05, CO-07, CO-14, CO-15) |
| D3 full corpus replay (`tools/corpus_replay.py`, detached checkouts) | base 2f9a3c6 **269** (264 ARMED) → head 04995af **285** · head ARMED **280** · excluded **5** (EXCLUSIONS.md, unchanged) · 16 new, all ARMED · 0 removed · no classification change · **D3 PASS** |
| CI | NOT RUN — the push was refused by the Claude Code session permission layer; D1 and the R14.4 CI proof are pending |
| canonical checker | only `served_route_count` 121 → 127; no FR/NFR status change; status.json regenerated by the generator (R4) |
| served routes (generator) | +6 (the routes above); served_routes.json a67836a4…c4b1 (was d91c8bc6…a6da); status.json b7743d06…a46a (was 9e4c9d5e…220b) |

## Findings
- **D2E-FIRST-ATTEMPT-VACUOUS (corrected before commit):** P-D2E-PAST-SLOT-BOOKABLE was VACUOUS because the test's "past"
  instant was off the slot grid, so the grid check refused it anyway. The test now uses a past instant that is on the grid,
  and the perturbation is ARMED. It was never committed as VACUOUS.
- **D2E-CI-PG-GUARD (caught by governance test):** `tests/governance/test_ci_postgres_coverage.py` failed because the new
  PostgreSQL suite was not yet named in CI's non-skip step. It is now named there.
- **D2E-FIRSTRUN-RACE / D2E-JO5-LOAD-WAIT (harness, fixed):** the first full-suite run failed 2 of 40 tests. J-O10 ar-mobile
  failed because the first-run guide opened after `dismissFirstRun` sampled visibility once, and the guide then intercepted
  the click. J-O5 ar-desktop failed because the "load" event came after 15 s under load, although navigation had completed.
  The fixture now waits up to 5 s for the guide, and J-O5 waits for `domcontentloaded`. No assertion was weakened.
- **D2E-X27-FROZEN-TEST-PRECONDITION:** see R14.1.

## Remaining OPEN towards CP1
X-01, X-02, X-03, X-05, X-07, X-10, X-11, X-22 (Sponsor A/B), X-24, X-26 (closes on merge of this unit), X-27.
CP1 = Phase-1 engineering complete. D2e is not project completion. **NEXT_BOUNDARY=J-O6.**
