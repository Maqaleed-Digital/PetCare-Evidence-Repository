# U11 · FR-06 durable consultation record + fail-closed telemedicine gate — AC-FR-06-04 closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U11   BASE_MAIN=41236b663bbc24b20880d1583fc4919a7ae65caf (U10 merged, PR #55)
BRANCH=build/u11-fr06-teleconsult
SELECTION (pass 1): FR-06 = 2 dependency criteria, ABSENT; next by id.
CRITERIA_CLOSED=[AC-FR-06-04]
AC-FR-06-05: built fail-closed, UI evidenced; gap = [DEPENDENCY] only — COUNSEL:REG-02_TELEMEDICINE.
GAPS_REMAINING={AC-FR-06-01: [ARABIC_RTL, SERVED_APP_E2E, UI] — see SQ-2; AC-FR-06-02: [SERVED_APP_E2E] — see SQ-2;
                AC-FR-06-03: [DEPENDENCY, SERVED_APP_E2E] — PRODUCTION; AC-FR-06-05: [DEPENDENCY] — COUNSEL:REG-02}
FR-06: ABSENT / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE
```

## Build
- Consultations were a module-level dict (lost on restart; the U7 finding). Now `consultations.py` +
  `PostgresConsultationRepository` over migration 0044: `consultation` (participants, requested_by, mode) and
  `consultation_outcome` (one per consultation, recorder named) — insert-only, status derived; every read goes through
  the repository with the session tenant (notes, messaging participant check, reads).
- `POST /api/consultations`: session tenant (body tenant optional; a disagreeing one 403); both participants must be
  identities of the tenant in their roles (owner / veterinarian). `POST …/{id}/outcome`: the consultation's vet with a
  live authority, once (409 after); audited. `GET /api/consultations` (own; admin: tenant).
- **AC-05 fail-closed gate.** `regulatory_determination` (REG-02_TELEMEDICINE, LAWFUL/NOT_LAWFUL, reference, recorder)
  has NO served write path. `mode=REMOTE_VIDEO` is refused (403 REMOTE_CONSULTATION_NOT_OFFERED, audited) unless the
  latest REG-02 determination is LAWFUL; `GET /api/consultations/remote/availability` says why. UI
  `/account/consultations` lists consultations with outcomes and, while the gate is closed, states that remote
  consultation is not offered and presents NO video/remote control.

## Not built in U11 — and why (SPONSOR_QUEUE SQ-2)
AC-FR-06-01 ("an owner and a verified vet can hold a scheduled video consultation with screen sharing from the served
application") and AC-FR-06-02 (720p, adaptive bitrate) are ratified with dependency NONE, while AC-FR-06-05 keeps remote
consultation fail-closed until REG-02 counsel. The served deployment therefore cannot demonstrate AC-01/02 today. The
video capability itself (WebRTC signaling, screen share, resolution/ABR records) is internally buildable behind the
gate and is scheduled for FR-06's next pass; SQ-2 asks how AC-01/02 are to be accepted.

## Tests changed because the requirement changed
`test_fr01_session_identity.py::test_appointment_and_consultation_records_are_tenant_scoped` named a non-existent owner
("o"); it now names the owner it had already created. Assertions unchanged.

## Evidence
AC-04 {PERSISTENCE x2 (PG), AUDIT, TENANT_ISOLATION} · AC-05 {UI ARTEFACT fr06-consultations.test.tsx}; DEPENDENCY not
evidenced. The gate test substitutes the determination list in-process (test setup, not counsel evidence).

## Perturbations
```
P-AC04-OUTCOME-UNAUDITED  outcome not audited                 -> record/audit test FAILS          ARMED
P-AC04-OUTCOME-ANYONE     anyone may record the outcome       -> record/audit test FAILS          ARMED
P-AC04-PARTICIPANTS       participant check removed           -> participants test FAILS          ARMED
P-AC04-TENANT             repository get ignores tenant       -> cross-tenant test FAILS          ARMED
P-AC04-DB-ONE-OUTCOME     outcome PK removed                  -> PG second-outcome test FAILS     ARMED
P-AC05-GATE-OPEN          gate always LAWFUL                  -> fail-closed gate test FAILS      ARMED
P-AC05-UI-NONOTICE        page omits the not-offered notice   -> vitest FAILS                     ARMED
PERTURBATIONS=7 ARMED=7 VACUOUS=0
```

## Findings
- Consultation NOTES (`_notes`) remain an in-memory store — clinical records, not an FR-06 criterion; recorded.
- FR-07 binding's `unresolved` corrected: consultation sessions are durable since this unit.
