# U6 · FR-27 pharmacy operations dashboard — AC-FR-27-01/03/04 closed, 2026-09-24

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U6   BASE_MAIN=853e0fe34065f052ea813e1cde3a25ee0e7de5fa (U5 merged)
BRANCH=build/u6-fr27-dashboard   SELECTION: FR-01 has no closable gap (AC-03 SQ-1, AC-04 L-2) -> FR-27
  (1 dependency criterion, REACHABLE_TESTED)
CRITERIA_CLOSED=[AC-FR-27-01, AC-FR-27-03, AC-FR-27-04]
GAPS_REMAINING={AC-FR-27-02: [AUDIT, DEPENDENCY, SERVED_APP_E2E] — COUNSEL:L-2 (dispensing actor/credential for
  POM/RESTRICTED/CONTROLLED); DEPENDENCY evidence is never fabricated}
FR-27: REACHABLE_TESTED / EVIDENCE_INCOMPLETE (3 of 4 criteria evidenced)
```

## AC-FR-27-01 — updates without manual refresh (ACCEPT_WITH_THRESHOLD, REAL_TIME_BOUND=5_SECONDS)
Ratified text: p95 <= 5 s, measured over at least 100 events in the acceptance environment.
- **Build.** `petcare_web/app/pharmacy/page.tsx` re-reads the served queue every `QUEUE_REFRESH_MS`
  (`petcare_web/lib/pharmacyQueue.ts` = 2000 ms) — silent (no loading flash), and a failed refresh keeps the last good
  queue. Previously the queue loaded only on mount and after an action.
- **Measurement.** `petcare_api/tests/test_pharmacy_dashboard_realtime.py` (served_app): 100 events; a veterinarian
  verifies, a second authorised dashboard session (partner_clinic_admin, same tenant) polls until visible; asserts
  `p95(server visibility latency) + QUEUE_REFRESH_MS <= 5 s`, reading QUEUE_REFRESH_MS from the TS source (one source);
  a second tenant's dashboard shows none of the 100 items.
- **UI.** `petcare_web/__tests__/fr27-dashboard.test.tsx` (fake timers): interval inside the bound; a new verified
  prescription appears with no user action after one interval; a failed refresh keeps the last queue.

## AC-FR-27-03 — every dashboard action audited with the session actor and persisted
Already true of the dispense action; evidence registered, no build: AUDIT
`test_option_a_workflow.py::test_j_every_step_is_audited_with_a_server_derived_actor` (spoofed header ignored) ·
PERSISTENCE `test_prescription_persistence_postgres.py::test_j_audit_events_for_the_workflow_persist_and_chain`.

## AC-FR-27-04 — usable in Arabic with RTL
Covered by the U3 customer-facing sweep (`/pharmacy`). The AC-04 perturbation (force the dashboard `dir="ltr"`) was
first **VACUOUS**: the sweep only checked `document.documentElement.dir`. The sweep was strengthened — in Arabic mode no
element inside a customer-facing page may carry `dir="ltr"` — and the perturbation is now ARMED. The FR-09 ARTEFACT
sha256 for `language-fr09.test.tsx` was re-registered accordingly (FR-09 evidence unchanged in substance).

## Perturbations
```
P-AC01 auto-refresh removed                     -> 'appears with no user action' FAILS                      ARMED
P-AC03 dispense audit actor from client header  -> test_j_every_step_is_audited_with_a_server_derived_actor ARMED
P-AC04 dashboard forced LTR                     -> '/pharmacy: Arabic by default' FAILS (after strengthening) ARMED
PERTURBATIONS=3 ARMED=3 VACUOUS=0
```

## Results
```
REGRESSION_LOCAL=1016 passed / 0 skipped · WEB_UNIT(local)=168 passed · TSC clean · status current
M4: no FR lowered; ACCEPTED=[FR-02]
SCANNERS: SECRET_SCAN=CLEAN · ACTIVE_LITERAL_DEFAULT=0 · DIFF_CHECK=CLEAN
```

## Findings
- "Acceptance environment" is read as the CI/non-production served app; the ratified bound is met there with wide
  margin. A production-environment re-measurement is a PRODUCTION act, outside the programme.
