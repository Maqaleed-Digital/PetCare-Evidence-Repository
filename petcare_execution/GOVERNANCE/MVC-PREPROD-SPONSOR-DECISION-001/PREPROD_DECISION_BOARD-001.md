# Pre-production decision board

**Date:** 2026-09-12 · **Base:** `aa10a44aba653349d4b59f2d7a18e98573f9ea48`
**Status:** 1 of 6 resolved · **P1 is NOT authorized**

Six items, not four. The board was previously drawn with four because the
tenant-assignment path was recorded as an engineering gap. It is not: **who may
assign or change tenant membership is an authority decision**, and it belongs on
this board alongside the others.

Every option below is quoted from an existing governed record. Nothing here
invents an alternative.

| # | Decision | State |
|---|---|---|
| 1 | PRE-1 / PRE-2 / pharmacy ratification | **RESOLVED** — `RATIFICATION-001.md`, `[SPONSOR]`, 12 Sep 2026 |
| 2 | First production tenant | UNRESOLVED — **needs two Sponsor values; no lane may choose them** |
| 3 | Tenant-assignment authority and control path | **PROPOSED** — `FINAL_PREPROD_POLICY-PROPOSED.md` |
| 4 | PRE-4 · session treatment at cutover | **PROPOSED** — `FINAL_PREPROD_POLICY-PROPOSED.md` |
| 5 | PRE-5 · engine variant | **PROPOSED** — `FINAL_PREPROD_POLICY-PROPOSED.md` |
| 6 | GitHub Support `refs/pull/1–6` | `NOT_SENT` |

---

## 1 · PRE-1 / PRE-2 / pharmacy — RESOLVED

Ratified in the Sponsor's own voice, tagged `[SPONSOR]`, 12 September 2026. See
`RATIFICATION-001.md` for the verbatim statement.

The ruling states its own boundary: it **does not** authorize a live database
apply, production secret creation, production cutover, or any irreversible
production action.

---

## 2 · First production tenant — UNRESOLVED

The registry exists and **ships empty** (`TENANT_ROWS_CREATED=0`). Nothing infers
a tenant, and nothing creates one.

### What a tenant row requires, from migration `0034`

```
tenant_id     TEXT PRIMARY KEY, non-blank — the stable machine identifier, and
              the value every tenant_id column references
display_name  TEXT NOT NULL, non-blank — presentation only, never compared
status        ACTIVE | DISABLED, defaults ACTIVE
created_at    set on write
disabled_at   NULL while ACTIVE
```

So the decision needs exactly two Sponsor-supplied values: **the identifier and
the display name.**

### What is NOT available to choose from

`tenant_jeddah_001` and `tenant_riyadh_001` appear **only** in EP-05/EP-06 test
fixtures. No governance record establishes either. Promoting a value whose
authority is a file under `tests/` would afterwards be indistinguishable from one
the Sponsor chose, which is why PRE-1 declined to offer them and why they are not
offered here.

### Consequence of leaving it unresolved

Every identity is tenantless and fails closed at `require_tenant()` with
`403 NO_TENANT_AUTHORITY`. That is correct behaviour, not a defect — but it means
a deployment with no tenant serves no tenant-scoped route to anyone.

Creating the first tenant is a live write: `GATE_LIVE_APPLY`.

---

## 3 · Tenant-assignment authority and control path — UNRESOLVED

**This is the item the board was missing.**

### What exists today

```
TENANT_ASSIGNMENT_HAS_NO_GOVERNED_API=YES
```

Registration establishes identity and **never** tenant authority — W0-C makes
tenant a server-side assignment, so a registration form cannot supply one. No
route assigns, changes or revokes tenant membership. The only path is an operator
calling `IDENTITY_REPO.upsert()` directly, which is what the end-to-end proof
does and labels as such.

An operator calling the repository is sufficient for a rehearsal and is not a
governed operating model: it leaves no audit event, requires no authorization,
and has no revocation path.

### What the control path needs to be

```
authorized actor
  → governed tenant-assignment API/service
  → explicit target identity
  → explicit tenant
  → authorization check
  → audit event
  → durable write
  → verification / revocation path
```

Each element already has an implementation to reach: `require_role` for the
authorization check, `AUDIT_REPO.append_event` for the audit event,
`PostgresIdentityRepository` for the durable write, and the registry's
`is_assignable` for the tenant check. What does not exist is the decision about
**who** may invoke it.

### A position is now proposed

`FINAL_PREPROD_POLICY-PROPOSED.md` carries a drafted ruling answering Q3.1–Q3.5:
`platform_admin` is the sole assign/change/revoke authority, may act across
tenants, and the control path **must not create, modify or elevate a role** —
`TENANT_ASSIGNMENT != ROLE_ASSIGNMENT`. Every change produces a durable audit
event; no second-party approval for ordinary membership.

It is PROPOSED, not ruled. The paragraph below still stands as the reason the
question was put to the Sponsor rather than answered by a lane.

### Why this was not settled by a lane

`platform_admin` is the obvious holder, and that is exactly the reason to refuse
to assume it. It is the only role with blanket route access, so binding tenant
membership to it would be the least-effort engineering answer — and a
least-effort answer adopted silently becomes constitutional authority by
accident. Tenant membership determines which data an identity can reach at all;
it is a stronger power than any route guard currently grants.

Recorded as a question for the Sponsor, with the facts, and **no recommendation**:

```
Q3.1  Which role or actor class may ASSIGN tenant membership?
Q3.2  May the same actor CHANGE or REVOKE an existing assignment, or is
      revocation a separate authority?
Q3.3  May an actor assign membership in a tenant other than its own?
Q3.4  What evidence must an assignment produce — an audit event is available;
      is a second-party approval required?
Q3.5  Does assigning `platform_admin` itself require a different authority from
      assigning `owner`?
```

`Q3.5` is asked because a tenant-assignment path that can also grant the highest
role is a privilege-escalation path, and MIG-03 exists in the migration for the
same reason.

---

## 4 · PRE-4 · session treatment at cutover — UNRESOLVED

Two admissible options, quoted from `MVC-W0F-KSA-MIGRATION-READINESS-001` §6:

> - **Invalidate all sessions.** Every user re-authenticates. Simple,
>   fail-closed, and free of cross-jurisdiction session-state transfer.
> - **Controlled continuity.** Session state migrates with the database, sessions
>   stay valid. Requires AC-7's server-side store to be live and the previous-key
>   question to be settled.

The record's own recommendation:

> Recommended: **invalidate**, unless continuity is a stated business
> requirement.

### A precondition the pack did not state

**Option 2 is not currently implementable.** Controlled continuity requires the
previous-key question to be settled, and the serving path has no previous-key
acceptance list — `PREVIOUS_KEY_LIST_PRESENT=NO`, recorded in the W0-F PR-B
receipt and still true in live source. Choosing continuity therefore selects
engineering work, not just a policy.

### And a scope observation

At **go-live** this decision is close to vacuous: sessions today live in process
memory, so switching to the persistent store leaves nothing to preserve. The
decision becomes live for the **KSA migration**, and for any emergency key
rotation thereafter — which is where AC7-07 was proven.

So the honest framing is: this is a standing policy about key rotation and
jurisdiction transfer, not a go-live step.

---

## 5 · PRE-5 · engine variant — UNRESOLVED

Quoted from `MVC-W0F-DATA-STORE-DECISION-001`:

> `ENGINE VARIANT` — RDS PostgreSQL vs Aurora PostgreSQL-compatible is an
> operational sizing choice, deferred. **Both satisfy every requirement above;
> neither changes application code.**
>
> `INSTANCE TOPOLOGY` — sizing, replicas, backup windows — operational, gated.

### Facts that bear on it, from this estate specifically

- The application is proven against **PostgreSQL 16** — 39 migrations replay
  clean, 103 integration controls pass. Both variants offer 16.
- `rds.force_ssl` applies to both, and both carry the same client-side trap:
  a runtime whose trust store lacks the RDS root CA fails to connect, and the
  failure reads as a wrong credential. P1 of the activation pack records it.
- Nothing in the repository expresses a preference, and no code path branches on
  the variant — that is the D.21 portability property working.

No recommendation is offered: the inputs are cost, availability target and
operational familiarity, none of which the repository holds.

---

## 6 · GitHub Support `refs/pull/1–6` — NOT_SENT

```
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
```

Parallel external housekeeping. The retired seed credential is gone from the
working tree and from every serving path, and the identities it belonged to are
discarded — so it can no longer become a production credential. It **remains in
this PUBLIC repository's git history**, and removing it there is an
external-account action that no engineering lane performs.

Not claimed closed, and not blocking any of the above.

---

## Sequence

```
1  RESOLVED — ratified
2..5  one consolidated production-policy ruling
6  build and verify the tenant-assignment control path (needs 3 first)
7  THEN authorize P1
```

`P1` is not authorized and is not requested by this document.

Issuing a production activation run before item 3 is decided would arrive at P5
with an unresolved authority path — a deployment where tenant membership is
granted by whoever can reach the repository.
