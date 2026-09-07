# MVC-W0F-ARCHITECTURE — D.21 ruling, architecture decisions, contract guards

**Base:** `41f77053a19819a36e1a761c698c145bc25e9e6f`
**Scope:** NON_PRODUCTION_ONLY · governance + architecture + guards (PR-A)

## A0 — live state verified

```
origin/main  41f77053a19819a36e1a761c698c145bc25e9e6f
PR #17       MERGED 2026-09-07T13:08:22Z
CP-2         Ratified · Date Ratified 2026-08-31 · Immutable Lock YES
             Notes carry RATIFICATION_LODGED_2026-09-07
AC-8         scrypt confirmed live in petcare_api/routers/auth.py::_hash_password
```

### One contradiction, recorded not overwritten

The W0-F pack still reads `W0_F_AGENT_IMPLEMENTATION=NO` — *"No agent lane may
implement it."* That flag was live at the moment this run began.

It is recorded as **superseded for non-production scope only**, by Sponsor
direction of 2026-09-07, in `MVC-W0F-ADDENDUM-001` §3, with each of the pack's
three grounds addressed individually. Two are resolved (the data decision is
made; the irreversible migration is excluded from this run). **The third is not.**

The pack's strongest ground — *"it is the substrate for every security control in
Wave-0; a subtle error does not fail a test, it silently widens authorization"* —
is a statement about the nature of the work, and no ruling can resolve it. It is
answered by method rather than dismissed: every control is an armed negative
control, and a guard that passes without a demonstrated failing perturbation is
not accepted as evidence. A reviewer should read this work with that warning in
mind.

## Sponsor D.21 authority — verbatim

> "Portfolio precedent may establish the temporary operating location, but not
> the final residency destination. MyVetiCare may remain out of Kingdom until the
> approved KSA hosting site is ready, at which point migration to KSA becomes
> mandatory."

```
D21_CURRENT_STATE=TEMPORARY_OUT_OF_KINGDOM_ALLOWED
D21_TARGET_STATE=KSA_MIGRATION_MANDATORY_WHEN_APPROVED_KSA_SITE_READY
D21_PORTFOLIO_PRECEDENT=TEMPORARY_OPERATING_LOCATION_ONLY
D21_PERMANENT_RESIDENCY_PRECEDENT=NO
```

The ruling answers the caution this lane raised in the previous run: siblings run
in `me-central-1` (UAE) while MyVetiCare is a KSA product under PDPL. That region
is now confirmed as an acceptable **temporary operating location** and explicitly
not a permanent residency authority.

The engineering consequence is the substantive one: KSA migration is a
**scheduled certainty, not a contingency**, so hosting location must be
configuration and never semantics.

## Artefacts produced

```
MVC-W0F-ADDENDUM-001                  append-only correction to the sealed pack
MVC-W0F-DATA-STORE-DECISION-001       AWS-managed PostgreSQL-compatible RDBMS
MVC-W0F-SECRET-SOURCE-DECISION-001    Secrets Manager for authority, SSM for config
MVC-W0F-KSA-MIGRATION-READINESS-001   12-step transition specification
MVC-W0F-IDENTITY-MIGRATION-PLAN-001   14-section plan, prepare-only
tests/governance/test_w0f_architecture_contracts.py   11 guards + meta-tests
```

The sealed W0-F pack is **not modified**. Every correction is an addendum.

## Decisions taken

```
W0F_DATA_STORE=AWS_MANAGED_POSTGRESQL_COMPATIBLE_RELATIONAL_SYSTEM_OF_RECORD
W0F_SECRET_AUTHORITY=AWS_SECRETS_MANAGER
W0F_CONFIG_AUTHORITY=AWS_SSM_PARAMETER_STORE
W0F_AC8=SATISFIED_BY_W0J_SCRYPT
PROVISIONED=NO · SECRETS_CREATED=NO · MIGRATION_APPLIED=NO
```

The data-store choice rests on repository evidence, not preference: 30
hand-written SQL migrations, foreign keys enforcing W0-H and W0-I invariants,
`CHECK` constraints already load-bearing (migration 0030 makes a silent
sole-practitioner bootstrap unrepresentable), and transactional requirements from
W0-G's chain and W0-I's time-bounded authority.

The secret split is drawn on **authority, not sensitivity**: a value that lets its
holder act as someone is a secret; a value that says where to look is
configuration.

## Guards — 11, each with a meta-test

`test_w0f_architecture_contracts.py` enforces D.21's portability rules:

| Guard | Property |
|---|---|
| no hardcoded region | a region literal makes the mandatory migration a code change |
| no hardcoded provider endpoint | the same defect wearing a hostname |
| KSA placeholders never assigned | an unapproved destination must not become load-bearing |
| no residency branch | the application must not know its jurisdiction |

Two defects were found in these guards **by their own meta-tests**, and both are
recorded because each would have produced a guard that looked armed:

1. **The residency needle did not match `is_ksa_region()`.** `\bis_ksa\b` fails
   between `a` and `_`, because underscore is a word character. The guard would
   have passed over the exact identifier shape it exists to catch.
2. **The placeholder guard flagged its own meta-test fixture.** `rglob` scans
   `tests/` too, so the planted `TARGET_KSA_REGION_OR_SITE = "me-south-1"` in the
   guard file tripped it. Fixed by exempting **one path** — the guard file itself
   — following the retired-role guard's precedent. It is a single path, not a
   pattern that could hide application code.

Meta-tests deliberately include regions **not in current use**
(`ap-southeast-2`, `sa-east-1`, `af-south-1`, `il-central-1`): a guard that only
knows today's regions prevents repeating a known mistake rather than preventing
the class.

A third property is asserted and matters: the region guard must **not** fire on a
region named in a comment. The data-store decision discusses `me-central-1` by
name while forbidding it in code, and a guard that could not tell those apart
would be widened until it meant nothing.

## Regression

```
governance + root    186 passed   (was 175; +11 architecture contract guards)
serving API           70 passed
runtime              247 passed
secret_scan          SCANNED=3820 ALLOWLISTED=0 FINDINGS=0  CLEAN
prohibited_literal   SCANNED=370  ACTIVE_LITERAL_DEFAULT=0
```

No existing test was modified. `ASSERTIONS_WEAKENED=0`.

## Remaining W0-F scope (PR-B)

```
AC-7 session revocation implementation  designed here, not yet built
secret provider abstraction             contract defined here, not yet built
identity migration schema + dry-run     planned here, not yet authored
W0-G/H/J residue closure                depends on the above
```

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO      LIVE_DB_QUERIED=NO
SECRETS_CREATED=NO      EXTERNAL_DASHBOARD_MUTATED=NO
SEALED_PACK_MODIFIED=NO KSA_PLACEHOLDERS_ASSIGNED=NO
```
