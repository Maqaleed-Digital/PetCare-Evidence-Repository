# RATIFICATION-003 — first production tenant (identity only)

**Resolves:** board item 2 · **Ruling date:** 12 September 2026
**Lodged:** 2026-09-12 · **Actor tag:** `[SPONSOR]`
**Base at lodgement:** `1531d2c79df67368a910d4681d376be0e9eab794`

## Outcome

```
ITEM_2_STATUS=RESOLVED
ITEM_2_TENANT_ID=pharmacare_riyadh
ITEM_2_DISPLAY_NAME=Pharma Care Pharmacies — Riyadh

AUTHORITY_ESTABLISHED=IDENTITY_AND_NAMING_ONLY
PRODUCTION_TENANT_ROW_CREATED=NO
PRODUCTION_TENANT_CREATION_AUTHORIZED=NO
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
```

## The ruling, verbatim

> ```
> [SPONSOR RULING — MYVETICARE FIRST PRODUCTION TENANT]
>
> I approve Pharma Care Pharmacies (Riyadh) as the first production tenant of
> MyVetiCare.
>
> tenant_id = pharmacare_riyadh
> display_name = Pharma Care Pharmacies — Riyadh
>
> This establishes the governed identity of the first production tenant.
>
> This ruling does not itself authorize creation of the tenant row, provisioning
> of production infrastructure, application of migrations, production credential
> entry, production identity creation, or cutover.
>
> P1_AUTHORIZED=NO
> GATE_LIVE_APPLY=NOT_AUTHORIZED
>
> Date: 12 September 2026
> [SPONSOR]
> ```

## Naming authority is not creation authority

The ruling draws the line itself, and it is worth restating because it is easy
to state and easy to lose. The identifier is now written down in a governance
record, and the shortest path from *written down* to *created* is somebody adding
one `INSERT` to a migration during a cutover window.

Closing that path is an engineering act this lane performed:
`tests/governance/test_production_tenant_not_created.py` asserts that

- **no migration creates a tenant row** — scoped to migrations, because a
  migration's `INSERT` creates a row the moment the chain is applied, with no
  actor, no authorization and no audit event;
- **the ruled identifier appears in no creating code** — not in a migration, a
  constant, a default or a fixture, even outside an `INSERT`;
- **the governed creation mechanism still exists** — `PostgresTenantRepository.create`
  contains an `INSERT INTO tenant` and must, because a future authorized act
  needs something to call. The distinction is between code that CAN create a
  tenant and a row that IS created;
- **the ruling is recorded in governance** — a guard that only forbade would be
  satisfied by the identifier existing nowhere at all, including in the record
  that ratifies it.

Three meta-tests plant each case, including that this repository's real
migration `0034` — which discusses tenants it declines to invent, at length, in
comments — keeps passing.

## What creating the row will require

The governed sequence, when authorized:

```
GATE_LIVE_APPLY          provision the database          (P1)
GATE_CREDENTIAL_ENTRY    create the session secret       (P2)
GATE_LIVE_APPLY          apply the migration chain       (P3)
GATE_LIVE_APPLY          create the tenant row           (P5.0)
                         PostgresTenantRepository.create, or the equivalent
                         governed act — never a migration INSERT
```

Membership is then assigned through the governed path built under
`RATIFICATION-002` — `POST /api/admin/identities/{user_id}/tenant` — which
produces the two-event audit record. Direct repository access remains not an
authorized operating path for membership.

## Board after this lodgement

```
ITEM_1=RESOLVED                     PRE-1 / PRE-2 / pharmacy, RATIFICATION-001
ITEM_2=RESOLVED                     this record — identity only
ITEM_3=RATIFIED_BUILT_PROVEN        RATIFICATION-002 + MVC-TENANT-MEMBERSHIP
ITEM_4=RATIFIED_INVALIDATE_ALL      RATIFICATION-002
ITEM_5=RATIFIED_RDS_POSTGRESQL_16   RATIFICATION-002
ITEM_6=NOT_SENT                     GitHub Support refs/pull/1-6 — OPEN
```

`ITEM_6` is not closed and must not be represented as closed. It does not block
this pre-P1 lane and is carried as a pre-final-release residual.
