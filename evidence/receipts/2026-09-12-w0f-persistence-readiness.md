# MyVetiCare — W0-F persistence readiness, 2026-09-12

Durable session receipt. Where this disagrees with any summary, transcript or
handoff, the repository and the register outrank it (Rule 14).

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_MUST_BE_PROVEN_APPLIED_BEFORE_ADJUDICATION
```

## Heads

```
START_HEAD=cb5f165a37c2337594222c985f7d7f6003296db0
PR_D_COMMIT=879061d   (branch wave0/w0f-persistence-adapter)
PR_E_COMMIT=38d67f6   (branch wave0/w0f-identity-migration-dryrun)
END_HEAD=NOT_YET_MERGED — see MERGE below
```

## Prior state, verified live before editing

```
PR18=MERGED  ad10910cdc4b69be743490eb2b6fef50aaa7cb6f  2026-09-07T14:00:39Z
PR19=MERGED  22c9efe0ed79c2db4a9106d03169ce061b12a52b  2026-09-07T14:12:33Z
PR20=MERGED  cb5f165a37c2337594222c985f7d7f6003296db0  2026-09-07T14:58:53Z
SESSION_STORE_WIRED=YES
AC7_07_PRESENT=YES
SUPERSEDING_GOVERNANCE_DECISION=NONE
BASELINE_REGRESSION=520 passed
```

Live state matched the instruction's expectations exactly; no completed work was
redone.

## PRs

```
NEW_PRS_CREATED=2
  #21  wave0/w0f-persistence-adapter          B6 + B7
  #22  wave0/w0f-identity-migration-dryrun    stacked on #21
NEW_PRS_MERGED=0
```

### MERGE — the one thing this run could not do

```
MERGE_BLOCKED_BY=CLAUDE_CODE_AUTO_MODE_CLASSIFIER
MERGE_BLOCKED_BY_GOVERNANCE=NO
```

`gh pr merge` is refused by the harness classifier in this environment. That is a
tooling restriction, **not** a gate: DL-OPS-FASTLANE-001 gates merge to main only
when evidence is INCOMPLETE, and the evidence here is complete. Both PRs require a
Sponsor merge. #21 first, then #22 retargets to `main` automatically.

## Secrets

```
SECRET_PROVIDER_IMPLEMENTED=YES
SECRET_AUTHORITY=AWS_SECRETS_MANAGER
CONFIG_AUTHORITY=AWS_SSM_PARAMETER_STORE_FOR_NON_SECRET_CONFIGURATION_ONLY
SECRET_FAIL_CLOSED=YES
LIVE_SECRET_CREATED=NO
LIVE_AWS_CALL_MADE=NO
```

## Data store

```
POSTGRES_ADAPTER_IMPLEMENTED=YES
POSTGRES_TEST_BACKEND=POSTGRESQL
POSTGRES_TEST_VERSION=16.11 (local ephemeral) / postgres:16 (CI service)
POSTGRES_TEST_LOCATION=LOCAL_EPHEMERAL
LIVE_DB_TOUCHED=NO
SQLITE_SUBSTITUTED_FOR_POSTGRES=NO
POSTGRES_MIGRATION_CHAIN=36 applied cleanly from empty
POSTGRES_REPOSITORY_TESTS=35 passed
MIGRATION_RUNNER=scripts/governance/apply_migrations.py (new — the estate had none)
```

## Sessions

```
SESSION_STORE_BACKEND_TESTED=POSTGRESQL_AND_IN_MEMORY
AC7_01=PASS_ON_POSTGRES   revoked session denied over the wire
AC7_02=PASS_ON_POSTGRES   tenant-A session denied in tenant B
AC7_03=PASS_ON_POSTGRES   expired session denied server-side
AC7_04=PASS_ON_POSTGRES   unknown/deleted session denied
AC7_05=PASS_ON_POSTGRES   one user's revocation leaves another active
AC7_06=PASS_ON_POSTGRES   individual revocation needs no key rotation
AC7_07=PASS_ON_POSTGRES   key rotation invalidates pre-rotation sessions

KEY_ROTATION_POSTGRES_RESULT=PASS
KEY_ROTATION_PG_STORE_RECORD_ACTIVE_DURING_TEST=YES
KEY_ROTATION_DENIAL_SOURCE=SIGNATURE_VERIFICATION
P_SESSION_ROTATE_PG_01_RESULT=FAILED_AS_REQUIRED (2 controls failed; restored 13 passed)
```

## Identity migration

```
IDENTITY_MIGRATION_DRYRUN=PASS
IDENTITY_SOURCE_COUNT=3
IDENTITY_MIGRATABLE_COUNT=0
IDENTITY_QUARANTINED_COUNT=3      all UNRESOLVED_NO_TENANT
IDENTITY_REJECTED_COUNT=0
IDENTITY_MIGRATION_APPLIED=NO

ROLE_ELEVATION_GUARD=ENFORCED  (MIG-03, armed by perturbing the map)
UNKNOWN_TENANT_GUARD=ENFORCED  (MIG-04)
DUPLICATE_IDENTITY_GUARD=ENFORCED  (MIG-06; every side quarantined)
```

**The live source migrates nobody.** The pilot identities carry no tenant and the
plan forbids inferring one. A production run today would quarantine everybody.

```
W0J_PRECONDITION=SPONSOR_TENANT_ASSIGNMENT_FOR_PILOT_IDENTITIES
```

## Residency

```
D21_CURRENT_STATE=TEMPORARY_OUT_OF_KINGDOM_ALLOWED
D21_TARGET_STATE=KSA_MIGRATION_MANDATORY_WHEN_APPROVED_KSA_SITE_READY
KSA_PORTABILITY_PROOF=PASS
KSA_TARGET_INVENTED=NO
```

## Wave-0 residue

```
W0F_STATUS=NON_PRODUCTION_IMPLEMENTATION_COMPLETE
W0G_STATUS=RESIDUE_REMAINING — the audit writer is not wired to the persistence
           boundary; non-production engineering, no gate needed
W0H_STATUS=READY_PENDING_PRODUCTION_GATE
W0J_STATUS=READY_PENDING_PRODUCTION_GATE + a Sponsor tenant decision
```

## Production readiness

```
PRODUCTION_ACTIVATION_PACK=READY
PRODUCTION_ACTIVATION_READINESS=READY_PENDING_SPONSOR_AUTHORIZATION
PACK=petcare_execution/GOVERNANCE/MVC-W0F-PRODUCTION-ACTIVATION-001/
PACK_EXECUTED=NO
```

## Regression

```
tests (root + governance)   228 passed
petcare_runtime/tests       247 passed
petcare_api/tests           223 passed
COMBINED (the CI command)   698 passed        (baseline 520)

prohibited_literal   SCANNED=385   ACTIVE_LITERAL_DEFAULT=0
secret_scan          SCANNED=3854  ALLOWLISTED=0  FINDINGS=0  CLEAN
evidence bundles     BUNDLES=27  ARTEFACTS=174  FAILED=0

CI on #21: verify SUCCESS; PostgreSQL step 48 passed / 0 skipped;
           TypeScript clean; web unit 120 passed; responsive 90 passed.
CI pre-existing skips: 7, all test_cross_repository_traceability.py (sibling
           repo absent on a runner). Present identically on the cb5f165a
           baseline; this change contributes 0.

ASSERTIONS_WEAKENED=0
CONTROLS_REMOVED=0
CONTROLS_STRENGTHENED=1   T-DISP-05
```

## Perturbations

```
PERTURBATION_TOTAL=12
PROBE_MARKER_VERIFIED=12/12
DIFF_VERIFIED=12/12         by content diff, not git diff
CONTROL_FAILED_AS_REQUIRED=12/12
RESTORED_PASS=12/12
VACUOUS_CONTROLS=0
NO_EVIDENCE_RESULTS=0
```

The first harness run falsely rejected five of six probes because it verified by
`git diff`, which reports nothing for an untracked file — the same false-negative
shape Rule 17 exists to prevent, pointing the other way.

## Findings — recorded, not quietly fixed

```
1  The migration chain is not re-runnable and the estate had no runner.
   Repaired with a ledger, not by editing 36 historical migrations.
2  `pytest tests` FAILED while the combined command CI runs PASSED. Green CI
   would have hidden it. Bootstrap moved to the root conftest.
3  CONF-01 is live: seeded identities authenticate and are then refused by every
   protected route. NOT resolved — it changes who may act.
4  Registration minted a cookie with no session id; every protected route
   returned 401 while /api/auth/me answered 200. Fixed.
5  A consumed invite code became spendable again on restart. Fixed.
6  The portability guard was not scanning `scripts/`. Fixed.
7  The pool `configure` hook left connections in a transaction, presenting a
   reachable database as unreachable. Fixed.
8  W0-G was classified as gated; it has unwritten code. Reclassified.
9  Five evidence/receipts/2026-09-07-*.md are untracked — the durable record of
   merged work is not in the repository. Raised, not committed by this run.
```

## Evidence

```
EVIDENCE_DIR=petcare_execution/EVIDENCE/MVC-W0F-PERSISTENCE-READINESS/20260912T100000Z
EVIDENCE_SHA256=EVIDENCE_SHA256.txt in that directory (11 artefacts)
ADAPTER_BUNDLE=petcare_execution/EVIDENCE/MVC-W0F-PERSISTENCE-ADAPTER/20260912T093000Z
```

## Gates

```
OPEN_GATES
  GATE_LIVE_APPLY          P1 provision · P3 schema apply · P4 identity migration
  GATE_CREDENTIAL_ENTRY    P2 session signing secret
  GATE_EXTERNAL_DASHBOARD_CONFIG   P5, if configured through a console
  GATE_IRREVERSIBLE_ACTION P4 step 6 (decommission seeding) · an unrecoverable cutover

NEXT_GENUINE_GATE=GATE_LIVE_APPLY   (P1 — provision the database)

DECISIONS THAT ARE NOT GATES AND BLOCK USEFUL EXECUTION
  PRE-1  Sponsor tenant assignment for the pilot identities   (blocks P4)
  PRE-2  CONF-01 role vocabulary                              (blocks a usable P5)
  PRE-3  W0-G residue / audit persistence posture
  PRE-4  session treatment at cutover
  PRE-5  engine variant and sizing
```

```
GITHUB_SUPPORT_STATUS=NOT_TOUCHED_BY_THIS_RUN (parallel housekeeping, as instructed)
```
