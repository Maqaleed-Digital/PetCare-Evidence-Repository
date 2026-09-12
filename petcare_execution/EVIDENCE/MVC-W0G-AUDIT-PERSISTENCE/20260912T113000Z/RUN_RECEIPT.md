# MyVetiCare — W0-G audit persistence + pre-production convergence, 2026-09-12

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION
RULE_18=RESIDUE_REMEASURED_FROM_LIVE_SOURCE
```

## Terminal state

```
W0F_STATUS=NON_PRODUCTION_IMPLEMENTATION_COMPLETE
W0G_STATUS=READY_PENDING_PRODUCTION_GATE
W0H_STATUS=READY_PENDING_PRODUCTION_GATE
W0J_STATUS=READY_PENDING_PRODUCTION_GATE  + PRE-1
PRE1=AWAITING_SPONSOR_RULING
PRE2=AWAITING_SPONSOR_RULING
SPONSOR_DECISION_PACK=READY
NEXT_GENUINE_GATE=SPONSOR_PREPROD_DECISION_PRE1_PRE2
```

## W0-G closed without approval, because none was required

```
W0G_STARTING_CLASSIFICATION=RESIDUE_REMAINING
W0G_LIVE_FINDING=the authoritative writer was a Python list; no audit repository
                 existed; zero audit_event rows were written by any path
AUDIT_REPOSITORY_IMPLEMENTED=YES
AUDIT_POSTGRES_IMPLEMENTED=YES
AUDIT_SERVING_PATH_WIRED=YES   11 call sites reach the repository
AUDIT_BACKEND_TESTED=POSTGRESQL_AND_IN_MEMORY
W0G_FINAL_STATUS=READY_PENDING_PRODUCTION_GATE
```

Not rounded up. Two items stay open and are NOT claimed closed: ARCH-01
(signatures or anchoring beyond a hash chain — a specification question carried
since W0-G) and `AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN` (thirteen authentication events
that cannot enter a `NOT NULL` tenant column without inventing a tenant).

## Findings this lane produced

```
1  Two functions named `_audit`, one authoritative and one a log line. The
   authentication one is renamed `_log_auth_event`; its thirteen events were
   never in the chain and are recorded as an open gap rather than given a
   default tenant.
2  `audit_chain_durability` was a fixed string that persistence would have made
   FALSE — the MVC-INC-ATTEST-001 defect inverted. Now computed.
3  `audit_event` had no ordering column. `occurred_at` is TEXT, so a tie
   reorders the chain into a verification failure that looks like tampering.
4  The per-test fixture cleared audit rows but not the chain head, so a clean
   chain reported as tampering. Six controls failed together and each passed
   alone.
5  PRE-1: there is NO tenant registry anywhere in the estate. `tenant_id` is an
   unconstrained TEXT column. The only tenant-shaped identifiers live in
   EP-05/EP-06 test fixtures.
6  PRE-1: the three seed identities' password is a tracked literal in a PUBLIC
   repository.
7  PRE-2: there are THREE role vocabularies, not two. The third is
   `petcare_web/middleware.ts`, which is written to alias the MACHINE forms.
8  PRE-2: a full `pharmacy` role surface survives in the web — alias, protected
   route, page, onboarding, home CTA. The retired-role guard cannot see it: its
   needle is `pharmacy_operator` and the web's short form is `pharmacy`.
```

Findings 5–8 are reported, not acted on. Each would change authorization or
product scope.

## Regression

```
ROOT      pytest tests                     228 passed
RUNTIME   pytest petcare_runtime/tests     247 passed
API       pytest petcare_api/tests         245 passed
POSTGRES  four PostgreSQL suites            82 passed
COMPOSITE the CI command                   720 passed     (baseline 698)

prohibited_literal   SCANNED=389   ACTIVE_LITERAL_DEFAULT=0
secret_scan          SCANNED=3876  ALLOWLISTED=0  FINDINGS=0  CLEAN

ASSERTIONS_WEAKENED=0   CONTROLS_REMOVED=0   CONTROLS_STRENGTHENED=1
PERTURBATIONS=7, all proven applied, all restored, 0 vacuous
```

## Boundary

```
PRODUCTION_MUTATED=NO      LIVE_DB_MUTATED=NO
CLOUD_RESOURCE_TOUCHED=NO  EXTERNAL_DASHBOARD_MUTATED=NO
MIGRATION_APPLIED_TO_PRODUCTION=NO   (0032 authored and rehearsed only)
SECRET_CREATED=NO
```
