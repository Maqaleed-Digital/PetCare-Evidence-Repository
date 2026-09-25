# U14 · FR-20 cash on delivery with digital receipting — AC-FR-20-01/02 closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U14   BASE_MAIN=fb3c1f6fe5b9b8d4ca61dc152a56859a561b0db2 (U13 merged, PR #58)
BRANCH=build/u14-fr20
SELECTION (pass 1): FR-20 = 2 dependency criteria, ABSENT; next by id after FR-19.
CRITERIA_CLOSED=[AC-FR-20-01, AC-FR-20-02]
GAPS_REMAINING={AC-FR-20-03: [AUDIT, DEPENDENCY, SERVED_APP_E2E], AC-FR-20-04: [AUDIT, DEPENDENCY, TENANT_ISOLATION]
                — EXTERNAL:LOGISTICS_PARTNER}
FR-20: ABSENT / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE (exclusively EXTERNAL-gated)
```

## Build
- Migration 0047: `tenant_price` (append-only; latest wins, insertion `seq` breaks same-instant ties), `customer_order`
  (+ lines; payment_method CHECK COD), `order_collection` (inserted only when the amount equals the stored total),
  `order_receipt` (FK to the collection — no receipt without a confirmed collection). Insert-only.
- `orders.py` + `PostgresOrderRepository`. Routes: `POST/GET /api/catalog/prices` (clinic admin sets; listing shows
  GENERAL/OTC only), `POST /api/orders` (owner; COD; server-priced; POM/RESTRICTED/CONTROLLED not orderable — they are
  dispensed against a prescription), `POST /api/orders/{id}/deliver` (staff: stock leaves as SUPPLY movements with
  batches; collection confirmation of the exact total + reference; receipt rendered in the owner's stored language,
  Arabic default; collection + receipt in one transaction; audited cash_collected / delivered / receipt_issued),
  `GET /api/orders`, `GET /api/orders/{id}/receipt` (owner or staff; retrievable later).
- UI `/owner/orders`: checkout with cash on delivery (sends product + quantity only); receipts shown in their
  language, RTL for Arabic.

## Defect caught during the unit
The first price repository broke same-instant ties by a random UUID (PostgreSQL) and by first-write (in memory), so
"latest price wins" was nondeterministic; the PG test caught it. Fixed with an insertion sequence (PG) and a stable
last-wins pick (memory) before anything merged.

## Evidence
AC-01 {SERVED_APP_E2E, PERSISTENCE (PG), UI ARTEFACT} · AC-02 {SERVED_APP_E2E, PERSISTENCE x2 (PG), UI + ARABIC_RTL
ARTEFACT fr20-cod-orders}. AC-03/04 NOT registered: the exact-total confirmation rule is tested, but the logistics
partner's confirmation interface is not held.

## Perturbations
```
P-AC01-NOT-COD             order does not record COD                -> AC-01 test FAILS          ARMED
P-AC01-PRICE-NOT-SERVER    price not from the tenant price list     -> AC-01 test FAILS          ARMED
P-AC01-POM-ORDERABLE       prescription products orderable          -> AC-01 test FAILS          ARMED
P-AC01-UI-NOT-COD          checkout sends another method            -> vitest FAILS              ARMED
P-AC02-NO-RECEIPT          no receipt retrievable                   -> AC-02 test FAILS          ARMED
P-AC02-WRONG-LANGUAGE      receipt ignores the owner's language     -> AC-02 test FAILS          ARMED
P-AC02-RECEIPT-UNSCOPED    another owner can read the receipt       -> AC-02 test FAILS          ARMED
P-AC02-UI-LTR              Arabic receipt rendered LTR              -> vitest FAILS              ARMED
P-AC02-DB-NO-FK            receipt FK to collection removed         -> PG test FAILS             ARMED
P-AC03-PAID-UNCONFIRMED    route guard on the collection removed    -> VACUOUS (first attempt): the repository's
                           validate_collection refuses the same amount — defence in depth, not a defect. REDESIGNED as:
P-AC03-NO-CONFIRMATION-CHECK-ANYWHERE  route guard AND repository check removed together -> rule test FAILS  ARMED
FINAL SET: PERTURBATIONS=10 ARMED=10 VACUOUS=0
```
