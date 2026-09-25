# U13 · FR-19 batch tracking and recall notifications — AC-FR-19-01/02 closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U13   BASE_MAIN=05149b33d163202ebfb02a3b2b8000b984953a97 (U12 merged, PR #57)
BRANCH=build/u13-fr19
SELECTION (pass 1): FR-19 = 2 dependency criteria, ABSENT; next by id after FR-16.
CRITERIA_CLOSED=[AC-FR-19-01, AC-FR-19-02]
GAPS_REMAINING={AC-FR-19-03: [DEPENDENCY, SERVED_APP_E2E], AC-FR-19-04: [DEPENDENCY, SERVED_APP_E2E] — EXTERNAL:SFDA_API}
FR-19: ABSENT / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE (exclusively EXTERNAL-gated)
```

## Defect found and fixed
The Option A route `POST /api/prescriptions/{id}/dispense` dispensed WITHOUT touching stock, so a dispense recorded no
batch — AC-FR-19-01's statement ("every stock movement and dispense records the batch"). A verified prescription is
now dispensed only FROM STOCK: the request names location, product, batch and quantity, and the dispense is a SUPPLY
movement citing the prescription (compensating movement if the transition loses a race). Authority, tenancy and state
refusals are unchanged (403/404/409 are decided before the stock origin); a verified prescription with no stock origin
is refused 400 STOCK_ORIGIN_REQUIRED and stays VET_VERIFIED. The pharmacy page now sends the stock origin.

## Build
- Receipts record the batch expiry (BRD P392; 400 BATCH_EXPIRY_REQUIRED); balances surface it. The DB already refuses a
  blank batch, a zero quantity, and any UPDATE/DELETE of a movement (migration 0041).
- Migration 0046: `stock_movement.batch_expiry`, `recall`, `recall_notification` (one per affected dispense).
- `recalls.resolve`: SUPPLY movement -> prescription -> pet profile -> owner, through stored records of the tenant only.
  A supply with no prescription, a prescription not stored, or a pet not stored goes to the INDETERMINATE partition
  (always present, with its reason); every output carries a completeness statement. `POST /api/recalls` (tenant staff)
  writes the recall and one notice per resolved dispense in ONE transaction; audited `recall.created` and
  `recall.owner_notified`. `GET /api/recalls/{id}` re-resolves. `GET /api/me/recall-notices`; UI `/owner/recalls`.

## Tests changed because the requirement changed
Every success-path dispense in `test_option_a_workflow.py`, `test_dispensing_fail_closed.py`, `test_fr14_prescriptions.py`
and `test_prescription_persistence_postgres.py` now passes a stock origin (`tenant_fixtures.stock_origin`); the PG served
tests also route `api.INVENTORY_REPO` to PostgreSQL. Receipt helpers in `test_inventory.py` / `test_fr14_prescriptions.py`
supply a batch expiry. No assertion was weakened.

## Evidence
AC-01 {PERSISTENCE x2 (PG), AUDIT} · AC-02 {SERVED_APP_E2E, AUDIT, TENANT_ISOLATION; UI ARTEFACT fr19-recall-notices}.
AC-03/04 NOT registered (SFDA interface/feed not held); the boundary refusal is tested.

## Perturbations
```
P-AC01-DISPENSE-NOSTOCK    dispense bypasses stock               -> batch test FAILS             ARMED
P-AC01-RECEIPT-NOEXPIRY    receipt without expiry accepted       -> batch test FAILS             ARMED
P-AC01-DB-BATCH            DB blank-batch CHECK removed          -> PG refusal test FAILS        ARMED
P-AC01-UI-NOBATCH          pharmacy omits the batch              -> vitest FAILS                 ARMED
P-AC02-HIDE-INDETERMINATE  unresolvable pet dropped silently     -> recall test FAILS            ARMED
P-AC02-NO-COMPLETENESS     completeness statement omitted        -> recall test FAILS            ARMED
P-AC02-NO-NOTIFY           no owner notified                     -> recall test FAILS            ARMED
P-AC02-CROSS-TENANT        batch supplies not tenant-scoped      -> cross-tenant test FAILS      ARMED
P-AC02-UI-HIDDEN           owner page renders no notices         -> vitest FAILS                 ARMED
P-AC03-EMPTY-BATCH         recall without batch accepted         -> boundary test FAILS          ARMED
PERTURBATIONS=10 ARMED=10 VACUOUS=0
```
