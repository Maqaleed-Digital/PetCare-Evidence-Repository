# MVC-P1-AUTHORIZATION-REQUEST-001

> ## ⛔ SUPERSEDED 2026-09-13 — DO NOT EXECUTE AGAINST THIS REQUEST
>
> Replaced by **`P1_AUTHORIZATION_REQUEST-002.md`**. Never granted, so nothing
> is revoked by this banner.
>
> It is superseded on a point of **execution safety**, not bookkeeping: this
> request's abort condition says stop if `D.1` reports a pending count other
> than **39**, and migration `0035_genesis_platform_admin.sql` (PR #33,
> `RATIFICATION-004`) made the correct count **40**. Executed as written against
> today's `main`, phase D would abort on a correct chain.
>
> Its evidence base `1531d2c7` and plan revision 1 digest `54157317…` are both
> superseded too. Retained unedited below as the record of what was requested on
> 2026-09-12.

**Status:** `SUPERSEDED / NEVER GRANTED`
**Prepared:** 2026-09-12 · **Requesting lane:** `[LANE]`

```
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
```

This document **requests** authorization. It does not grant, imply or record
one. Only a Sponsor act ratifies (Rule 20), and a recommendation is not an
authorization.

---

## What is being requested

Authorization to execute **Phases B, C and D** of
`P1_ACTIVATION_PLAN-001.md` — provision the production database, create and
bind the production secrets, and apply the migration chain — against the
approved production account.

```
ENVIRONMENT=production
ENGINE=RDS PostgreSQL, major version 16          RATIFICATION-002 item 5
FIRST_PRODUCTION_TENANT=pharmacare_riyadh        RATIFICATION-003 (identity only)
EVIDENCE_BASE_SHA=1531d2c79df67368a910d4681d376be0e9eab794
PLAN_DOCUMENT=P1_ACTIVATION_PLAN-001.md
PLAN_SHA256=54157317830c767478db3ec6a2135d0e35e6aedaf5aa1660caf755889f190805
```

## What will be created or mutated

| Phase | Act | Reversible |
|---|---|---|
| B.1 | create an RDS PostgreSQL 16 instance — **the first live mutation of this programme** | yes, by deletion |
| B.3 | set `rds.force_ssl=1` on the parameter group | yes |
| B.4 | create snapshot `<ID>-pre-schema` | yes |
| C.2 | create the session signing secret — **credential entry** | the secret, yes; a disclosed value, no |
| C.3 | configure managed rotation | yes |
| D.2 | apply 39 migrations to the live database | yes, by restoring `pre-schema` |
| D.5 | create snapshot `<ID>-post-schema` | yes |

**First live mutation:** `B.1`.
**Credential-entry gate:** `C.2`.

## Explicitly EXCLUDED from this request

```
E  creating the tenant row pharmacare_riyadh   — RATIFICATION-003 withholds it;
                                                 needs its own authorization
F  creating any production identity            — and the first platform_admin
                                                 bootstrap authority is UNRULED
G  binding the serving path / console config
H  cutover
   decommissioning the in-memory seeding path  — GATE_IRREVERSIBLE_ACTION
```

Authorizing B–D does not authorize E.

## Operational inputs the Sponsor or operator must supply

None can be derived from the repository, and AWS read-only discovery returned
`NOT_AVAILABLE` — the CLI is installed, no credentials are configured, and none
were requested. Each is an input, not a decision this lane may take:

```
AWS account / profile · region · DB instance identifier · instance class ·
allocated storage and type · Multi-AZ · backup retention · backup and
maintenance windows · read replicas · VPC, DB subnet group, subnet ids ·
security group ids · KMS key · DB parameter group · monitoring · master username
```

## Abort and rollback conditions

Stop and roll back rather than continue if:

- `B.2` reports `PubliclyAccessible=true`, `StorageEncrypted=false`, or a
  backup retention of `0`;
- a TLS connection with `sslmode=verify-full` cannot be established before
  `D` — the RDS root CA is missing from the runtime trust store, and the
  failure presents as a wrong credential;
- `D.1` reports a pending count other than 39, or names a migration the
  repository does not contain;
- `D.2` fails on any migration — nothing from that file is applied and it is
  not recorded, so the next run retries exactly it;
- `D.3` applies anything on the second run;
- `D.4` finds a non-empty `tenant` or `user_identity` table, a chain head
  other than `GENESIS/1`, or a role constraint admitting a value outside the
  four canonical ids.

Each abort restores the most recent snapshot and leaves the plan re-runnable.

## Evidence this request rests on

```
REGRESSION=846 passed (ROOT 246 · RUNTIME 247 · API 353)
POSTGRESQL=142 controls across 7 suites, 0 skipped
PERTURBATIONS=3 this lane, all proven applied and restored, 0 vacuous
SCANNERS=prohibited_literal 402/0 · secret_scan CLEAN · bundles 30/206/0 failed
PRODUCTION_TENANT_ROW_CREATED=NO   proven from live source
LIVE_SCHEMA_APPLIED=NO
PRODUCTION_SECRETS_ENTERED=NO
```

## Residual carried into this request

```
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
```

The retired seed credential is absent from every serving path and the identities
it belonged to are discarded, so it cannot become a production credential. It
remains in this PUBLIC repository's git history. Not closed, not blocking B–D,
and it should be cleared before final production release.

Also open and not blocking: `ARCH-01` signatures/anchoring,
`AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN`, the PRE-2D pharmacy surface disposition,
`PILOT_INVITE_CODES_ARE_PUBLIC_LITERALS`, and the unruled first-`platform_admin`
bootstrap authority.

## Decision

```
P1_RULING=____________________   date: __________  [SPONSOR]
```

No approval is recorded here on the Sponsor's behalf.
