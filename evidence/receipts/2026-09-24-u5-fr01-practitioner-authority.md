# U5 · FR-01 — AC-FR-01-02: regulated acts need a live practitioner authority attribute, 2026-09-24

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U5   BASE_MAIN=770117f96b4e0bc6184d3257175d55fd1be222eb (U4 merged)
BRANCH=build/u5-fr01-practitioner-authority   SELECTION: FR-01 still has a closable gap (ordering unchanged)
CRITERIA_CLOSED=[AC-FR-01-02]
GAPS_REMAINING: AC-FR-01-03 (SPONSOR_QUEUE SQ-1) · AC-FR-01-04 (COUNSEL:L-2)
FR-01: REACHABLE_TESTED / EVIDENCE_INCOMPLETE (2 of 4 criteria evidenced)
```

## Criterion (ratified)
"Every regulated act (prescribing, dispensing) is authorised by a live practitioner authority attribute evaluated at
the moment of the act, in addition to role and tenant membership." Fails if "any permission check resolves a
regulated act from a role, group, permission string or token claim without reading a live authority attribute."

## Build
- Migration `0039_fr01_practitioner_authority.sql` (additive): `practitioner_authority_grant` — tenant- and
  identity-FK'd, professional_class {VETERINARIAN}, licence_ref, effective_from, expires_at, revoked_at (+ by).
- `petcare_api/practitioners.py`: time-bounded grant (`held_at(when)`), `evaluate()` → grant in force or the reason
  ("no authority granted" / "revoked at …" / "expired at …" / "not yet effective"); tenant-checked in-memory repo;
  `PostgresPractitionerAuthorityRepository` (conditional revoke UPDATE; double revoke refused).
- Enforcement: `issue_prescription`, `verify_prescription`, `dispense_prescription` keep the role check AND call
  `_require_practitioner_authority(actor, tenant)` at the act; refusal is 403 `PRACTITIONER_AUTHORITY_REQUIRED` naming
  the attribute and why (REQ-MVC-8.38); the success audit event carries `reason_code=authority:<grant_id>`.
- Governed administration (never self-service): `POST /api/admin/practitioners/{user_id}/authority` (platform_admin,
  target must be a veterinarian in the session tenant, self-grant refused), `POST …/authority/{grant_id}/revoke`,
  `GET /api/practitioners/me/authority`. Grant and revoke are audited as the session actor.

## Tests
```
petcare_api/tests/test_practitioner_authority.py (served_app, 6): role alone refused, refusal names the attribute ·
  grant in force permits and the audit records the grant · revocation applies at the next act · expired grant refused
  naming expiry · other-tenant grant confers nothing · admin-only, never self-granted, only veterinarians
petcare_api/tests/test_practitioner_authority_postgres.py (2): grant + revocation durable across instances; invalid
  class / unknown identity / double revoke refused
PERTURBATION: issue_prescription with the authority check removed (role alone) -> role-alone test FAILS -> revert
  -> PASSES   ARMED
```

## Fixture changes (disclosed)
Existing suites that prescribe/dispense as a veterinarian now grant authority explicitly through
`tenant_fixtures.grant_practitioner_authority` (option A workflow, dispensing fail-closed, pet profile history,
PostgreSQL served-app suite — which also swaps `PRACTITIONER_REPO` to its PostgreSQL persistence). No assertion was
changed; T-DISP-01..08 pass unchanged.

## Binding and evidence
- bindings FR-01: +7 implements, +3 routes, +2 test files, basis lines. evidence.json AC-FR-01-02:
  SERVED_APP_E2E (TEST role-alone refusal) · AUDIT (TEST grant recorded on the act's audit event).
- served_routes.json regenerated: 40 → 43.

## Results
```
REGRESSION_LOCAL=1015 passed / 0 skipped · M4: no FR lowered; ACCEPTED=[FR-02]
SCANNERS: SECRET_SCAN=CLEAN · ACTIVE_LITERAL_DEFAULT=0 · DIFF_CHECK=CLEAN
CI config: verify.yml PostgreSQL list += test_practitioner_authority_postgres.py
```

## Findings
- **Operational consequence (by design).** After merge, a veterinarian cannot prescribe, verify or dispense until a
  platform admin records a VETERINARIAN authority grant for them. No UI exists for grant administration yet (API
  only); any environment with existing vets needs grants recorded before use. Production is not live.
- `professional_class` is closed to VETERINARIAN; pharmacy-class authority is AC-FR-01-04 (COUNSEL:L-2).
