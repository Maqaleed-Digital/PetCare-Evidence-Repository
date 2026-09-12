# RATIFICATION-002 — final pre-production policy

**Ratifies:** board items 3, 4, 5 · **Item 2:** explicitly NOT ruled
**Date of ruling:** 12 September 2026 · **Actor tag:** `[SPONSOR]`
**Base at recording:** `6bc2f9e3638a4c3cc1e15c507ad27f68bc5c271e`
**Supersedes as the operative record:** `FINAL_PREPROD_POLICY-PROPOSED.md`
(kept as the draft that was put forward; where the two differ, this governs)

## Outcome

```
ITEM_2_STATUS=UNRESOLVED
PRODUCTION_TENANT_CREATION_AUTHORIZED=NO

ITEM_3_STATUS=RATIFIED
TENANT_ASSIGNMENT_AUTHORITY=platform_admin
CROSS_TENANT_ASSIGNMENT=AUTHORIZED
TENANT_ROLE_COUPLING=PROHIBITED
TENANT_ASSIGNMENT_ROLE_PARAMETER=ABSENT
AUDIT_MODEL=TWO_EVENT
SECOND_PARTY_APPROVAL=NOT_REQUIRED_FOR_ORDINARY_TENANT_MEMBERSHIP

ITEM_4_STATUS=RATIFIED
PRE4_SESSION_POLICY=INVALIDATE_ALL
PREVIOUS_KEY_ACCEPTANCE_LIST=NOT_AUTHORIZED
AC7_ROTATION_REVOCATION_PROPERTY=MUST_BE_PRESERVED

ITEM_5_STATUS=RATIFIED
ENGINE_VARIANT=RDS_POSTGRESQL
POSTGRESQL_MAJOR_VERSION=16

ITEM_6  GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT

P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
GATE_IRREVERSIBLE_ACTION=NOT_AUTHORIZED
```

## Where the ruling differs from the draft that was proposed

Recorded because the differences are substantive, not editorial.

| | Proposed | Ruled |
|---|---|---|
| Item 2 | fields left blank, awaiting values | **explicitly NO RULING** — the absence is itself a decision, and it does not block the authorized lane |
| Audit model | (a) two events, recommended | **selected**, and the field set is forbidden from being widened for it |
| `reason_code` | recommended against encoding old→new | **prohibited** — no structured state in an unvalidated field as a substitute for governed representation |
| Role parameter | "must not accept a role as an input" | same, plus *"must not create, modify, elevate, downgrade, or otherwise change"* — downgrade named as well as elevation |
| Direct repository access | implied | **stated**: "Direct repository access is not an authorized operating path" |
| Engine | RDS PostgreSQL 16 | same, plus a constraint: must not introduce RDS-specific semantics that would defeat D.21 portability |

## The ruling, verbatim

> ```
> [SPONSOR RULING — MYVETICARE FINAL PRE-PRODUCTION POLICY]
>
> Date: 12 September 2026
>
> ## ITEM 2 — FIRST PRODUCTION TENANT
>
> NO RULING AT THIS TIME.
>
> The first production tenant remains unresolved.
>
> No tenant identifier or display name may be invented, inferred, promoted from
> test fixtures, derived from geography, email address, role, application
> defaults, or otherwise created without explicit Sponsor authority.
>
> The absence of a production tenant does not block the non-production
> implementation and verification authorized below.
>
> ## ITEM 3 — TENANT-ASSIGNMENT AUTHORITY AND CONTROL PATH
>
> I authorize `platform_admin` as the sole actor role permitted to assign,
> change, or revoke tenant membership under the initial MyVetiCare operating
> model. A `platform_admin` may administer tenant membership across tenants.
>
> Tenant assignment and role assignment are separate authorities. The governed
> tenant-assignment control path must not accept a role as an input and must not
> create, modify, elevate, downgrade, or otherwise change an identity's role.
>
> TENANT_ASSIGNMENT != ROLE_ASSIGNMENT
>
> In particular, the tenant-assignment path must not grant `platform_admin`.
> Creation of, or elevation to, `platform_admin` is a separate
> privilege-management authority and is not authorized by this ruling.
>
> Every tenant assignment, reassignment, and revocation must pass through a
> governed service/API path that authenticates the acting identity; verifies the
> required `platform_admin` authority; identifies the target identity explicitly;
> validates every destination tenant against the governed tenant registry;
> refuses unknown or disabled tenants; performs the durable identity update;
> records the membership change in the governed audit system; provides a
> verification/readback path; provides a governed revocation path; and fails
> closed if authorization, tenant validation, audit persistence, or identity
> persistence cannot be established.
>
> Direct repository access is not an authorized operating path.
>
> I select the two-event audit model. A reassignment from Tenant A to Tenant B
> must produce a removal event scoped to Tenant A and an addition event scoped to
> Tenant B, so that each tenant's own governed audit history records the change
> to its own perimeter. A revocation produces the removal event only; a
> first-time assignment produces the addition event only.
>
> The existing governed audit-event field set is not to be widened solely for
> this requirement. No `previous_tenant_id` field is authorized. No structured
> old-to-new tenant state may be hidden inside an unvalidated free-text or reason
> field as a substitute for governed representation. The existing audit-chain
> semantics and governed event field set are to remain intact unless separately
> authorized.
>
> No second-party approval is required for ordinary tenant-membership assignment,
> reassignment, or revocation under this initial operating model. This ruling
> does not authorize role elevation or other privilege administration.
>
> ## ITEM 4 — PRE-4 SESSION POLICY
>
> PRE4_SESSION_POLICY=INVALIDATE_ALL
>
> At a jurisdiction migration, signing-key replacement, emergency signing-key
> rotation, or equivalent controlled security transition, existing sessions are
> invalidated and affected users must re-authenticate. Controlled previous-key
> acceptance is not authorized. A previous-key acceptance list is not required.
> The existing property that signing-key rotation invalidates previously issued
> sessions must be preserved.
>
> This is a standing security and migration policy. It is not a requirement to
> preserve current in-memory sessions at initial production go-live.
>
> ## ITEM 5 — PRE-5 ENGINE VARIANT
>
> ENGINE_VARIANT=RDS_POSTGRESQL
> POSTGRESQL_MAJOR_VERSION=16
>
> Aurora PostgreSQL-compatible remains an allowed future architectural option but
> is deferred unless subsequently justified by measured availability, scaling,
> operational, or commercial requirements.
>
> This decision must not introduce application-level dependence on RDS-specific
> semantics that would defeat the existing D.21 portability property.
>
> Instance class, storage sizing, Multi-AZ or other topology, read replicas,
> backup and maintenance windows, production networking, security groups,
> parameter groups, monitoring configuration, production endpoint creation and
> live database provisioning remain P1 operational decisions and are not selected
> or authorized by this ruling.
>
> ## AUTHORIZED NEXT LANE
>
> One non-production engineering lane to implement and prove the governed
> tenant-assignment service/API, the two-event audit model, and the authority,
> revocation and fail-closed semantics above; to run all required controls; to
> merge complete non-production work where Rule 13 is satisfied; to update
> production-readiness evidence and the activation pack; and to stop at the first
> true production gate.
>
> A synthetic test tenant may be used only for non-production verification and
> acquires no production authority.
>
> ## NOT AUTHORIZED
>
> Creation of the first production tenant; provisioning any live production
> database; applying schema or migrations to a live production database;
> entering, generating, rotating, or binding production credentials or secrets;
> creating production identities; assigning production tenant membership;
> production cutover; destructive or irreversible production action; production
> network or external-dashboard configuration.
>
> P1_AUTHORIZED=NO
>
> ## ITEM 6 — EXISTING RESIDUAL
>
> GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
>
> It does not block the non-production tenant-assignment implementation
> authorized by this ruling, but it remains open and must not be represented as
> closed.
>
> [SPONSOR]
> ```

## Items 4 and 5 required no engineering

Both select behaviour the estate already has, which is recorded so that a future
reader does not look for an implementation that does not exist.

**Item 4.** `AC7-07` is proven on PostgreSQL: rotating the signing key denies
every pre-rotation session while its store record stays active, so the denial
comes from signature verification. Declining the previous-key acceptance list
preserves that property rather than commissioning work whose effect would be to
weaken it. `PREVIOUS_KEY_LIST_PRESENT=NO` moves from *a gap* to *policy*.

**Item 5.** No code path branches on the engine variant — the D.21 portability
property. The ruling's added constraint (no RDS-specific semantics) is already
guarded: `tests/governance/test_w0f_architecture_contracts.py` forbids a provider
endpoint or region literal in application code, and `test_ksa_portability.py`
proves relocation changes no application byte.

## Item 3 was implemented under this ruling

See `petcare_execution/EVIDENCE/MVC-TENANT-MEMBERSHIP/…`. The twelve authorized
proof points are each carried by a named control.
