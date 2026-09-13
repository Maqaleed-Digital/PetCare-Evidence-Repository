# MVC-P1-AUTHORIZATION-REQUEST-002

**Status:** `REQUESTED / NOT GRANTED`
**Prepared:** 2026-09-13 · **Requesting lane:** `[LANE]`
**Supersedes:** `P1_AUTHORIZATION_REQUEST-001.md` (never granted)

```
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
```

This document **requests** authorization. It does not grant, imply or record
one. Only a Sponsor act ratifies (Rule 20), and a recommendation is not an
authorization.

---

## Why this reissue exists

Request `-001` rested on evidence base `1531d2c7` and on revision 1 of the plan.
Both moved:

* `RATIFICATION-004` (`MVC-GENESIS-PLATFORM-ADMIN-001`, 12 Sep) ruled the
  first-`platform_admin` bootstrap that `-001` carried as an open blocker, and
  PR #33 merged its non-production implementation to `main`.
* That merge added migration `0035_genesis_platform_admin.sql`, so the chain is
  now **40** migrations, not 39.

**The second point is not bookkeeping.** Revision 1 of the plan told the
operator to abort if `D.1` reported a pending count other than 39 — so executing
`-001` as written against today's `main` would have **aborted a correct chain**
at phase D. The stale number was the defect, not the chain. Plan revision 2
corrects it and adds `platform_admin_genesis` to the D.4 schema verification.

## What is being requested

Authorization to execute **Phases B, C and D** of `P1_ACTIVATION_PLAN-001.md`
(**revision 2**) — provision the production database, create and bind the
production secrets, and apply the migration chain — against the approved
production account.

```
ENVIRONMENT=production
ENGINE=RDS PostgreSQL, major version 16          RATIFICATION-002 item 5
FIRST_PRODUCTION_TENANT=pharmacare_riyadh        RATIFICATION-003 (identity only)
EVIDENCE_BASE_SHA=e693e6620d80661e34ae970abf0297d0bd37f98e
PLAN_DOCUMENT=P1_ACTIVATION_PLAN-001.md          revision 2
PLAN_SHA256=16818f7d483d58fa6d8da9a7ddf32ab24101bda1423a60164c00a7e23dc49539
PLAN_SHA256_REVISION_1=54157317830c767478db3ec6a2135d0e35e6aedaf5aa1660caf755889f190805   SUPERSEDED
```

`EVIDENCE_BASE_SHA` is the `main` that resulted from merging PR #33, and is the
commit every number below was measured at. This request document and the plan
amendment are governance prose committed on top of it; they touch no code, no
migration and no test. Plan step `A.1` still binds the act to the SHA actually
checked out at execution time, and that SHA must contain this request.

## What will be created or mutated

| Phase | Act | Reversible |
|---|---|---|
| B.1 | create an RDS PostgreSQL 16 instance — **the first live mutation of this programme** | yes, by deletion |
| B.3 | set `rds.force_ssl=1` on the parameter group | yes |
| B.4 | create snapshot `<ID>-pre-schema` | yes |
| C.2 | create the session signing secret — **credential entry** | the secret, yes; a disclosed value, no |
| C.3 | configure managed rotation | yes |
| D.2 | apply **40** migrations to the live database | yes, by restoring `pre-schema` |
| D.5 | create snapshot `<ID>-post-schema` | yes |

**First live mutation:** `B.1`.
**Credential-entry gate:** `C.2`.

Applying `0035` creates the genesis **shape** — the `GENESIS` provenance value,
the single-`GENESIS` unique index, and an **empty** `platform_admin_genesis`
table. It creates no identity and consumes no authority. `D.4` asserts that
table is empty precisely so that "the chain was applied" can never be confused
with "the genesis act was performed".

## Explicitly EXCLUDED from this request

```
-  the first platform_admin genesis act        - RULED by RATIFICATION-004 but
                                                 PRODUCTION_GENESIS_EXECUTION=
                                                 NOT_AUTHORIZED. It is
                                                 GATE_LIVE_APPLY *plus*
                                                 GATE_CREDENTIAL_ENTRY and needs
                                                 an authorization naming
                                                 P1_GENESIS_STEP-001.md
E  creating the tenant row pharmacare_riyadh   - RATIFICATION-003 withholds it;
                                                 needs its own authorization
F  creating any production identity
G  binding the serving path / console config
H  cutover
   decommissioning the in-memory seeding path  - GATE_IRREVERSIBLE_ACTION
```

Authorizing B–D does not authorize E, and does not authorize the genesis step.

## Operational inputs the Sponsor or operator must supply

Unchanged from `-001`. None can be derived from the repository, and AWS
read-only discovery remains `NOT_AVAILABLE` — the CLI is installed, no
credentials are configured, and none were requested. Each is an input, not a
decision this lane may take:

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
- **`D.1` reports a pending count other than 40**, or names a migration the
  repository does not contain;
- `D.2` fails on any migration — nothing from that file is applied and it is
  not recorded, so the next run retries exactly it;
- `D.3` applies anything on the second run;
- `D.4` finds a non-empty `tenant`, `user_identity` **or `platform_admin_genesis`**
  table, a chain head other than `GENESIS/1`, or a role constraint admitting a
  value outside the four canonical ids.

Each abort restores the most recent snapshot and leaves the plan re-runnable.

## Evidence this request rests on

Measured at `EVIDENCE_BASE_SHA`, not carried from `-001`:

```
REGRESSION=889 passed   (ROOT 271 · RUNTIME 247 · API 371)
                        271 + 247 + 371 = 889 - the per-suite sum check
                        each suite also run ALONE, not only combined
POSTGRESQL=160 controls across 8 suites, 0 skipped
CI=PR #33 verify green, 0 skipped steps; 882 passed + 7 skipped, where the 7 are
   the pre-existing cross-repository join CI cannot compute (baseline main was
   847 + the same 7). 882 + 7 = 889.
PERTURBATIONS=13/13 armed, 0 vacuous          MVC-GENESIS-PLATFORM-ADMIN bundle
SCANNERS=prohibited_literal 407/0 · secret_scan CLEAN 3960/0
         bundles 32 / 213 artefacts / 0 failed
MIGRATION_COUNT=40                             from live source
PRODUCTION_TENANT_ROW_CREATED=NO               proven from live source
GENESIS_CONSUMED=NO                            in every environment
LIVE_SCHEMA_APPLIED=NO
PRODUCTION_SECRETS_ENTERED=NO
PRODUCTION_IDENTITY_CREATED=NO
```

## Rule adjudication at this base

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT              SATISFIED
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE               SATISFIED
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN       SATISFIED
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT  SATISFIED
RULE_17=PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION SATISFIED
RULE_18=RESIDUE_REMEASURED_FROM_LIVE_SOURCE            SATISFIED
RULE_19=NO_FALSE_TAMPER_FINDING_UNDER_CORRECT_OPERATION SATISFIED
RULE_20 · RULE_21 · RULE_22                            UNDERIVED
```

`RULE_20`, `RULE_21` and `RULE_22` are cited by label in earlier receipts, but
**no definition of them exists anywhere in this repository**. They are reported
as `UNDERIVED` rather than adjudicated: a rule whose text cannot be read cannot
be applied, and inventing the text would be the defect the rules exist to
prevent. `RULE_20` is invoked at the top of this document ("only a Sponsor act
ratifies") on the strength of that established usage, not of a definition.

## Residual carried into this request

```
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
```

The retired seed credential is absent from every serving path and the identities
it belonged to are discarded, so it cannot become a production credential. It
remains in this PUBLIC repository's git history. Not closed, not blocking B–D,
and it should be cleared before final production release.

Also open and not blocking: `ARCH-01` signatures/anchoring,
`AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN`, the PRE-2D pharmacy surface disposition, and
`PILOT_INVITE_CODES_ARE_PUBLIC_LITERALS` (re-measured live: 2 literals).

**Closed since `-001`:** `FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY` — ruled by
`RATIFICATION-004`, mechanism built and proven non-production, act not
performed.

## Decision

```
P1_RULING=____________________   date: __________  [SPONSOR]
```

No approval is recorded here on the Sponsor's behalf.
