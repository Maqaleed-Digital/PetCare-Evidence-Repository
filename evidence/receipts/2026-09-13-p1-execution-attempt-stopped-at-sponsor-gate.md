# Receipt — P1 production activation run, stopped at the Sponsor gate

**Date:** 2026-09-13 · **Lane:** `[LANE]` · **Repository:** `petcare-evidence-repository`

```
MYVETICARE_PRODUCTION_EXECUTION=STOPPED_AT_SPONSOR_GATE
START_SHA=63c4eae46d9cfe771cdff2f615c651fc87368763
NEXT_GENUINE_GATE=SPONSOR_P1_B_D_AUTHORIZATION
```

A continuous production-activation run was attempted. It stopped at the first
genuine gate — the Sponsor authorization for `REQUEST-002` — which is terminal
boundary **A**. No production action of any kind was taken.

## 1 — Live state, measured not assumed (Rule 14)

```
ORIGIN_MAIN=63c4eae46d9cfe771cdff2f615c651fc87368763   matches handoff
WORKTREE_TRACKED_CHANGES=0
MIGRATION_COUNT=40
TENANT_INSERTS_IN_MIGRATIONS=0
GENESIS_INSERTS_IN_MIGRATIONS=0
SEEDED_PLATFORM_ADMINS=0
RULES_RATIFIED=13..24
RULES_UNDEFINED_UNRATIFIED=1..12
```

Every handoff value was re-derived from live source. None was carried from
narrative. Nothing diverged, so no supersession analysis was required.

## 2 — Authority check · the gate that stopped this run

```
REQUEST_002_STATUS=REQUESTED / NOT GRANTED
REQUEST_002_DECISION_LINE=BLANK
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
SPONSOR_ACT_AUTHORIZING_REQUEST_002=NONE_FOUND
```

The whole of `petcare_execution/GOVERNANCE` was searched for a Sponsor act
granting P1. The only two `P1_RULING=` lines in the estate are the blank
decision lines of `REQUEST-001` (superseded) and `REQUEST-002`.

Under ratified **Rule 20**, no agent may ratify, approve, authorize or sign a
Sponsor decision on the Sponsor's behalf, and neither an execution prompt, a
recommendation, readiness, nor green CI constitutes authority. The gate holds.

## 3 — Request freshness · no repair was warranted

`REQUEST-002` was checked against live state rather than assumed current:

```
CITED_PLAN_SHA256=16818f7d483d58fa6d8da9a7ddf32ab24101bda1423a60164c00a7e23dc49539
ACTUAL_PLAN_SHA256=16818f7d483d58fa6d8da9a7ddf32ab24101bda1423a60164c00a7e23dc49539   MATCH
CITED_EVIDENCE_BASE=e693e66…   ancestor of origin/main: YES
REQUEST_002_STALE=NO
```

No reissue or repair was performed, because none was justified. A reissue is
warranted only when the evidence base or the plan digest moves; neither has.

## 4 — AWS access, re-probed from live (Rule 18)

```
AWS_CLI=aws-cli/2.34.18 installed
AWS_PROFILE=<not set>      AWS_REGION=<not set>
AWS_ACCESS_KEY=<not set>   AWS_SECRET_KEY=<not set>
AWS_STS_GET_CALLER_IDENTITY=NoCredentials
AWS_ACCESS=REQUIRED_HUMAN_GATE
```

No credentials were requested, created, or inferred. Because none exist, **zero**
operational inputs are currently discoverable read-only: every `describe`/`list`
call that could resolve a VPC, subnet, security group, KMS key or parameter group
requires an authenticated session.

## 5 — Operational inputs, classified

15 declared input rows in the live plan's operational-input block. With no AWS
session nothing classifies as `DISCOVERABLE_READ_ONLY` today; several are
nonetheless **constrained** by governed abort conditions, which narrows what the
Sponsor must actually choose.

| input | classification | governed constraint already fixed |
|---|---|---|
| `AWS_ACCOUNT / PROFILE` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | approved production account |
| `REGION` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | D.21 — approved temporary operating location; KSA migration mandatory when the approved site is ready |
| `DB_INSTANCE_IDENTIFIER` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | naming convention |
| `INSTANCE_CLASS` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | — |
| `ALLOCATED_STORAGE / MAX / TYPE` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | — |
| `MULTI_AZ` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | — |
| `BACKUP_RETENTION_DAYS` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | **must be > 0** — retention of 0 is an abort condition |
| `BACKUP_WINDOW / MAINTENANCE_WINDOW` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | — |
| `READ_REPLICAS` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | — |
| `VPC_ID / DB_SUBNET_GROUP / SUBNET_IDS` | `CREDENTIAL_GATED` → `SPONSOR` | **`PubliclyAccessible=true` is an abort condition** ⇒ private placement |
| `SECURITY_GROUP_IDS` | `CREDENTIAL_GATED` → `SPONSOR` | as above |
| `KMS_KEY_ID` | `CREDENTIAL_GATED` → `SPONSOR` | **`StorageEncrypted=false` is an abort condition** ⇒ a key is mandatory, not optional |
| `DB_PARAMETER_GROUP` | `CREDENTIAL_GATED` → `SPONSOR` | **must carry `rds.force_ssl=1`** (plan B.3) |
| `MONITORING` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | — |
| `MASTER_USERNAME` | `SPONSOR_OPERATIONAL_DECISION_REQUIRED` | — |

```
OPERATIONAL_INPUTS_RESOLVED=0/15
DISCOVERABLE_READ_ONLY_TODAY=0     blocked behind AWS_ACCESS
ALREADY_FIXED_BY_GOVERNED_STATE=engine RDS PostgreSQL 16 · rds.force_ssl=1 ·
                                StorageEncrypted=true · PubliclyAccessible=false ·
                                backup retention > 0
```

Nothing was invented. Four values that look like free choices are in fact
already bounded by the plan's own abort conditions, and that is recorded so the
Sponsor decides within the bound rather than re-deciding it.

## 6 — Rule-13 acceptance at this boundary

```
REGRESSION=889 passed   ROOT 271 · RUNTIME 247 · API 371
                        271 + 247 + 371 = 889 — per-suite sum reconciled
POSTGRESQL=160 controls, 8 suites, 0 skipped
PERTURBATIONS=13/13 armed, 0 vacuous   MVC-GENESIS-PLATFORM-ADMIN bundle
BUNDLES=32 / 213 artefacts / 0 failed
SECRET_SCAN=CLEAN 3960/0
PROHIBITED_LITERAL=407 scanned / 0 active defaults
SEALED_BUNDLES_MODIFIED=0     HISTORICAL_RECEIPTS_REWRITTEN=0
```

## 7 — Production boundary, unchanged

```
RDS_PROVISIONED=NO          RDS_IDENTIFIER=NOT_CREATED
PRODUCTION_SECRETS_BOUND=NO
LIVE_SCHEMA_APPLIED=NO      MIGRATIONS_APPLIED=0
GENESIS_AUTHORIZED=NO       GENESIS_CONSUMED=NO
PLATFORM_ADMIN_CREATED=NO
PRODUCTION_TENANT_ROW_CREATED=NO
PRODUCTION_IDENTITIES=0     SERVING_CUTOVER=NO
REFS_PULL_1_6=PROPOSED_RELEASE_RESIDUAL   not governed; needs its own act
```

## 8 — Stop reason

```
STOP=SPONSOR_AUTHORIZATION_ABSENT
NEXT_GENUINE_GATE=SPONSOR_P1_B_D_AUTHORIZATION
GATE_AFTER_THAT=AWS_CREDENTIAL_ENTRY + SPONSOR_OPERATIONAL_INPUT_DECISION
```

This is terminal boundary **A**, and it was not manufactured: every read-only
verification available was completed first, the request was checked for
staleness and found current, full regression and evidence verification were run,
and no safe executable step remained.

Two gates stand between this receipt and `B.1`, the first live mutation — the
Sponsor act, and then AWS access plus the operational decisions above. Crossing
the first does not by itself make B–D executable.
