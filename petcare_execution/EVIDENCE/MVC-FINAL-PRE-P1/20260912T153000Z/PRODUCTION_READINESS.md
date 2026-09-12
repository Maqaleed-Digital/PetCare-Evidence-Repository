# Production readiness — remeasured from live evidence

**Base:** `1531d2c79df67368a910d4681d376be0e9eab794` · **Date:** 2026-09-12

Not inherited. `READY` is not carried forward because an earlier receipt said
`READY`; each prerequisite below was re-read from source or re-run in this lane.

## Classification

| Prerequisite | State | Basis |
|---|---|---|
| Canonical role authority (PRE-2 2-C) | **READY** | `roles.py`; 31 controls; `VALID_ROLES is ALLOWED_ROLES` |
| Seed identities discarded (PRE-1 1-B) | **READY** | startup creates 0 identities, proven in a fresh subprocess; 16 controls |
| No live credential literal | **READY** | 0 across 239 serving files |
| Tenant registry | **READY** | `0034`; 18 controls; ships empty |
| Tenant-assignment control path | **READY** | `tenant_membership.py`; 39 controls; 6 perturbations |
| Audit chain persisted + verified | **READY** | `0032`; 22 controls; two-event model proven |
| Session store + AC-7 | **READY** | 13 controls on PostgreSQL; rotation denial from signature verification |
| Secret provider, fail-closed | **READY** | 64 controls; no fallback on any path |
| Migration chain + ledger | **READY** | 39 replay clean; runner idempotent; drift refused |
| KSA portability / engine neutrality | **READY** | 0 region, endpoint or engine literals in application trees |
| Identity migration | **READY** | `PASS_EMPTY_BY_DESIGN`, `SOURCE=0` |
| First production tenant identity | **READY** | `RATIFICATION-003` — identity only |
| Session policy at transition | **READY** | `INVALIDATE_ALL`; selects behaviour AC7-07 proves |
| Engine variant | **READY** | RDS PostgreSQL 16 |
| CI non-skip coverage | **READY** | control added; 142 PostgreSQL controls named and run |
| — | | |
| Production database | **READY_PENDING_LIVE_GATE** | plan Phase B; `GATE_LIVE_APPLY` |
| Production secrets | **READY_PENDING_LIVE_GATE** | plan Phase C; `GATE_CREDENTIAL_ENTRY` |
| Live schema apply | **READY_PENDING_LIVE_GATE** | plan Phase D; `GATE_LIVE_APPLY` |
| Production tenant **row** | **READY_PENDING_LIVE_GATE** | plan Phase E; withheld by `RATIFICATION-003` |
| Serving binding / cutover | **READY_PENDING_LIVE_GATE** | plan Phases G–H |
| Operational sizing inputs | **READY_PENDING_LIVE_GATE** | reserved to P1 by `RATIFICATION-002` item 5; recorded as inputs, not invented |
| — | | |
| GitHub Support `refs/pull/1–6` | **OPEN_NON_BLOCKING_PRE_RELEASE** | `NOT_SENT`; external account action |
| `ARCH-01` signatures / anchoring | **OPEN_NON_BLOCKING_PRE_RELEASE** | specification question, carried since W0-G |
| `AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN` | **OPEN_NON_BLOCKING_PRE_RELEASE** | needs a governed answer on tenantless security events |
| PRE-2D pharmacy surface disposition | **OPEN_NON_BLOCKING_PRE_RELEASE** | capability question answered; surface disposition not ruled |
| `PILOT_INVITE_CODES_ARE_PUBLIC_LITERALS` | **OPEN_NON_BLOCKING_PRE_RELEASE** | outside the rulings' scope |
| Clinical serving persistence | **OPEN_NON_BLOCKING_PRE_RELEASE** | outside W0-F/W0-G; recorded in the W0-F bundle |
| — | | |
| First `platform_admin` bootstrap authority | **BLOCKED** | see below |
| — | | |
| Aurora topology | **NOT_APPLICABLE** | deferred by `RATIFICATION-002` item 5 |
| Previous-key acceptance list | **NOT_APPLICABLE** | `NOT_AUTHORIZED` by `RATIFICATION-002` item 4 |
| Seed identity migration | **NOT_APPLICABLE** | discarded by `RATIFICATION-001`; source is empty |

## The one BLOCKED item

```
FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY=UNRULED
```

Found while writing Phase F of the plan, not carried from a prior receipt.

Assigning tenant membership requires an existing `platform_admin`
(`RATIFICATION-002` item 3). Creating or elevating one is *"a separate
privilege-management authority and is not authorized by this ruling"*. Seed
identities are discarded and registration establishes no tenant and no elevated
role.

So the production system, as ruled, has no authorized way to obtain its first
`platform_admin` — and therefore no way to assign the first identity to
`pharmacare_riyadh`.

**It does not block B–D.** Provisioning, secrets and schema are unaffected, and
the plan requests only those. It blocks **Phase F**, and it should be ruled
before the cutover window rather than discovered inside it.

## Determination

```
PRODUCTION_READINESS=READY_PENDING_LIVE_GATE
NEXT_GENUINE_GATE=GATE_LIVE_APPLY   (plan Phase B.1 — provision the database)
P1_AUTHORIZED=NO
```

Every non-production prerequisite is `READY`. Everything remaining is either a
live gate, a recorded non-blocking residual, or the single unruled authority
above.
