# U17 · FR-04 restricted-substance workflow disabled; supply class from registration — AC-FR-04-02/03 closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U17   BASE_MAIN=94405b9c2952f5216ca27a3c4e4ac0352980f881 (U16 merged, PR #61)
BRANCH=build/u17-fr04
SELECTION (pass 1): FR-04 = 3 dependency criteria, ABSENT; first of the 3-dependency FRs by id.
CRITERIA_CLOSED=[AC-FR-04-02, AC-FR-04-03]
AC-FR-04-01: internal parts evidenced (SERVED_APP_E2E, UI, AUDIT); gap = [DEPENDENCY] only — COUNSEL:EV-11.
GAPS_REMAINING={AC-FR-04-01: [DEPENDENCY] — COUNSEL:EV-11; AC-FR-04-04: [DEPENDENCY, SERVED_APP_E2E],
                AC-FR-04-05: [AUDIT, DEPENDENCY, SERVED_APP_E2E] — EXTERNAL:KYC_PROVIDER}
FR-04: ABSENT / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE (exclusively COUNSEL/EXTERNAL-gated)
```

## Defect found and fixed — a ratified criterion the earlier units did not honour
AC-FR-04-02 (dependency NONE): "until counsel resolves EV-11 and L-2, the restricted-substance workflow is disabled in
every environment and cannot be enabled by flag, admin action or configuration." U8 (FR-13), U9 (FR-14) and U13
(FR-19) let a veterinarian with a live authority receive, adjust, transfer, supply and dispense RESTRICTED/CONTROLLED
stock. Those units applied AC-FR-13-04 / AC-FR-14-02 ("veterinarian only until counsel"), which govern WHO may act;
AC-FR-04-02 is stricter (NO ONE may act) and consistent with them. Now:
- `inventory.restricted_substance_workflow_enabled()` is a constant `False` — no environment, flag, setting or admin
  record is read; nothing rebinds it (static control `test_fr04_gate_is_constant.py`).
- `_refuse_restricted_substance` is called by every served stock path — movements (receipt = register, adjustment =
  wastage, transfer), supplies, dispense — and refuses RESTRICTED/CONTROLLED for EVERY actor (403
  RESTRICTED_SUBSTANCE_WORKFLOW_DISABLED), audited with reason `RESTRICTED_SUBSTANCE_WORKFLOW_DISABLED:EV-11`.
- POM remains veterinarian-only with the prescription gate (unchanged).

## Tests changed because the requirement changed
- `test_inventory.py` AC-FR-13-04 (parametrised; registered FR-13 evidence ids unchanged): for RESTRICTED/CONTROLLED
  the veterinarian is now also refused; POM/unregistered unchanged. The criterion's own assertion (a non-veterinarian
  cannot move them) is unchanged.
- `test_fr14_prescriptions.py` AC-FR-14-03 (parametrised; ids unchanged): RESTRICTED/CONTROLLED are never supplied,
  with or without a verified prescription; POM/unregistered unchanged.
- `test_fr30_compliance.py` AC-FR-30-01: the served app can no longer create CONTROLLED movements, so the recorded
  controlled history is written at the repository layer; the report is still generated from, and traces to, it. The
  served dispense of a CONTROLLED product is asserted refused (403).

## Build (other)
- AC-03: no served route writes `product_registration` (`register_product(` absent from main.py); a class in a request
  body is 422 in any tenant; an unregistered medicine is POM (staff refused, vet allowed, supply needs a prescription);
  the class resolved at the act is audited (`RECEIPT:POM`).
- AC-01 UI: `/owner/orders` states, in the purchase flow, that restricted/controlled medicines require purchaser
  identity verification and are disabled pending EV-11.

## Evidence
AC-01 {SERVED_APP_E2E x2, AUDIT x2 (the workflow refusal tests), UI ARTEFACT fr04-restricted-notice} — DEPENDENCY not
evidenced · AC-02 {SERVED_APP_E2E x2} · AC-03 {PERSISTENCE (existing PG ledger/registration test), AUDIT,
TENANT_ISOLATION}. The static gate test is a control, not registered (it does not drive main:app, so it carries no
served_app marker). AC-04/05: no KYC adapter built.

## Perturbations
```
P-AC02-GATE-ENABLED              gate returns True                         -> workflow + static tests FAIL   ARMED
P-AC02-ENV-SWITCH                gate reads an environment variable        -> workflow test FAILS            ARMED
P-AC02-MOVEMENT-UNGATED          movements path skips the gate             -> workflow test FAILS            ARMED
P-AC02-SUPPLY-UNGATED            supplies path skips the gate              -> workflow test FAILS            ARMED
P-AC02-DISPENSE-UNGATED          dispense path skips the gate              -> workflow test FAILS            ARMED
P-AC02-UNAUDITED                 refusal audit reason lost                 -> workflow test FAILS            ARMED
P-AC03-CLASS-FROM-BODY-TOLERATED body class silently ignored, not refused  -> AC-03 test FAILS              ARMED
P-AC03-UNREGISTERED-GENERAL      unregistered treated as GENERAL           -> AC-03 test FAILS              ARMED
P-AC01-UI-NO-NOTICE              purchase flow omits the notice            -> vitest FAILS                  ARMED
PERTURBATIONS=9 ARMED=9 VACUOUS=0
```
