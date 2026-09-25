# U8 · FR-13 real-time multi-location inventory — AC-FR-13-01/02/03 closed, AC-04 built fail-closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U8   BASE_MAIN=b19ac23a84cdd23330522986dd0e951f8b4f3b6c (U7 merged, PR #52)
BRANCH=build/u8-fr13-inventory   RESUMED AFTER MAC RESTART: branch existed at BASE_MAIN with no commits and no
  uncommitted work; nothing was recovered or discarded.
SELECTION (pass 1; FR-02/09/01/27/07 already taken): FR-13 = 1 dependency criterion (COUNSEL:L-2), ABSENT —
  first remaining under the rule (fewest dependency criteria, then status, then id).
CRITERIA_CLOSED=[AC-FR-13-01, AC-FR-13-02, AC-FR-13-03]
AC-FR-13-04: internally built and evidenced (SERVED_APP_E2E, AUDIT); gap = [DEPENDENCY] only — COUNSEL:L-2.
  DEPENDENCY evidence is never fabricated.
GAPS_REMAINING={AC-FR-13-04: [DEPENDENCY] — COUNSEL:L-2}
FR-13: ABSENT / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE (exclusively COUNSEL-gated)
```

## Build
- Migration `0041_fr13_inventory_ledger.sql` (additive): `inventory_location`, `product_registration`
  (supply class + source `SFDA_REGISTRATION`; no served write path), `stock_movement` (append-only ledger:
  non-zero integer delta, reason RECEIPT/ADJUSTMENT/TRANSFER_OUT/TRANSFER_IN, class resolved at the act, actor).
  A trigger refuses UPDATE and DELETE on `stock_movement`; indexes for the per-location and per-product checks.
- `petcare_api/inventory.py` (supply classes, `VETERINARIAN_ONLY = {POM, RESTRICTED, CONTROLLED}`, unregistered =
  POM, in-memory repository) · `PostgresInventoryRepository`: one transaction per request, advisory lock per
  (tenant, location, product, batch), a balance never goes below zero; balances are `SUM(quantity_delta)`.
- Routes (main.py): POST/GET `/api/inventory/locations` (a clinic administrator adds a location), GET
  `/api/inventory/stock[?product_id=]` (every location of the SESSION tenant with ledger-derived balances), POST
  `/api/inventory/movements` (receipt, adjustment, transfer = paired OUT/IN rows). Actor and tenant from the session;
  the body forbids actor/tenant/class (422). Tenant staff only (veterinarian, partner_clinic_admin); owners 403.
- AC-FR-13-04 (MVC-PHARM-001 §5, until counsel): a POM/RESTRICTED/CONTROLLED (or unregistered) product needs role
  veterinarian AND a live practitioner authority (`_require_practitioner_authority`); a refusal is audited
  `inventory.movement.refused` / denied. GENERAL/OTC stock is handled by tenant staff with no prescription or
  veterinarian gate. No pharmacy authority role was created.
- UI `petcare_web/app/pharmacy/inventory/page.tsx` (`/pharmacy/inventory`, existing middleware vet/admin): stock per
  location, re-read every `INVENTORY_REFRESH_MS` (`petcare_web/lib/inventory.ts` = 2000 ms), last good view kept on a
  failed refresh, record-movement form sending no actor/tenant/class; Arabic default RTL.

## Tests
```
petcare_api/tests/test_inventory.py (served_app, 13): per-location visibility incl. transfer and per-product check ·
  100-event p95 visibility to a second authorised session · tenant B sees/moves nothing · owner 403 ·
  movement audited with session actor, X-Actor-Id ignored, actor/tenant/class in body 422 · balance == sum of
  movements, negative refused · no UPDATE/DELETE of stock_movement in server code (probe discriminates) ·
  non-veterinarian and lapsed-authority vet refused for POM/RESTRICTED/CONTROLLED/unregistered, refusal audited,
  live vet allowed · GENERAL/OTC handled by clinic admin
petcare_api/tests/test_inventory_postgres.py (4): second-instance read-back, balance == sum, cross-tenant refused ·
  database refuses UPDATE and DELETE (RestrictViolation) · no stored quantity/balance column ·
  sub-second check on 300,000 movements (30 locations x 1,000 products x 2 batches x 5)
petcare_web/__tests__/fr13-inventory.test.tsx (vitest, 5): interval inside bound · every location with its stock,
  Arabic RTL · change appears with no user action · failed refresh keeps view · movement body carries no identity
MEASURED (local): AC-FR-13-03 worst of 20 — per-location 22.2 ms, per-product 1.2 ms (bound 1,000 ms)
```

## Perturbations
```
P-AC01-ISO     in-memory locations() tenant filter removed      -> test_another_tenant_never_sees_or_moves… FAILS  ARMED
P-AC01-UI      page refresh interval does nothing               -> 'appears with no user action' FAILS           ARMED
P-AC02-TRIGGER immutability trigger not created                 -> test_the_database_refuses_update_and_delete… ARMED
P-AC02-AUDIT   audit actor read from X-Actor-Id header          -> test_every_movement_is_audited_with_the_session… ARMED
P-AC03-SLOW    balance query given a 1.05 s delay (pg_sleep)    -> sub-second test FAILS: 1.066 s < 1.0 false     ARMED
P-AC04-CLASS   veterinarian-only supply-class check removed     -> 4 parametrised non-veterinarian tests FAIL    ARMED
PERTURBATIONS=6 ARMED=6 VACUOUS=0   (each file restored byte-exact, sha256 checked)
```
P-AC03 is a synthetic delay: it proves the timing assertion fires at the bound; it does not claim an index removal
would cross one second at this data size (it would not).

## Binding and evidence
- bindings FR-13 (was ABSENT, 0 hits): 8 implements, 4 routes, 2 test files; fitness PERSISTENT_POSTGRES / SESSION /
  SESSION, ui_surface [/pharmacy/inventory]; `unresolved` records the COUNSEL:L-2 dependency and that product
  registration (FR-04 SFDA feed) has no served write path.
- evidence.json: AC-FR-13-01 {SERVED_APP_E2E x2, TENANT_ISOLATION: TEST · UI: ARTEFACT} · AC-FR-13-02
  {PERSISTENCE x2, AUDIT: TEST} · AC-FR-13-03 {PERSISTENCE: TEST} · AC-FR-13-04 {SERVED_APP_E2E, AUDIT: TEST x4
  parametrised ids}. No DEPENDENCY item. served_routes 47 -> 51. status regenerated by checker v1.3.
- CI: `test_inventory_postgres.py` added to the "PostgreSQL controls must not be skipped" list.
- `language-fr09.test.tsx` (FR-09 ARTEFACT) deliberately NOT edited; the page's Arabic/RTL is asserted in the FR-13
  test instead, so FR-09's registered sha256 is untouched.

## Findings
- **"Production-sized" is not defined by the BRD.** Fixed in the test module as 300,000 movements / 30 locations /
  2,000 product-batches per location, asserted on the worst of 20 runs. A production re-measurement is a PRODUCTION
  act, outside the programme.
- **"Location B's authorised user"**: the estate has no user-to-location assignment; every tenant staff session is
  authorised for every location of its tenant, which is what the test measures.
- **Supply class source.** The class is read from `product_registration` (source SFDA_REGISTRATION); nothing served
  writes it. Until FR-04's registration feed exists every product is unregistered and therefore POM —
  veterinarian-only — which is the fail-closed state AC-FR-04-03 requires.
