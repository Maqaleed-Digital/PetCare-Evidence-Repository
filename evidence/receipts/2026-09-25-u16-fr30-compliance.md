# U16 · FR-30 SFDA compliance reporting automation — AC-FR-30-01/02/03 closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U16   BASE_MAIN=382fe8e8571fd23430cdd300f6c9588b81487dc3 (U15 merged, PR #60)
BRANCH=build/u16-fr30
SELECTION (pass 1): FR-30 = 2 dependency criteria, ABSENT; last of the 2-dependency ABSENT FRs.
CRITERIA_CLOSED=[AC-FR-30-01, AC-FR-30-02, AC-FR-30-03]
GAPS_REMAINING={AC-FR-30-04: [DEPENDENCY, SERVED_APP_E2E], AC-FR-30-05: [AUDIT, DEPENDENCY] — EXTERNAL:SFDA}
FR-30: ABSENT / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE (exclusively EXTERNAL-gated)
```

## Build
- Migration 0049: antimicrobial agent/class on `product_registration` (both or neither; registration facts);
  `prescription_product` (a prescription names its registered product; `PrescriptionRequest.product_id` optional);
  `notifiable_disease` (governed register: code + statutory window; no served write path); `notifiable_case`
  (report_due_at NOT NULL and > detected_at); `notifiable_case_report`; `compliance_report` (period, rows, content hash).
- AC-01 `POST /api/compliance/reports/controlled-substances`: every CONTROLLED ledger movement of the session tenant in
  the period — receipts, dispenses (with their prescription), adjustments — generated automatically; each total carries
  the movement ids it sums; the header is stored and audited. `GET …/reports/{id}` re-derives from the ledger and states
  whether it reproduces the stored hash (it does not once the period's ledger changes — the check is live).
- AC-02 `GET /api/compliance/antimicrobials?group_by=…`: structured records only (prescription → registered product →
  agent/class; pet profile → species; issuing vet; month) with a coverage statement; a prescription naming a drug only
  in free text is outside the register (never text-searched); unresolved species are listed.
- AC-03 `POST /api/pets/{id}/notifiable-cases` (vet, live authority): clock = detection + the register's window;
  `GET /api/compliance/notifiable-cases` shows OPEN / OVERDUE / REPORTED with hours remaining; `…/{id}/reported`.

## Evidence
AC-01 {PERSISTENCE (PG), AUDIT, TENANT_ISOLATION} · AC-02 {PERSISTENCE (PG)} · AC-03 {AUDIT}. AC-04/05 not built.

## Perturbations
```
P-AC01-DISPENSES-OMITTED     report drops SUPPLY movements          -> AC-01 test FAILS      ARMED
P-AC01-UNTRACEABLE-TOTALS    totals carry no movement ids          -> AC-01 test FAILS      ARMED
P-AC01-REPRODUCE-UNCHECKED   re-derivation always "reproduces"     -> AC-01 test FAILS      ARMED
P-AC01-UNAUDITED             generation not audited                -> AC-01 test FAILS      ARMED
P-AC01-CROSS-TENANT          ledger read unscoped                  -> AC-01 test FAILS      ARMED
P-AC02-TEXT-SEARCH           free-text medication counted          -> AC-02 test FAILS      ARMED
P-AC02-NO-COVERAGE           coverage statement omitted            -> AC-02 test FAILS      ARMED
P-AC02-PG-NOT-DURABLE        PG antimicrobial facts not read back  -> PG test FAILS         ARMED
P-AC03-NO-CLOCK              window ignored (fixed 1h)             -> AC-03 test FAILS      ARMED
P-AC03-UNAUDITED             case not audited                      -> AC-03 test FAILS      ARMED
P-AC03-DB-NO-CLOCK-CHECK     clock NOT NULL / CHECK removed        -> PG test FAILS         ARMED
PERTURBATIONS=11 ARMED=11 VACUOUS=0
```

## Findings
- The notifiable-disease register and antimicrobial classification must be populated from the competent authority's
  lists (governed data, outside the programme); the platform refuses an unlisted disease rather than guessing.
