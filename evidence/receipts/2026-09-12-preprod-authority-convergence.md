# MyVetiCare — pre-production authority convergence, 2026-09-12

Durable session receipt. Where this disagrees with any summary, transcript or
handoff, the repository and the register outrank it (Rule 14).

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION
RULE_18=RESIDUE_REMEASURED_FROM_LIVE_SOURCE
RULE_19=NO_FALSE_TAMPER_FINDING_UNDER_CORRECT_OPERATION
```

## Heads

```
START_HEAD=e46fb5adc65ad835ea75a6d8098321bd09482b1b
PR23_STATUS=MERGED   PR23_SHA=7d8a36f08339682e90d6b1c71208ffe51ff7d6a2
PR24_STATUS=MERGED   PR24_SHA=e46fb5adc65ad835ea75a6d8098321bd09482b1b
PR25=wave0/preprod-authority-convergence
END_HEAD=<PR #25 merge commit>
```

## PRE-1

```
PRE1_RULING=1-B
PRE1_IMPLEMENTED=YES
SEED_IDENTITIES_FOUND=3
SEED_IDENTITIES_DISCARDED=3
SEED_RUNTIME_PATH_PRESENT=NO
PUBLISHED_SEED_PASSWORD_LIVE_PATH=NO
```

The seed password was a literal in a PUBLIC repository. W0-F's persistence is what
would have made it permanent: every boot of a durable deployment would have
written three accounts with a published credential into the identity store, one
of them holding the highest role in the system.

## PRE-2

```
PRE2_RULING=2-C
PRE2_IMPLEMENTED=YES
CANONICAL_ROLE_IDS=platform_admin · partner_clinic_admin · veterinarian · owner
DISPLAY_ROLE_AUTHORITY_USAGE=0
CONF01_STATUS=CLOSED
```

Proven through the real registration endpoint, not a fixture. The two 403s that
bracket the change mean opposite things: `Unknown role` said the system rejected
its own vocabulary; `NO_TENANT_AUTHORITY` says this identity has no scope yet.

`petcare_runtime` was NOT rewritten: its role tokens are its own vocabulary, it
has 247 tests, and the serving layer never called its authorizer.

## Pharmacy

```
PHARMACY_ROLE_RULING=REMOVE
PHARMACY_ROLE_PRESENT=NO
PHARMACY_OPERATOR_PRESENT=NO   (as an authorization principal)
PHARMACY_DOMAIN_CAPABILITIES=REBOUND_OR_EXPLICITLY_NON_AUTHORITATIVE
PHARMACY_PENDING_BINDINGS=3
  the /pharmacy page's safety-check and cold-chain regions (no governed backend action)
  access_control.ROLE_PHARMACY_OPERATOR      dead constant, registered pending
  ai_hitl CONTEXT_ROLE_MAP `pharmacist`      reviewer routing, registered pending
```

`/pharmacy` is rebound to the veterinarian — the actor the backend already proves
may dispense (T-DISP-01). No `pharmacist` or `pharmacy` role was invented.

## Tenant registry

```
TENANT_REGISTRY_IMPLEMENTED=YES
TENANT_ROWS_CREATED=0
TENANT_DEFAULT_PRESENT=NO
TENANT_INFERENCE_PRESENT=NO
AUDIT_EVENT_TENANT_FK=ABSENT_BY_DESIGN
```

Migration 0034: `tenant` table, FKs from `user_identity` and `app_session`, NULL
still permitted because the tenantless identity is a governed state. `audit_event`
has no FK — it legitimately holds `UNATTRIBUTED`, and adding one would require a
fake tenant every unauthenticated probe event appeared to belong to.

## Identity migration

```
IDENTITY_MIGRATION_REHEARSAL=PASS_EMPTY_BY_DESIGN
IDENTITY_SOURCE_SEEDS=0
IDENTITY_DISCARDED_SEEDS=3
IDENTITY_MIGRATABLE=0
IDENTITY_QUARANTINED=0
```

`SOURCE=0`, not `QUARANTINED=3`. A quarantine of three is a backlog somebody must
disposition before a cutover; a source of zero is a migration with nothing to do.

```
END_TO_END_IDENTITY_PROOF=PASS
  registration -> canonical role -> deliberate tenant assignment -> session ->
  permitted route 201 -> audit_event persisted -> chain verified ->
  cross-tenant denied -> revoked -> denied
  SEED_HELPER_USED=NO  DIRECT_DB_FIXTURE_FOR_THE_USER=NO
```

## Audit and ARCH-01

```
AUDIT_INTEGRATION_RESULT=PASS
ARCH01_STATUS=OPEN
  AUDIT_CHAIN_INTEGRITY=IMPLEMENTED
  AUDIT_WRITE_AUTHORITY=SERVER_ESTABLISHED
  SIGNATURE_ANCHORING=OPEN
```

A valid hash chain is not write authenticity, and nothing here closes that.

## Residue — Rule 18, re-measured from live source

```
W0F_STATUS=READY_PENDING_PRODUCTION_GATE
W0G_STATUS=READY_PENDING_PRODUCTION_GATE
W0H_STATUS=READY_PENDING_PRODUCTION_GATE
W0J_STATUS=READY_PENDING_PRODUCTION_GATE
```

W0-J's `+ PRE-1` qualifier is discharged. None is CLEAN, and none is claimed to be.

## Credentials

```
LIVE_APPLICATION_CREDENTIAL_LITERAL_COUNT=0   (239 serving files scanned)
GITHUB_SUPPORT_STATUS=GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
```

The retired credential is gone from the working tree. It remains in this PUBLIC
repository's git history; that is an external-account action, untouched here and
not claimed closed.

## Regression

```
REGRESSION_TOTALS
  ROOT      pytest tests                  242 passed
  RUNTIME   pytest petcare_runtime/tests  247 passed
  API       pytest petcare_api/tests      313 passed
  COMPOSITE the CI command                802 passed      (baseline 720)
  242 + 247 + 313 = 802 — the per-suite sum check

POSTGRES_TOTALS
  test_postgres_integration            35
  test_session_store_postgres_e2e      13
  test_identity_migration_postgres     12
  test_audit_persistence_postgres      22
  test_tenant_registry                 18
  test_end_to_end_identity_postgres     3
  TOTAL                               103 passed
  MIGRATIONS_IN_CHAIN=39  REPLAYED_CLEANLY=39  TENANT_ROWS_AFTER_REPLAY=0
  LIVE_DB_TOUCHED=NO

  prohibited_literal SCANNED=399  ACTIVE_LITERAL_DEFAULT=0
  secret_scan        SCANNED=3923 FINDINGS=0  CLEAN
  evidence bundles   BUNDLES=29  ARTEFACTS=201  FAILED=0

  CI on #25: 795 passed + 7 pre-existing skips = 802; PostgreSQL step 82/0
             skipped; TypeScript clean; web unit 120; responsive 90.

  ASSERTIONS_WEAKENED=0  CONTROLS_REMOVED=0  CONTROLS_STRENGTHENED=2

PERTURBATION_TOTALS
  9 probes · MARKER_VERIFIED=9/9 · DIFF_VERIFIED=9/9
  CONTROL_FAILED_AS_REQUIRED=9/9 · RESTORED_PASS=9/9 · VACUOUS=0
```

## Evidence

```
EVIDENCE_DIR=petcare_execution/EVIDENCE/MVC-PREPROD-AUTHORITY-CONVERGENCE/20260912T124500Z
EVIDENCE_SHA256=EVIDENCE_SHA256.txt in that directory (15 artefacts)
```

## Findings — recorded, not quietly fixed

```
1  `ROLE_ALIAS[rawRole] ?? rawRole` passed an UNMAPPED role through, so a cookie
   carrying `admin` opened the admin surface. Fixed to `?? ''`.
2  SEED-01 measured the suite rather than the startup path. Now a subprocess.
3  SEED-02c could not see its own perturbation: a negative lookbehind meant to
   skip `password_hash` skipped `DEFAULT_ADMIN_PASSWORD` too.
4  The perturbation harness falsely rejected INSERTION probes, because the
   replacement text necessarily contains the original.
5  The CI non-skip guard fell behind a SECOND time — four suites named, two added.
6  `TENANT_ASSIGNMENT_HAS_NO_GOVERNED_API`: registration cannot assign a tenant
   and no admin route does.
7  `PILOT_INVITE_CODES_ARE_PUBLIC_LITERALS`: OWNER-PILOT-001 / VET-PILOT-001 are
   still seeded at startup from source literals in a PUBLIC repository. Outside
   the ruling's scope; removing invite-gated registration is a product act.
```

## State

```
PRODUCTION_ACTIVATION_PACK=petcare_execution/GOVERNANCE/MVC-W0F-PRODUCTION-ACTIVATION-001/
PRODUCTION_ACTIVATION_READINESS=READY

OPEN_ENGINEERING_RESIDUE
  ARCH-01 signatures/anchoring (specification)
  AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN (needs a governed answer, not code)
  TENANT_ASSIGNMENT_HAS_NO_GOVERNED_API (blocks a usable P5)
  CLINICAL_SERVING_PERSISTENCE (outside W0-F/W0-G)

OPEN_SPONSOR_DECISIONS
  PRE-2D  the pharmacy product surface's long-term disposition
  PRE-4   session treatment at cutover (invalidate vs continuity)
  PRE-5   engine variant and sizing
  the first production tenant (a Sponsor act; the registry ships empty)

OPEN_PRODUCTION_GATES
  GATE_LIVE_APPLY          provision · apply schema · create the first tenant
  GATE_CREDENTIAL_ENTRY    create the session signing secret
  GATE_IRREVERSIBLE_ACTION decommission the in-memory seeding path

NEXT_GENUINE_GATE=GATE_LIVE_APPLY   (P1 — provision the database)
```
