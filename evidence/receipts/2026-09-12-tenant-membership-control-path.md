# MyVetiCare — governed tenant-assignment control path, 2026-09-12

Durable session receipt. Where this disagrees with any summary, the repository
and the register outrank it (Rule 14).

```
RULE_13 · RULE_14 · RULE_15 · RULE_16 · RULE_17 · RULE_18 · RULE_19
```

## Heads

```
START_HEAD=6bc2f9e3638a4c3cc1e15c507ad27f68bc5c271e
PR29_STATUS=MERGED  PR29_SHA=0e3da91c9b4e32b1ee5980c6ce7ad48fed9d56f1
END_HEAD=0e3da91c9b4e32b1ee5980c6ce7ad48fed9d56f1
HARNESSONLY_MERGE_DENIAL=NO
```

## Authority

```
RULING=Sponsor, 12 September 2026, [SPONSOR]
RECORD=petcare_execution/GOVERNANCE/MVC-PREPROD-SPONSOR-DECISION-001/RATIFICATION-002.md
ITEM_2_STATUS=UNRESOLVED          PRODUCTION_TENANT_CREATION_AUTHORIZED=NO
ITEM_3_STATUS=RATIFIED            implemented by this lane
ITEM_4_STATUS=RATIFIED            INVALIDATE_ALL — no engineering required
ITEM_5_STATUS=RATIFIED            RDS PostgreSQL 16 — no engineering required
ITEM_6  GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
P1_AUTHORIZED=NO
```

## Delivered

```
GOVERNED_PATH=petcare_api/tenant_membership.py
ROUTES=POST /api/admin/identities/{user_id}/tenant   assign · reassign · revoke
       GET  /api/admin/identities/{user_id}/tenant   readback
AUTHORITY=platform_admin, from the validated session
ROLE_PARAMETER=ABSENT             extra="forbid" rejects a smuggled one with 422
AUDIT_MODEL=TWO_EVENT             removal scoped to the tenant left,
                                  addition scoped to the tenant joined
GOVERNED_FIELD_SET=UNCHANGED (12) no previous_tenant_id, no encoding in reason_code
TENANT_VALIDATION=REGISTRY        unknown and disabled are ONE answer
ATOMICITY=ONE TRANSACTION         armed by induced failure
DIRECT_REPOSITORY_ACCESS=PROVEN NOT AN AUTHORIZED SERVING PATH
NON_DURABLE_STORE=REFUSED (503)   authorization is checked FIRST, so the refusal
                                  never leaks the store's configuration
```

All twelve authorized proof points are mapped to named controls in
`MVC-TENANT-MEMBERSHIP/20260912T140000Z/TENANT_MEMBERSHIP_SERVICE.md`.

## Regression

```
ROOT      242 · RUNTIME 247 · API 353 · COMPOSITE 842      (baseline 802)
242 + 247 + 353 = 842 — the per-suite sum check
POSTGRES  7 suites, 142 controls
PERTURBATIONS=6, MARKER 6/6, DIFF 6/6, FAILED_AS_REQUIRED 6/6, RESTORED 6/6
ASSERTIONS_WEAKENED=0  CONTROLS_REMOVED=0  CONTROLS_STRENGTHENED=1
CI on #29: 835 passed + 7 pre-existing skips = 842; web 120; responsive 90
```

## Findings

```
1  The body-tenant guard fired on the new route. A TRUE NEW CASE, not a defect:
   require_tenant() answers "which tenant may THIS CALLER act on", and a
   platform_admin administering across tenants is authorised to act outside its
   own scope. The guard now resolves the enclosing route by AST and demands
   either tenant-scope authorization or a NAMED, BOUND administrative authority.
2  The CI non-skip step fell behind a THIRD time. Converted from a habit into a
   control: tests/governance/test_ci_postgres_coverage.py asserts every
   `test_*postgres*.py` suite is named in the step.
3  Two of this lane's own tests were wrong and were caught by running them: a
   write-detector that matched local variable reads, and an oracle assertion that
   compared refusal strings literally when they legitimately differ by the id the
   caller supplied.
```

## Boundary

```
PRODUCTION_MUTATED=NO         LIVE_DB_MUTATED=NO
PRODUCTION_TENANT_CREATED=NO  PRODUCTION_IDENTITY_CREATED=NO
SECRET_CREATED=NO             CLOUD_RESOURCE_TOUCHED=NO
SYNTHETIC_FIXTURES_ONLY=YES   they acquire no production authority
```

## Open

```
ITEM_2  the first production tenant             UNRESOLVED — Sponsor
ITEM_6  GITHUB_SUPPORT_REFS_PULL_1_6            NOT_SENT — open, not closed
        ARCH-01 signatures / anchoring          OPEN
        AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN         OPEN
        PRE-2D pharmacy surface disposition     OPEN
        PILOT_INVITE_CODES_ARE_PUBLIC_LITERALS  OPEN
NEXT_GENUINE_GATE=GATE_LIVE_APPLY (P1 — provision the database)
```
