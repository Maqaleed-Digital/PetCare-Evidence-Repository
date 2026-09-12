# RATIFICATION-001 — Sponsor ratification of the pre-production authority rulings

**Ratifies:** `MVC-PREPROD-SPONSOR-DECISION-PACK-001`
**Date of ruling:** 12 September 2026 · **Recorded:** 2026-09-12
**Actor tag:** `[SPONSOR]`
**Base at time of recording:** `aa10a44aba653349d4b59f2d7a18e98573f9ea48`

## Status change this record effects

```
BEFORE  RULING_ACTOR_TAG=UNTAGGED
        implementation proceeded on a direct instruction, recorded as such
AFTER   RULING_ACTOR_TAG=[SPONSOR]
        PRE-1 and PRE-2 are RATIFIED Sponsor decisions
```

The implementations merged under PR #25 and PR #26 were carried out on a direct
instruction that carried no actor tag, and the decision pack said so rather than
implying more. This record closes that gap: the same rulings are now given in the
Sponsor's own voice, tagged, and dated.

Nothing in the implementation changes. What changes is its standing.

## The ruling, verbatim

> ```
> [SPONSOR RULING — MYVETICARE PRE-PRODUCTION AUTHORITY]
>
> I ratify PRE-1 Option 1-B.
>
> The three historical seed identities are development artefacts and must not be
> migrated into production. Their published/default credential must never become
> a production credential. Production identities must be created only through
> the governed identity-creation path.
>
> I ratify PRE-2 Option 2-C.
>
> Canonical machine role IDs are the sole authorization authority:
>
> - platform_admin
> - partner_clinic_admin
> - veterinarian
> - owner
>
> Human-readable and localized role labels are presentation values only and must
> not confer, expand, or determine authorization.
>
> I also ratify the pharmacy-role disposition:
>
> - pharmacy is not an authorization principal or role;
> - pharmacy-domain and dispensing capabilities may remain where an already
>   governed actor is authorized to perform them;
> - capabilities for which no governed actor exists remain non-authoritative /
>   disabled until separately assigned.
>
> These rulings ratify the implementations already merged under PRE-1 and PRE-2.
> They do not authorize any live database apply, production secret creation,
> production cutover, or irreversible production action.
>
> Date: 12 September 2026
> [SPONSOR]
> ```

## What this ratifies

| | Ratified | Implemented at |
|---|---|---|
| PRE-1 | Option **1-B** — seed identities are development artefacts, not migrated; the published credential never becomes a production credential; production identities only through the governed creation path | PR #25 (`e96c3de`) |
| PRE-2 | Option **2-C** — canonical machine role IDs are the sole authorization authority; labels are presentation only | PR #25 (`e96c3de`) |
| Pharmacy | `pharmacy` is not a principal; capabilities remain where a governed actor exists; otherwise non-authoritative/disabled until separately assigned | PR #25 (`e96c3de`) |

Each is verified against live source in
`petcare_execution/EVIDENCE/MVC-PREPROD-AUTHORITY-CONVERGENCE/20260912T124500Z/`.

## What this explicitly does NOT authorize

Quoted from the ruling, because the boundary is the point:

> They do not authorize any live database apply, production secret creation,
> production cutover, or irreversible production action.

```
GATE_LIVE_APPLY           NOT AUTHORIZED
GATE_CREDENTIAL_ENTRY     NOT AUTHORIZED
GATE_IRREVERSIBLE_ACTION  NOT AUTHORIZED
GATE_EXTERNAL_DASHBOARD_CONFIG  NOT AUTHORIZED
P1 (provision the database)     NOT AUTHORIZED
```

A ratification of a design decision is not an authorization to apply it to a
production system. The two are separate acts and this record is only the first.

## The ratified pharmacy clause has an engineering consequence already recorded

> capabilities for which no governed actor exists remain non-authoritative /
> disabled until separately assigned.

Three such capabilities are recorded as `DOMAIN_CAPABILITY_PENDING_ROLE_BINDING`
in `PHARMACY_ROLE_DISPOSITION.md`: the `/pharmacy` page's safety-check and
cold-chain regions, a dead `ROLE_PHARMACY_OPERATOR` constant, and a HITL reviewer
map naming `pharmacist`. None confers authority today. Each is now covered by a
ratified rule rather than by a lane's judgement.

## What remains UNRESOLVED after this ratification

This record resolves decisions 1 of 6 on the pre-production board. It does not
touch the other five, and it does not imply a disposition for any of them:

```
2  First production tenant                     UNRESOLVED
3  Tenant-assignment authority and control path UNRESOLVED
4  PRE-4 session treatment at cutover          UNRESOLVED
5  PRE-5 engine variant                        UNRESOLVED
6  GitHub Support refs/pull/1-6                NOT_SENT
```

**Decision 3 is an authority decision, not an engineering task.** The estate now
has a tenant registry, but the only way to assign a tenant is an operator calling
the identity repository directly. Who may assign or change tenant membership, and
under what audit and control rules, is a constitutional question. No lane should
settle it by choosing a convenient default — in particular, `platform_admin`
holding that power because it was the obvious place to put it would be
constitutional authority acquired by accident.
