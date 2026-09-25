# U9 · FR-14 prescription upload and vet verification — AC-FR-14-01..05 closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U9   BASE_MAIN=1448dc1eaaaafb1f14b53591bfc560ee52c6d070 (U8 merged, PR #53)
BRANCH=build/u9-fr14-dispensing
SELECTION (pass 1): FR-14 = 2 dependency criteria, REACHABLE_TESTED — first remaining under the rule.
CRITERIA_CLOSED=[AC-FR-14-01, AC-FR-14-02, AC-FR-14-03, AC-FR-14-04, AC-FR-14-05]
GAPS_REMAINING={AC-FR-14-06: [DEPENDENCY, SERVED_APP_E2E] — EXTERNAL:SFDA_API;
                AC-FR-14-07: [DEPENDENCY, SERVED_APP_E2E] — PRODUCTION}
FR-14: REACHABLE_TESTED / EVIDENCE_INCOMPLETE (0/7)  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE (5/7; rest dependency-held)
```

## Build
- **AC-01.** `GET /api/prescriptions/queue/awaiting-verification` (vet). `PrescriptionRequest.tenant_id` optional — the
  session decides; a disagreeing value is still refused (403). UI `/vet/prescriptions`: issue (no actor/tenant sent),
  attach documents, verify; Arabic default RTL. Dispensing stays on `/pharmacy`.
- **AC-02.** A non-veterinarian dispense is now AUDITED (`prescription.dispense_denied`, NOT_VETERINARIAN) before the
  403. No dispensing path reads a class from the request; `/api/inventory/supplies` forbids `supply_class` (422).
- **AC-03.** `POST /api/inventory/supplies` + migration 0042: a SUPPLY movement on the FR-13 ledger. GENERAL/OTC:
  tenant staff, no prescription. POM/RESTRICTED/CONTROLLED/unregistered: a VET_VERIFIED prescription of the session
  tenant, a veterinarian with a live authority; the supply dispenses the prescription (compensating movement if the
  dispense loses a race). CHECK `stock_movement_supply_gate`: the DATABASE refuses a vet-only SUPPLY without a
  prescription, and any SUPPLY that adds stock. Refusals audited `inventory.supply.refused`.
- **AC-04.** The served refusal already named attribute + expiry (U5); now asserted exactly. The UI reads
  `/api/practitioners/me/authority` and presents prescribing as unavailable (disabled fieldset) with the attribute and
  the localised expiry, instead of failing on submit.
- **AC-05.** Every prescription read is audited with the session actor via `_rx_read_audit`: document list, both
  queues, transitions (single read and download were already audited).
- **AC-06 (EXTERNAL:SFDA_API).** `petcare_api/sfda.py` port: only VALID is valid; INVALID/UNKNOWN/UNAVAILABLE and any
  unrecognised answer are not; the served adapter is `UnconfiguredSfdaAdapter` (UNAVAILABLE). Route
  `POST …/sfda-validation`, audited.
- **AC-07 (PRODUCTION).** `GET /api/prescriptions/metrics/verification-time`: share verified within 30 min, p95.

## Evidence — and what is deliberately NOT registered
- AC-01 {SERVED_APP_E2E; PERSISTENCE x2 (existing PG lifecycle + served-app-to-Postgres); UI ARTEFACT} · AC-02
  {SERVED_APP_E2E, AUDIT} · AC-03 {SERVED_APP_E2E x6 parametrised} · AC-04 {SERVED_APP_E2E; UI ARTEFACT} · AC-05
  {TENANT_ISOLATION, AUDIT; PERSISTENCE x2 existing PG}.
- **AC-06 SERVED_APP_E2E is NOT registered.** The criterion is "passes an adapter/contract test of the SFDA
  prescription-validation interface". The contract double in the test encodes OUR reading; the published SFDA
  interface is not held. Registering it would be the fabricated integration proof the ratified text forbids. The gap
  is attributable to EXTERNAL:SFDA_API (interface spec + access).
- **AC-07 SERVED_APP_E2E is NOT registered.** The fails_if is a production measurement; the instrument is built and
  tested, the reading is the PRODUCTION dependency.

## Tests
```
petcare_api/tests/test_fr14_prescriptions.py (served_app, 12)   petcare_api/tests/test_fr14_supply_postgres.py (2, CI PG list)
petcare_web/__tests__/fr14-prescriptions.test.tsx (vitest, 2)
```

## Perturbations
```
P-AC01-SKIPVERIFY      ISSUED->DISPENSED allowed                 -> governed-transitions test FAILS          ARMED
P-AC01-UI-NOVERIFY     verify button does not POST /verify       -> vitest 'issues a prescription' FAILS     ARMED
P-AC02-DISPENSE-ROLE   dispense role check removed               -> client-asserted-class test FAILS         ARMED
P-AC03-UNGATED         prescription gate off for every class     -> 4 POM/RESTRICTED/CONTROLLED/unreg FAIL   ARMED
P-AC03-OVERGATED       prescription gate on for every class      -> GENERAL/OTC tests FAIL                   ARMED
P-AC04-NOAUTHORITY     live authority not required to issue      -> lapsed-vet test FAILS                    ARMED
P-AC04-UI-ENABLED      prescribing fieldset never disabled       -> vitest 'authority expired' FAILS         ARMED
P-AC05-READ-UNAUDITED  transitions read not audited              -> read-and-transition audit test FAILS     ARMED
P-AC06-UNKNOWN-VALID   UNKNOWN treated as valid                  -> SFDA port contract test FAILS            ARMED
P-AC07-TARGET          target 60 min instead of 30               -> instrument test FAILS                    ARMED
PERTURBATIONS=10 ARMED=10 VACUOUS=0   (byte-exact restore, sha256 checked)
```

## Findings
- **Prescription ↔ product.** Prescriptions name the medication as free text; a POM supply cites a VET_VERIFIED
  prescription but the product is not bound to it. Binding requires the registered product catalogue (FR-04).
- **Read auditing volume.** The dispensing dashboard polls the queue every 2 s, and each poll is now an audit event
  (the ratified statement is "every prescription read"). Recorded for operations sizing; not a defect.
