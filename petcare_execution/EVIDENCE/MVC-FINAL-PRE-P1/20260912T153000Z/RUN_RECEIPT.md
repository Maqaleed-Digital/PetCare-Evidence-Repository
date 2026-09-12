# MyVetiCare — final pre-P1 readiness, 2026-09-12

```
START_SHA=1531d2c79df67368a910d4681d376be0e9eab794
BASE_VERIFIED=origin/main was exactly the handoff SHA; no intervening commits
WORKING_TREE=CLEAN at lane start
```

## Board

```
ITEM_1=RESOLVED                      RATIFICATION-001
ITEM_2=RESOLVED                      RATIFICATION-003
ITEM_2_TENANT_ID=pharmacare_riyadh
ITEM_2_DISPLAY_NAME=Pharma Care Pharmacies — Riyadh
ITEM_3=RATIFIED_BUILT_PROVEN         RATIFICATION-002 + MVC-TENANT-MEMBERSHIP
ITEM_4=RATIFIED_INVALIDATE_ALL       RATIFICATION-002
ITEM_5=RATIFIED_RDS_POSTGRESQL_16    RATIFICATION-002
ITEM_6=NOT_SENT                      GitHub Support refs/pull/1-6 — OPEN
```

## The three negatives, proven from live source

```
PRODUCTION_TENANT_ROW_CREATED=NO
  migration 0034 contains 0 INSERTs; `pharmacare_riyadh` appears in no tracked
  file before this lane; no production database exists to hold a row
P1_AUTHORIZED=NO
LIVE_SCHEMA_APPLIED=NO
PRODUCTION_SECRETS_ENTERED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
```

## What this lane added

Naming authority is not creation authority, and that distinction is now a
control rather than a sentence.
`tests/governance/test_production_tenant_not_created.py` asserts:

- no **migration** creates a tenant row — scoped to migrations, because a
  migration's `INSERT` creates the row the moment the chain is applied, with no
  actor, no authorization and no audit event;
- the ruled identifier appears in no creating code — not as a constant, a
  default or a fixture, even outside an `INSERT`;
- the governed creation **mechanism** still exists — `PostgresTenantRepository.create`
  contains an `INSERT INTO tenant` and must, because a future authorized act
  needs something to call;
- the ruling **is** recorded in governance — a guard that only forbade would be
  satisfied by the identifier existing nowhere at all.

The first draft of that guard was too broad: it flagged the repository's
parameterised `create`. A guard that forbids the mechanism forbids the registry
from ever being used, and would be deleted the first time somebody needed it.
The line is between code that CAN create a tenant and a row that IS created.

## Regression

```
ROOT      pytest tests                  246 passed
RUNTIME   pytest petcare_runtime/tests  247 passed
API       pytest petcare_api/tests      353 passed
COMPOSITE the CI command                846 passed
246 + 247 + 353 = 846 — the per-suite sum check

POSTGRESQL  142 passed across 7 suites (ephemeral local PostgreSQL 16.11)
            LIVE_DB_TOUCHED=NO

prohibited_literal  SCANNED=402  ACTIVE_LITERAL_DEFAULT=0
secret_scan         SCANNED=3938 FINDINGS=0  CLEAN
evidence bundles    BUNDLES=30  ARTEFACTS=206  FAILED=0

PERTURBATIONS=3, all proven applied, all restored, 0 vacuous
ASSERTIONS_WEAKENED=0
```

## AWS

```
READ_ONLY_AWS_DISCOVERY=NOT_AVAILABLE
  aws-cli/2.34.18 is installed; no profile, access key, secret key or region is
  configured. No credentials were requested and none were entered.
```

Consequence, recorded rather than worked around: no account, VPC, subnet,
security-group, KMS or endpoint identifier could be read, so every such value in
the P1 plan is an `<INPUT_REQUIRED>` rather than a decision. Nothing was invented.

## A finding that blocks a later phase

```
FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY=UNRULED
```

Found while writing Phase F of the plan. Assigning tenant membership requires an
existing `platform_admin`; creating or elevating one is *"a separate
privilege-management authority"* that `RATIFICATION-002` does not authorize; seed
identities are discarded and registration establishes no elevated role.

The production system as ruled therefore has no authorized way to obtain its
first `platform_admin`, and so no way to assign the first identity to
`pharmacare_riyadh`.

It does **not** block Phases B–D, which is all the authorization request covers.
It blocks Phase F, and it should be ruled before the window rather than inside it.

## Deliverables

```
P1_PLAN=petcare_execution/GOVERNANCE/MVC-P1-PRODUCTION-ACTIVATION/P1_ACTIVATION_PLAN-001.md
P1_PLAN_SHA256=54157317830c767478db3ec6a2135d0e35e6aedaf5aa1660caf755889f190805
P1_AUTHORIZATION_REQUEST=petcare_execution/GOVERNANCE/MVC-P1-PRODUCTION-ACTIVATION/P1_AUTHORIZATION_REQUEST-001.md
PRODUCTION_READINESS=READY_PENDING_LIVE_GATE
FIRST_LIVE_MUTATION=plan Phase B.1 (aws rds create-db-instance)
CREDENTIAL_ENTRY_GATE=plan Phase C.2 (create the session signing secret)
```

## Notion-ready update

> **MyVetiCare — Final Pre-P1 Readiness**
>
> **Item 2 ratified.** First production tenant: *Pharma Care Pharmacies
> (Riyadh)* — `tenant_id = pharmacare_riyadh`. Identity only; the row is not
> created and creating it is not authorized.
>
> **Board items 1–5 resolved.** Seed identities discarded, canonical machine
> role authority, pharmacy role removed with capabilities retained, tenant
> registry, `INVALIDATE_ALL` session policy, RDS PostgreSQL 16.
>
> **Tenant-membership path built and proven** — `platform_admin` only,
> cross-tenant, two-event audit, no role parameter, one transaction. 39 controls,
> 6 perturbations.
>
> **Current main:** `1531d2c` (this lane merges on top).
> **Regression:** 846 passed; 142 PostgreSQL controls; scanners clean.
>
> **`P1_AUTHORIZED=NO`. Next gate: `GATE_LIVE_APPLY`** — provision the
> production database. The P1 plan and the authorization request are prepared and
> unexecuted.
>
> **Open:** GitHub Support `refs/pull/1–6` still `NOT_SENT`. The first
> `platform_admin` bootstrap authority is unruled and blocks Phase F.

*(No Notion action was performed. This is the block to paste.)*

## Boundary

```
PRODUCTION_MUTATED=NO        LIVE_DB_MUTATED=NO
CLOUD_RESOURCE_TOUCHED=NO    EXTERNAL_DASHBOARD_MUTATED=NO
SECRET_CREATED=NO            TENANT_ROW_CREATED=NO
IDENTITY_CREATED=NO          MIGRATION_APPLIED_TO_PRODUCTION=NO
```
