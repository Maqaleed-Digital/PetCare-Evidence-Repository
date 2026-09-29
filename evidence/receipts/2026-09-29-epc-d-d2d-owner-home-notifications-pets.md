# MVC-EPC-D-001 v1.5 — Lane D unit D2d: CO-01 owner home, CO-14 notification centre (J-O10), J-O4 pets; R10–R13

```
PROGRAMME=MVC-EXTERNAL-PRODUCTION-CLOSURE-001   INSTRUMENT=MVC-EPC-D-001 v1.5   UNIT=D2d
BRANCH=lane-d/d2d-owner-pets-reminders-deliveries
START_HEAD=4896e3316e29d12f13f9af0b53e6a6035446777e (= origin/main = merge-base; D2c PR #86)
IMPLEMENTATION_COMMITS=3e6c09b (D2d + R10–R13) · c3783f9 (R12 test teardown) · 28d908f (D2c anchor collision)   END_HEAD=see PR
AUTHORITY: MVC-EPC-D-001 v1.5 [SPONSOR] + Sponsor continuation authority 2026-09-28 (R10, R11, R12) + ruling R13 2026-09-29
ACCEPTANCE_COUNTS=UNCHANGED — requirements/acceptance/** byte-identical; every registered test node id unchanged
```

## Phase V (accepted, not repeated)
Verified before this unit continued and re-checked on resume: HEAD = origin/main = merge-base = 4896e33; D0 525e849,
D1 e1a6e2d, D2a f2a6e21, D2b c47bb0a, D2c 4896e33 reachable; the preserved D2d worktree diff was unchanged.

## D2a traceability (not recreated)
D2a = canonical web app (`petcare_web`), auth-log PII removal, X-22 root cause. PR #84, head d88a304, merge
**f2a6e21ac0f303b612da1689be73459c97149cef** (reachable from main). Receipt:
`evidence/receipts/2026-09-28-epc-d-d2a-canonical-app-authlog.md`; ledger row in `2026-09-28-epc-d-ledger-s4.md`.

## What was built
- **CO-01 owner home** (`app/owner/page.tsx`): the pets shown are the served `/api/pets` list — explicit loading and
  error states, never a claimed "no pets" before the server answers; cards link to the served screens (pets,
  notifications, orders/deliveries, account); the dead `href="#"` booking link is gone (booking disclosed as not yet
  available — J-O5).
- **CO-14 notification centre** (`app/owner/notifications/page.tsx`): one chronological list of FR-23 reminders and
  FR-19 recall notices from the server; nothing generated or stored in the browser.
- **J-O4 pets** (`e2e-full/jo4-pets.spec.ts`) and **J-O10 notifications** (`e2e-full/jo10-notifications.spec.ts`).
- **Harness teardown**: Playwright ends the API stack with SIGTERM; `tools/e2e_stack.py` turns SIGTERM/SIGHUP into a
  normal exit so the throwaway cluster is stopped (finding D2D-E2E-CLUSTER-LEAK).

## R10 / X-25 — reminder consent enforced at dispatch
The only reminder dispatch boundary is `POST /api/reminders/run` (`main.run_reminders`). Immediately before each send
it calls `owner_consent.reminder_dispatch_decision` on the server ledger, in the tenant that holds the due item.
Admitted only when the owner's latest `care_reminders` event is a well-formed GRANT; ABSENT, REVOKED, MALFORMED and
UNREADABLE (any read error) refuse. A refusal records nothing, is audited `reminder.withheld` (denied, reason code
`<REASON>:owner:<id>`) and is returned under `withheld`. The ledger has no expiry semantics, so none is applied. No
provider is called: delivery is IN_APP.
Tests `test_epc_d2d_reminder_consent.py`: admitted with consent; absent; revoked; unreadable; malformed; revoke after
an earlier grant stops the later 24-hour reminder; consent from another tenant does not admit; the decision table (9).
Full stack: J-O10 — the first run withholds `CONSENT_ABSENT`, the owner grants on /account, the next run delivers once.
**This is a governed product/security decision. It is NOT a legal conclusion about the lawful basis for care
reminders under Saudi PDPL, and nothing in this receipt represents it as one.**
**X-25 = CLOSED_WITH_EVIDENCE** (tests + ARMED perturbations below + J-O10).

## R13 — Sponsor ruling, Option A
```
R13_DECISION=OPTION_A
R13_TESTS_AMENDED=4, method: in place, insert-only precondition (the register's TEST items are keyed by node id and
  carry no supersession mechanism), provenance below
R13_ASSERTIONS_CHANGED=NO
AC_FR_23_01_ANNOTATED=YES  (governance/sponsor_acts/MVC-EPC-D-001-R13-FR23-CONSENT.md; ratified text unchanged)
```
| TEST_ID | BEFORE (file sha256) | AFTER (file sha256) | PRECONDITION_CHANGE | ASSERTIONS_CHANGED | COVERAGE_WEAKENED |
|---|---|---|---|---|---|
| AC-FR-23-01 `test_fr23_reminders.py::test_a_due_date_reminds_the_owner_seven_days_and_again_24_hours_before_if_outstanding` | ce1b1795…f7ae | 5f1b99c6…b9 | owner grants care_reminders via POST /api/me/consents/care_reminders | NO | NO |
| AC-FR-23-01 `test_fr23_reminders.py::test_reminders_never_reach_another_tenants_owner` | ce1b1795…f7ae | 5f1b99c6…b9 | both owners grant | NO | NO |
| AC-FR-23-02 `test_fr23_reminders.py::test_reminders_are_in_the_owners_language_and_every_send_is_audited` | ce1b1795…f7ae | 5f1b99c6…b9 | both owners grant | NO | NO |
| AC-FR-09-03 `test_fr09_notification_language.py::test_every_notification_and_document_is_in_the_recipients_language` | 33c1fa29…b4 | 54e469fe…cf | each owner grants before the reminder run | NO | NO |

Full hashes — before: test_fr23_reminders.py `ce1b1795e9fc74e1b7491b943a7d8406d3fab7969d4d25cbcfd5f6e54164f7ae`,
test_fr09_notification_language.py `33c1fa298bcc75b0f49a57edddf05c5116eaa261a5ad358c0eae510a069cf1b4` (last changed by
U19 9769603); after: `5f1b99c608ecb72b547de1670eb650bc3bbae01aa4f0cc15e4c39d33dc2347b9`,
`54e469fe252abc39f7d112d3dad522d871a92358337bba3ac98e8750bbddb8cf`. Diffs are insert-only: 0 lines removed, 10 and 3
added. REASON=R10 makes consent a dispatch precondition. RULING=R13.

## R13.3 — consent capture at onboarding
```
CARE_REMINDERS_OFFERED_AT_ONBOARDING=NO (before D2d) -> YES (D2d, served and tested)
```
Before: the served signup (`components/auth/AccountFlows.tsx` → `POST /api/auth/self-register`) offered only the
required privacy-notice checkbox; care reminders could be granted only later on /account. Bounded, D2d-owned
correction: signup now offers care reminders as a SEPARATE, OPTIONAL, UNTICKED choice; the server records a
`care_reminders` GRANT (origin self_registration) only for a JSON boolean `true` (`StrictBool`: "yes"/1 → 422); it can
never stand in for the privacy notice. Invite registration is tenantless at registration (D2C-INVITE-CONSENT-DEFERRED):
those owners grant on /account. Evidence: J-O1 asserts the choice is visible, unticked and not required (4 projects);
`test_an_owner_who_leaves_care_reminders_unticked_gives_no_reminder_consent`,
`test_an_owner_who_ticks_care_reminders_at_signup_is_recorded_server_side_and_admitted`,
`test_only_a_real_boolean_counts_as_a_care_reminders_choice` (3), `test_care_reminders_cannot_stand_in_for_the_privacy_notice`.

## R11 / X-26 and R13.5 — identity authority
Legacy `POST /api/appointments` stores the client-supplied `owner_id` (and `clinic_id`) — X-26 confirmed. No
`petcare_web` code calls it; D2d does not touch it; D2d only removes the owner home's dead booking link.
**X-26 remains OPEN, owned by J-O5.** No historical perturbation targeting the legacy route required exclusion.
```
R11_EQUIVALENT_DEFECT_SEARCH=COMPLETE
PATHS_SEARCHED=petcare_api/*.py + petcare_api/routers/*.py (36 files: AST over every pydantic request model for the
  fields owner_id,user_id,tenant_id,clinic_id,actor_id,veterinarian_id,vet_id,pharmacy_id,recipient_id,patient_id,
  practitioner_id,created_by,recorded_by,issued_by,target_user_id,role, then every handler use of body.<field>);
  petcare_web/{app,components,lib} (every request body carrying owner_id/user_id/tenant_id/clinic_id)
CANDIDATES=11 request models (+0 web request bodies)
CONFIRMED_EQUIVALENT_DEFECTS=1
R11_EQUIVALENT_DEFECT_RESULTS=POST /api/appointments owner_id (+clinic_id) = X-26 (J-O5)
```
| Model / route | Field(s) | Classification |
|---|---|---|
| AppointmentRequest · POST /api/appointments | owner_id, clinic_id | **CONFIRMED** — client identity stored verbatim = X-26 (J-O5) |
| PetRequest · POST /api/pets (platform_admin branch) | owner_id | **RELATED — unvalidated selector** (caller identity is server-derived, but the named owner was not checked). D2d-owned (CO-02/J-O4): **fixed** — must be an owner of the session tenant; `test_epc_d2d_pet_owner_selector.py` (2) + P-D2D-PET-OWNER-UNVALIDATED |
| ConsultationRequest · POST /api/consultations | pet_id vs owner_id | **RELATED — unvalidated selector**: participants are validated against tenant+role, but `pet_id` is not checked to be that owner's pet in the tenant. Owned by the consultation journeys (J-O6/J-V3) — reconciled as canonical ledger row **X-27**, not fixed here |
| ConsultationRequest / PrescriptionRequest / NoteRequest / PetRequest / TenantMembershipRequest | tenant_id | NOT A DEFECT — `require_tenant(request, body.tenant_id)` refuses any value ≠ the session tenant (membership is platform-admin only, actor from session) |
| ConsultationRequest | owner_id, veterinarian_id | NOT A DEFECT — validated as identities of the session tenant in those roles |
| DeliveryRequest · POST /api/deliveries | owner_id | NOT A DEFECT — validated as an owner of the session tenant |
| AppointmentRequest/ConsultationRequest/PrescriptionRequest | clinic_id | stored label only — never used in any authorization comparison (search: 0 comparisons) |
| AuditProbePayload · POST /audit/ui | actor_id | NOT A DEFECT — prefixed `client-asserted:` so it can never match a real principal |
| RoleChangeRequest / CredentialRequest / RegisterRequest | role | NOT A DEFECT — target values checked against `_ASSIGNABLE` / the invite's allowed role |

## R12 — scratch PostgreSQL ownership
`petcare_api/tests/pg_harness.py`: `start_ephemeral_cluster` writes `LANE_D_SCRATCH_OWNER.json` (owner, run nonce,
the data directory's real path, created_at, pid) BEFORE the server starts; `ownership_proof` requires the harness
prefix, a parseable marker naming this harness, binding to this directory's real path and (in-run) this run's nonce;
`cleanup_owned_cluster` removes nothing without that proof. Zero connections / a stopped server are never proof.
Tests `test_epc_d2d_scratch_ownership.py` (11): proven → removed; unmarked → refused; ambiguous (unreadable, wrong
owner, empty nonce, unbound path) → refused; copied marker → refused; other run → refused; unrelated name → refused;
stopped zero-connection unmarked → refused; the real harness marks before start and removes only its own cluster.
```
R12_PRIOR_OBSERVED_CLUSTER_COUNT=31
R12_CURRENT_REPRODUCIBLE_PRIOR_CLUSTERS=0
HISTORICAL_OWNERSHIP_PROVEN=NO
```
| Classification | Count | Items (measured 2026-09-28 and 2026-09-29) |
|---|---|---|
| PROVEN_HARNESS_OWNED | 0 | — |
| PROBABLE_HARNESS_OWNED | 4 | (a) pytest tmp `…/pytest-16/test_the_harness_marks_its_clu0/petcare-pg-ky0_w1rr`, postmaster started 2026-09-29 12:34:50 +03 during this unit's own run of P-D2D-HARNESS-UNMARKED (which suppresses the marker); cause fixed in c3783f9 (D2D-R12-TEST-LEAKED-ON-FAILURE). (b–d) `$TMPDIR/petcare-pg-i4xopchu` 12:59:47, `-s2o2qsl0` 13:01:43, `-lxhd2yku` 13:02:47, all running and unmarked, created inside the D3 BASE replay window (12:48:30–13:03:06) by base-code (4896e33) full-stack perturbations, which predate both the SIGTERM teardown and the marker — the D2D-E2E-CLUSTER-LEAK this unit fixes. The two HEAD replays and three full-stack runs of D2d code leaked none. All four: NOT stopped, NOT deleted (R12: unmarked ⇒ no cleanup) |
| NOT_PROVEN | 0 | — |
| NOT_HARNESS_OWNED | 2 | Homebrew `postgresql@16` service (`/usr/local/var/postgresql@16`); another session's `…/9ccd358c…/scratchpad/pgdata` (not harness naming). Untouched |

The 31 previously observed were at the host's SysV segment limit (kern.sysv.shmmni=32); none is reproducible now (0
`petcare-pg-*` directories anywhere searched; 1–2 segments in use), so no provenance is claimed for them.

## X-22 — unmasked
```
X22_TZ_MASKING=NO
X22_STATUS=OPEN
```
Backend suites ran with TZ unset (host +03). Outside 00:00–03:00 Riyadh the frozen U10 test passes, which proves
nothing, so R13.7's controlled clock was used: `evidence/replay/2026-09-29-epc-d/x22_controlled_clock.py` runs the
UNMODIFIED frozen test with `date.today()`, `datetime.now()`, `datetime.utcnow()` and `time.time()` pinned to ONE instant
(TZ not set; refuses TZ=UTC and non-+03 hosts; production code untouched):
- WINDOW 2026-09-29T22:30:00Z = **2026-09-30 01:30 Asia/Riyadh** → FAIL: `assert (201 == 400)` — a licence expiring
  "yesterday" by the local calendar (29 Sep) is accepted because the server compares with the UTC date (29 Sep).
- CONTROL 2026-09-30T09:00:00Z = 2026-09-30 12:00 Asia/Riyadh → PASS.

→ **REPRODUCED with discrimination.** Root cause is the frozen U10 fixture (D2a analysis); R13.7 forbids modifying U10,
so X-22 stays OPEN for its owning closure unit before CP1.

## PORT-08 — list-region expectation 6 → 4
```
PORT08_EXPECTATION=4
PORT08_EVIDENCE=base 4896e33 app/owner/page.tsx contains 0 fetch/useEffect calls: owner-timeline and owner-consents were
  static cards, always empty; timeline content is served on /owner/pets (selected pet medical_history records +
  prescriptions, each with an empty state; FR-02 screen; J-O4 4/4); consents are served on /account (ConsentLedger via
  DataView loading/empty/error; J-O2 4/4, J-O10 4/4); /vet 1 and /pharmacy 2 regions unchanged; no FR/AC names these
  home-page regions (PORT-08 register capability "Empty / loading / error state coverage per surface", closing commit
  4a2a9060); superseded expectation = 6 (set when /pharmacy went 4 → 2).
```

## Evidence
| Check | Result |
|---|---|
| tsc | clean |
| web vitest | 41 files / **215** passed |
| backend (CI command `pytest tests petcare_runtime/tests petcare_api/tests`, TZ unset, head 28d908f, 2026-09-29 13:21 +03) | **1204 passed, 0 failed, 0 skipped** |
| canonical checker `tools/check_register.py` | output == requirements/status.json; acceptance states, summary and acceptance block unchanged |
| served routes (`tools/list_served_routes.py main:app`, canonical env) | unchanged (requirements/served_routes.json byte-identical) |
| full stack (Playwright → petcare_web → main:app → PostgreSQL), ar/en × 1280/390, head 28d908f | **36/36**; journeys **7/53** (J-00, J-O1, J-O2, J-O3, J-O4, J-O10, J-O11); screens **7/107** (PUB-01, PUB-07, CO-01, CO-02, CO-03, CO-14, CO-15) |
| D2d perturbations `perturb_epc_d_d2d.py` | **19 ARMED / 0 VACUOUS** |
| FR-23 / FR-09 perturbations after R13.1 | perturb_u15.py **9/9 ARMED**, perturb_u19.py **3/3 ARMED** |
| D3 full corpus replay (`tools/corpus_replay.py`, detached checkouts) | base main 4896e33 **250** → head 28d908f **269** · head ARMED **264** · excluded **5** (the EXCLUSIONS.md items, unchanged) · 19 new, all ARMED · 0 removed · no classification change · **D3 PASS** |

## Generated artefacts
| File | Before sha256 | After sha256 | Generator |
|---|---|---|---|
| requirements/status.json | 9e4c9d5e1a746f906e0b7e4f3fbdc0aeb6ccfeadfd88b3a85307076b11d4220b | c92203635b8e750c82b4b399844a37ca74b94688c5ace9c1a0cd8810252275e0 | `tools/check_register.py` |

Diff inspected: FR-23 `counts.basis` 6 → 7 only (the added bindings basis line citing the consent gate and the R13 act).

## Findings
- **D2D-E2E-CLUSTER-LEAK (fixed):** Playwright ended the API stack with SIGKILL, so pg_harness's atexit never ran and
  every journey run leaked a cluster and its SysV segment. SIGTERM + signal handler.
- **D2D-R10-MASKED-TENANT-PERTURBATION (fixed before commit):** the first R10 draft read consent in the SESSION tenant.
  Under U15's P-AC01-NO-TENANT-SCOPE the leaked reminder was then withheld rather than sent, so the frozen isolation
  test passed and the perturbation turned VACUOUS. The gate now reads consent in the due's tenant (identical in the
  unperturbed world, where dues are tenant-scoped); tenant isolation stays with the two scopes U15 proves; U15 9/9 ARMED.
- **D2D-FIRST-ATTEMPT-VACUOUS (corrected):** P-D2D-HOME-EMPTY-BEFORE-SERVER first targeted surface-states.test.tsx,
  whose fetch stub answers `[]` (empty is then correct) — VACUOUS. Added `epc-d2d-owner-home.test.tsx`, which holds the
  answer back; redesigned perturbation ARMED. Never committed as VACUOUS.
- **D2D-R12-TEST-LEAKED-ON-FAILURE (fixed, c3783f9):** when the real-cluster R12 test failed (as under
  P-D2D-HARNESS-UNMARKED) it never stopped the server it started. It now stops (never deletes) its own server in a
  finally block. The one postmaster leaked before the fix is inventoried above and left untouched.
- **D2D-D3-CAUGHT-ANCHOR-COLLISION (fixed in-PR, 28d908f):** the first head replay stopped `perturb_epc_d_d2c.py`
  after 5 of 16: the new signup care_reminders append repeated the exact text P-D2C-SELF-REG-CONSENT-NOT-RECORDED
  anchors on, so its uniqueness assertion fired. The committed D2c script was NOT edited; the new code builds a named
  event instead. D2c 16/16 ARMED again; D3 re-run on 28d908f.
- **D2D-TEST-ORDER-FLAKE (fixed):** a new D2d signup test compared two same-instant consent events in ledger order
  (ties ordered by random event id); now compared as a set.
- **D2D-J-O10-FIXTURE-LANGUAGE:** the Arabic projects enter the due title in Arabic; the X1 untranslated-text scan is
  unchanged.
- **X-27 (new canonical ledger row):** consultation `pet_id` not validated against the selected owner/tenant.

## Remaining OPEN after D2d (towards CP1)
X-22 (frozen U10 fixture; owning closure unit) · X-26 (legacy appointments; J-O5) · X-27 (consultation pet selector;
J-O6/J-V3) · X-24 (canonical-app retirement statement; D9) · journeys 46/53 and screens 100/107 not yet PASS.
CP1 = Phase-1 engineering complete (LANE_D=FINISHED); CP2 = Phase-1 live; CP3 = project complete / full approved BRD.
D2d is NOT project completion. **NEXT_BOUNDARY=J-O5.**
