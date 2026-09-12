# RATIFICATION-004 — first production `platform_admin` genesis authority

**Ratifies:** the blocking finding `FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY=UNRULED`
**Date of ruling:** 12 September 2026 · **Actor tag:** `[SPONSOR]`
**Reference:** `MVC-GENESIS-PLATFORM-ADMIN-001`
**Relation to RATIFICATION-002:** narrows nothing and relaxes nothing. Item 3's
withholding of role-creation and role-elevation authority stands; this ruling
creates one single-use exception to it and says so explicitly.

## Outcome

```
GENESIS_AUTHORITY=SINGLE_USE
GENERAL_PLATFORM_ADMIN_ELEVATION_AUTHORITY=NOT_AUTHORIZED
GENESIS_AUDIT_ACTOR=UNATTRIBUTED_OR_GOVERNED_SYSTEM_GENESIS
INVENTED_ACTOR=PROHIBITED
GENESIS_REUSE=PROHIBITED
SECOND_GENESIS_ATTEMPT=MUST_FAIL_CLOSED

PRODUCTION_GENESIS_EXECUTION=NOT_AUTHORIZED_BY_THIS_RULING
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
```

## The deadlock this resolves

`RATIFICATION-002` item 3 made `platform_admin` the sole role permitted to
administer tenant membership, and withheld every authority that could create or
elevate one. The estate has no other route to that role: registration is
invite-gated and mints `owner` or `veterinarian` only, `PRE1_RULING=1-B`
discarded the three seed identities, and startup creates none.

Production therefore had no authorized way to obtain its first administrator, so
nobody could ever be assigned to `pharmacare_riyadh` — recorded as the blocking
finding `FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY=UNRULED`. That finding is now
closed. It blocked plan Phase F, never B–D.

## Where implementation had to resolve the ruling's text

Recorded because these are readings, not restatements, and a later reader is
entitled to see which way they went and why.

| | Question | Resolution |
|---|---|---|
| Tenant context | §3 permits *"the tenant context required by the governed production identity model"* | **ABSENT.** The governed model represents platform scope as the absence of a tenant plus an explicit role, never as a tenant standing for everyone (TENANT-04/TENANT-09, `petcare_api/tenants.py`). Sponsor-selected 12 Sep. |
| Why not `pharmacare_riyadh` | §3 names the ruled first production tenant | Migration 0034 puts an FK from `user_identity.tenant_id` onto `tenant`. Binding the administrator to it would require creating that row first — a production tenant-row creation §9 withholds — making genesis ordering-dependent on an unauthorized act. |
| Genesis event tenant | `audit_event.tenant_id` is `TEXT NOT NULL` | `UNATTRIBUTED`, the representation the estate already uses for a governed event with no tenant perimeter. 0034 deliberately puts no FK on that column precisely so no fake tenant row is needed. |
| Genesis actor | §4 requires an unattributed/system-capable actor, `INVENTED_ACTOR=PROHIBITED` | `actor_id` and `actor_role` are both `UNATTRIBUTED`. Neither is a member of `ALLOWED_ROLES`, so no authorization decision can match them. Naming the new administrator as the actor was rejected: it would read as though they authorized their own creation. |
| Resulting role in the record | §4 requires the record to identify the resulting role; the governed field set may not be widened | Carried by the event **name** — `platform_admin.genesis` — which is governed representation, and by `platform_admin_genesis.granted_role`, CHECK-constrained to the single value. No field was added, and nothing is encoded in `reason_code` beyond the ruling reference. |
| Provenance | none of the three existing origins describes this identity | A fourth, `GENESIS` (migration 0035). Recording the first administrator as `SEED` would file them with the development artefacts PRE-1 discarded. |

## What was built, and what was not

```
GENESIS_NON_PRODUCTION_IMPLEMENTATION=COMPLETE
PRODUCTION_GENESIS_EXECUTED=NO
GENESIS_CONSUMED=NO
```

Built under §8:

* `petcare_runtime/migrations/0035_genesis_platform_admin.sql` — `GENESIS`
  provenance, a unique index admitting at most one `GENESIS` identity, and the
  `platform_admin_genesis` consumption record with a singleton primary key.
  **Creates no identity and consumes no authority.**
* `petcare_api/platform_admin_genesis.py` — the governed procedure. No role
  parameter; `INSERT` only, never `UPDATE` and never an upsert, so no existing
  identity can be elevated; one transaction carrying the identity, the governed
  audit event and the consumption record together.
* `scripts/governance/platform_admin_genesis.py` — the operator entry point,
  with a read-only `--check` mode. Not a route: §7 withholds a reusable
  bootstrap endpoint.
* `petcare_api/tests/test_platform_admin_genesis_postgres.py` — 18 controls on
  real PostgreSQL.
* `tests/governance/test_platform_admin_genesis_authority.py` — the guards over
  §2/§5/§7's prohibitions, each with a meta-test proving it fires.

Not built, because the ruling withholds it: the production genesis write, the
production identity, the production credential, and any second or replacement
`platform_admin`.

## The ruling, verbatim

> ```
> [SPONSOR RULING — MYVETICARE FIRST PLATFORM ADMINISTRATOR GENESIS AUTHORITY]
>
> Date: 12 September 2026
>
> I authorize a single-use genesis act to establish the first production
> `platform_admin` for MyVetiCare.
>
> This authority exists only because the governed production system requires an
> existing `platform_admin` before tenant membership can be administered, while
> all ordinary role-creation and role-elevation authority remains separately
> governed.
>
> ## 1 — PURPOSE
>
> The genesis act is authorized solely to establish the first governed production
> `platform_admin` required to commence administration of the MyVetiCare
> production environment.
>
> This ruling does not establish a general privilege-management authority.
>
> GENESIS_AUTHORITY=SINGLE_USE
> GENERAL_PLATFORM_ADMIN_ELEVATION_AUTHORITY=NOT_AUTHORIZED
>
> ## 2 — FIRST PRODUCTION PLATFORM ADMINISTRATOR
>
> The first production `platform_admin` must be created through a dedicated
> genesis procedure.
>
> The procedure must not accept an arbitrary role parameter.
>
> Its resulting role is fixed by the governed procedure to:
>
> `platform_admin`
>
> The genesis procedure must not be capable of creating any other privileged role
> or of elevating an existing identity to another role.
>
> The actual human identity and production authentication credential for the
> first platform administrator remain subject to the production identity and
> credential-entry gates.
>
> This ruling does not authorize inventing, embedding, or storing a default
> credential.
>
> ## 3 — TENANT CONTEXT
>
> The first production tenant is already ruled as:
>
> tenant_id = `pharmacare_riyadh`
> display_name = `Pharma Care Pharmacies — Riyadh`
>
> The genesis procedure may establish the first platform administrator with the
> tenant context required by the governed production identity model, but must not
> create any additional tenant or infer any tenant value.
>
> ## 4 — GENESIS AUDIT
>
> Because no governed production administrator exists before the genesis act, the
> genesis event has no prior governed human actor.
>
> The genesis operation must therefore be recorded explicitly as a genesis/system
> event using the governed audit model's existing unattributed/system-capable
> representation.
>
> The audit record must clearly identify:
>
> * that the event is a first-platform-administrator genesis event;
> * the target identity;
> * the resulting `platform_admin` role;
> * the relevant production tenant context;
> * the governing Sponsor ruling;
> * the execution timestamp;
> * the result of the genesis operation.
>
> The absence of a prior human actor must not be disguised by inventing an actor
> identity.
>
> GENESIS_AUDIT_ACTOR=UNATTRIBUTED_OR_GOVERNED_SYSTEM_GENESIS
> INVENTED_ACTOR=PROHIBITED
>
> ## 5 — SINGLE-USE PROPERTY
>
> The genesis authority must be consumable exactly once.
>
> Before execution, the procedure must prove that no governed production
> `platform_admin` already exists and that the genesis authority has not
> previously been consumed.
>
> After successful execution:
>
> * the genesis authority is marked consumed;
> * the genesis path becomes unavailable for subsequent use;
> * a second invocation must fail closed;
> * the system must verify that the intended first platform administrator exists;
> * no additional privileged identity may have been created by the genesis
>   operation.
>
> GENESIS_REUSE=PROHIBITED
> SECOND_GENESIS_ATTEMPT=MUST_FAIL_CLOSED
>
> The single-use property must be enforced by durable production state, not by
> operator memory or documentation alone.
>
> ## 6 — TRANSACTION AND FAILURE SEMANTICS
>
> The genesis operation must be atomic with its required durable audit evidence.
>
> A failure must not leave:
>
> * a privileged identity without the corresponding governed genesis audit
>   record; or
> * a genesis audit record claiming creation of an administrator that was not
>   created.
>
> If any required persistence, validation, or audit step fails, the entire
> genesis operation must fail closed.
>
> ## 7 — STEADY-STATE AUTHORITY AFTER GENESIS
>
> Once the first production `platform_admin` exists, all ordinary
> tenant-membership administration proceeds through the already ratified governed
> tenant-assignment control path.
>
> This ruling does not authorize:
>
> * creation of a second `platform_admin`;
> * elevation of another identity to `platform_admin`;
> * arbitrary role modification;
> * a reusable bootstrap endpoint;
> * direct database privilege writes as an operating procedure;
> * seed identities;
> * default administrator credentials.
>
> Any later creation, replacement, or elevation of a `platform_admin` requires a
> separate privilege-management authority unless separately ratified in the
> future.
>
> ## 8 — IMPLEMENTATION AUTHORITY
>
> This ruling authorizes non-production implementation and verification of the
> single-use genesis mechanism.
>
> It also authorizes preparation of the exact production genesis step for
> inclusion in the P1/cutover runbook.
>
> It does NOT by itself authorize execution of the production genesis write.
>
> PRODUCTION_GENESIS_EXECUTION=NOT_AUTHORIZED_BY_THIS_RULING
>
> ## 9 — PRODUCTION BOUNDARIES
>
> This ruling does not authorize:
>
> * RDS provisioning;
> * production schema application;
> * production secret entry;
> * production tenant-row creation;
> * production identity creation;
> * execution of the production genesis act;
> * serving binding;
> * cutover;
> * irreversible production action.
>
> P1_AUTHORIZED=NO
> GATE_LIVE_APPLY=NOT_AUTHORIZED
> GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
>
> [SPONSOR]
> ```

## What remains open

`PRODUCTION_TENANT_ROW_CREATED=NO` is unchanged and unaffected — the first
administrator holds no tenant, so genesis does not depend on it. Assigning any
identity to `pharmacare_riyadh` still requires that row, and creating it remains
a separate Sponsor act (`RATIFICATION-003` ruled the identity only).

The P1 runbook step is prepared under §8 at
`../MVC-P1-PRODUCTION-ACTIVATION/P1_GENESIS_STEP-001.md`. It is a prepared step,
not an authorization: executing it is `GATE_LIVE_APPLY` plus
`GATE_CREDENTIAL_ENTRY`, and both are `NOT_AUTHORIZED`.
