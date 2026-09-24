# U1 · AC-FR-02-04 — POST /api/pets audit actor from session, 2026-09-24

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U1   BASE_MAIN=899c5395ac6461a6fc901cdc919fbad46f19d4a9 (U0 merged)
BRANCH=build/u1-fr02-ac04-audit-actor   AUTHORITY=MVC-ACCEPT-PACK-P1 I-02
CRITERIA_CLOSED=[AC-FR-02-04]
```

## Criterion (ratified, verbatim)
- statement: "Every profile create and change is attributed in the audit chain to the session actor."
- fails_if: "a profile mutation is written with a client-supplied actor or without an audit event."
- evidence: [AUDIT, SERVED_APP_E2E] · dependency: NONE · disposition: ACCEPT
- ratified_text (I-02): "Current failure on POST /api/pets is implementation debt and MUST be remediated against this criterion. It does not weaken the criterion."

## Defect and fix (Rule 21: remove, don't validate)
BEFORE `petcare_api/main.py` create_pet took `x_actor_id: str = Header(...)` and wrote it as `actor_id` and the
role as `actor_role` in `_audit` (base lines 1209, 1222). AFTER the header parameter is removed; `actor_id,
actor_role = _actor(request)` (main.py:1222) — the PR #38 derivation from the signed session — and the tenant
from `require_tenant` once. A client-sent X-Actor-Id has no effect. No other pets behaviour changed.

## Tests — petcare_api/tests/test_pet_audit_actor.py (module-marked served_app; all through main.app)
```
E1 test_e1_client_supplied_actor_has_no_effect_on_audit_record        A claims actor B -> audit actor A, role owner   PASS
E2 test_e2_audit_record_is_in_session_tenant_and_invisible_to_other_tenant  audit tenant = A; tenant-B session sees none PASS
E3 test_e3_unauthenticated_create_is_rejected_and_writes_no_audit     401, audit count unchanged                     PASS
E4 test_e4_create_without_actor_header_succeeds_and_is_audited        header no longer required; audited as session   PASS
served_app collection: 4/4
PERTURBATION: create_pet actor restored to the client X-Actor-Id header -> E1 FAILED -> revert -> PASSED   ARMED
```

## Binding and evidence
- `requirements/bindings.json` FR-02: tests += test_pet_audit_actor.py (basis :58); fitness.audit_actor_source
  CLIENT_SUPPLIED -> SESSION (basis main.py:1222). Nothing else in FR-02 changed.
- `requirements/acceptance/evidence.json` AC-FR-02-04: AUDIT (TEST E1), SERVED_APP_E2E (TEST E1, served_app).

## Status (tools/check_register.py)
```
FR-02: REACHABLE_UNTESTED / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE
AC-FR-02-04 GAP: [AUDIT, SERVED_APP_E2E] -> []
REMAINING FR-02 GAPS (scope of the next FR-02 unit):
  AC-FR-02-01 [PERSISTENCE, SERVED_APP_E2E, TENANT_ISOLATION, UI]
  AC-FR-02-02 [ARABIC_RTL, SERVED_APP_E2E, UI]
  AC-FR-02-03 [PERSISTENCE]
M4: no FR engineering status lowered; ACCEPTED=0
```

## Results
```
REGRESSION_LOCAL=980 passed / 0 skipped
SCANNERS: SECRET_SCAN=CLEAN · ACTIVE_LITERAL_DEFAULT=0 · DIFF_CHECK=CLEAN · status.json current
M3: product main.py, one new test file, bindings.json, evidence.json, status.json, new receipt, ledger append
```

## Findings
- FR-02 `unresolved` text in bindings.json still says "No test exercises POST /api/pets"; now stale. Left
  unedited (unit scope limited binding edits to tests/fitness); correct it in the next FR-02 unit.
