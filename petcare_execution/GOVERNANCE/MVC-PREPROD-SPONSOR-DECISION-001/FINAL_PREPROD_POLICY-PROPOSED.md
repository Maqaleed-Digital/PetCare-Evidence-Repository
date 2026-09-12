# Final pre-production policy — PROPOSED, awaiting Sponsor signature

**Status:** `PROPOSED / AWAITING_SPONSOR_RULING`
**Drafted:** 2026-09-12 · **Base:** `f94a927838312fb2457f62f7deeb3a50352596e2`
**Resolves:** board items 2, 3, 4, 5 · **Board:** `PREPROD_DECISION_BOARD-001.md`

## Two things this document does not do

**It does not supply item 2.** The tenant identifier and display name must
correspond to the real organisation to be onboarded first. No lane may choose
them: PRE-1's whole finding was that a tenant value with no authority behind it
is indistinguishable, once written, from one the Sponsor chose. The fields are
left blank below.

**It is not a ruling.** It is the text of one, prepared so that signing it is a
single act. `STATUS` stays `PROPOSED` until it is given in the Sponsor's own
voice with a `[SPONSOR]` tag — as `RATIFICATION-001.md` was. Writing the wording
does not make the wording present.

---

## The ruling text, for signature

```text
[SPONSOR RULING — MYVETICARE FINAL PRE-PRODUCTION POLICY]

2 — FIRST PRODUCTION TENANT

tenant_id = <SPONSOR VALUE — NOT SUPPLIED>
display_name = <SPONSOR VALUE — NOT SUPPLIED>

This is the first governed production tenant.
No tenant value may be inferred from email address, role, geography,
test fixtures, or application defaults.

3 — TENANT-ASSIGNMENT AUTHORITY

I authorize `platform_admin` as the sole actor role permitted to assign,
change, or revoke tenant membership.

A platform_admin may assign membership across tenants.

Every assignment, change, and revocation must:

- identify the authenticated actor;
- identify the target identity;
- identify the previous tenant where applicable;
- identify the resulting tenant or revocation;
- validate the target tenant through the governed tenant registry;
- produce a durable audit event;
- fail closed if authorization, tenant validity, persistence, or audit
  recording cannot be established.

Tenant assignment must not create, modify, or elevate a user's role.

In particular, the tenant-assignment control path must not grant
`platform_admin`.

Creation or elevation of a platform_admin is a separate privilege-management
authority and is not authorized by this ruling.

No second-party approval is required for ordinary tenant membership changes
under this initial operating model.

4 — PRE-4 SESSION POLICY

I select INVALIDATE ALL SESSIONS.

At a jurisdiction migration, signing-key replacement, or equivalent controlled
security transition, existing sessions are invalidated and users must
re-authenticate.

Controlled previous-key acceptance is not authorized.

No previous-key acceptance list is required by this policy.

5 — PRE-5 ENGINE VARIANT

I select:

  RDS PostgreSQL
  PostgreSQL major version 16

Aurora PostgreSQL-compatible is deferred unless subsequently justified by
measured availability, scaling, operational, or commercial requirements.

Instance topology, sizing, backup configuration, replicas, and production
network configuration remain P1 operational decisions and are not authorized
by this ruling.

BOUNDARY

This ruling authorizes the non-production implementation and verification of
the governed tenant-assignment control path.

It does NOT authorize:

- provisioning the production database;
- applying schema to a live production database;
- creating or entering production credentials/secrets;
- production tenant creation;
- production identity creation;
- cutover;
- irreversible production action.

P1_AUTHORIZED=NO

Date: 12 September 2026
[SPONSOR]
```

---

## Implementation consequences, checked against live source

Recorded before signature, because one of them changes what the ruling asks for.

### 3.1 · `TENANT_ASSIGNMENT != ROLE_ASSIGNMENT` is implementable as an invariant

The serving layer already separates them. `UserIdentity.role` and
`UserIdentity.tenant_id` are distinct fields, `require_role` reads the role from
the session irrespective of tenant, and roles are not tenant-scoped — so moving an
identity between tenants cannot change what it may do, only what it may see.

The control path can therefore take a target identity and a tenant and **never
accept a role argument at all**, which is stronger than validating one. A
parameter that does not exist cannot be misused.

### 3.2 · ⚠️ The audit record has no field for the PREVIOUS tenant

The ruling requires every change to "identify the previous tenant where
applicable". The governed audit record cannot currently carry it.

`GOVERNED_EVENT_FIELDS` is exactly twelve fields, one of which is a single
`tenant_id`. There is no free-form payload, and the module states the cost of
changing the set:

> Changing this set changes every future digest and invalidates verification of
> every existing row, so it is a schema-and-chain migration, never an edit.

There is a second, sharper consequence. `query_events_for_tenant` filters on that
one `tenant_id`. **A membership change recorded under the new tenant alone is
invisible to the old tenant's audit log** — the tenant an identity left would
have no record that it left.

Three ways to satisfy the ruling:

| | Approach | Cost |
|---|---|---|
| **(a)** | write **two** audit events — a removal scoped to the old tenant, an addition scoped to the new | no schema change, no chain migration; both tenants see their own history; two rows per change |
| (b) | extend `GOVERNED_EVENT_FIELDS` with `previous_tenant_id` | a schema-and-chain migration; invalidates verification of existing rows unless versioned |
| (c) | encode `old→new` inside `reason_code` | no schema change, but puts structured data in a free-text field that nothing validates |

**(a) is recommended.** It is the only one that gives the *departed* tenant a
record of the departure, which is what "identify the previous tenant" is for —
and it needs no chain migration. A revocation is then simply the removal event
with no matching addition.

This is an engineering recommendation about how to satisfy the ruling, not a
change to it. If the Sponsor prefers (b), the chain migration is in scope and
should be said so explicitly.

### 4.1 · The session policy needs no engineering

`PRE4_SESSION_POLICY=INVALIDATE_ALL` selects the behaviour the system already
has. `AC7-07` is proven on PostgreSQL: rotating the signing key denies every
pre-rotation session while its store record stays active, so the denial comes
from signature verification.

Declining the previous-key acceptance list preserves that property rather than
commissioning work whose main effect would be to weaken it.

```
PREVIOUS_KEY_ACCEPTANCE_LIST=NOT_REQUIRED   (was PRESENT=NO; now by policy)
```

### 5.1 · The engine selection needs no engineering

No code path branches on the variant — the D.21 portability property. The estate
is proven against PostgreSQL 16, which RDS offers. The client-side TLS trap
recorded in P1 applies either way and stays a P1 step.

Leaving topology to the P1 sizing pack is consistent with the data-store
decision, which already records `INSTANCE TOPOLOGY … operational, gated`.

---

## What signing this enables, and what it does not

```
ENABLES   one non-production lane: build the governed tenant-assignment control
          path, prove authority / audit / revocation, re-run acceptance evidence,
          stop at GATE_LIVE_APPLY.
DOES NOT  provision · apply schema · create secrets · create a production tenant
          · create a production identity · cut over · anything irreversible.
P1_AUTHORIZED=NO
```

Item 2's values are not required to build the control path — the path validates a
tenant against the registry, and a test tenant exercises it. They are required
before any production tenant exists, which is a `GATE_LIVE_APPLY` act.

So items 3, 4 and 5 can be signed without item 2 if the Sponsor prefers to name
the first tenant later. Recorded so the choice is available rather than assumed.

## Residual

```
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
```

Separate, still open, should be cleared before final production release, and does
not hold up the tenant-assignment implementation.
