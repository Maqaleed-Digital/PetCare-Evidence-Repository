# MyVetiCare — W0-F persistence readiness (PR-E), 2026-09-12

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_MUST_BE_PROVEN_APPLIED_BEFORE_ADJUDICATION
```

This bundle covers the whole W0-F non-production run. PR-D built the secret
provider and the PostgreSQL adapter; PR-E adds the identity migration rehearsal,
the KSA portability proof, the residue reclassification and the production
activation pack.

## Terminal state

```
W0F_NON_PRODUCTION_IMPLEMENTATION=COMPLETE
PRODUCTION_ACTIVATION_PACK=READY
NEXT_GENUINE_GATE=GATE_LIVE_APPLY   (P1 — provision the database)
```

## Preflight, verified live before editing

```
START_HEAD=cb5f165a37c2337594222c985f7d7f6003296db0
PR18=MERGED  ad10910cdc4b69be743490eb2b6fef50aaa7cb6f
PR19=MERGED  22c9efe0ed79c2db4a9106d03169ce061b12a52b
PR20=MERGED  cb5f165a37c2337594222c985f7d7f6003296db0
SESSION_STORE_WIRED=YES
AC7_07_PRESENT=YES
SUPERSEDING_GOVERNANCE_DECISION=NONE
BASELINE_REGRESSION=520 passed
```

## Results

```
SECRET_PROVIDER_IMPLEMENTED=YES
POSTGRES_ADAPTER_IMPLEMENTED=YES
POSTGRES_TEST_BACKEND=POSTGRESQL (16.11 local ephemeral / postgres:16 in CI)
LIVE_DB_TOUCHED=NO
LIVE_SECRET_CREATED=NO
MIGRATION_CHAIN=36 applied cleanly from empty
AC7_01..07=PASS_ON_POSTGRES
KEY_ROTATION_POSTGRES_RESULT=PASS
KEY_ROTATION_PG_STORE_RECORD_ACTIVE_DURING_TEST=YES
DENIAL_SOURCE=SIGNATURE_VERIFICATION
IDENTITY_MIGRATION_DRYRUN=PASS
KSA_PORTABILITY_PROOF=PASS
REGRESSION=698 passed (228 / 247 / 223)
PERTURBATIONS=12, all proven applied, all restored, 0 vacuous
ASSERTIONS_WEAKENED=0
```

## The three things a reader should carry away

### 1 · The identity migration migrates nobody today

```
IDENTITY_SOURCE_COUNT=3  MIGRATABLE=0  QUARANTINED=3 (all UNRESOLVED_NO_TENANT)
```

The pilot identities carry no tenant assignment and the plan forbids inferring
one. The migration is correct; the estate is not ready. `P4` of the activation
pack cannot produce a useful result until the Sponsor assigns tenants.

### 2 · W0-G is NOT merely gated

The previous classification said it waited on a live apply. It waits on an
unwritten adapter: the audit writer is still a Python list and no `audit_event`
row is ever written. Calling it `READY_PENDING_PRODUCTION_GATE` would put
non-production engineering behind an approval that was never the blocker.

### 3 · CONF-01 will become durable if it is not decided first

Seeded identities authenticate and are then refused by every protected route.
Binding the serving path to a durable store does not fix that — it persists it.

## Everything else that was found

See `POSTGRES_INTEGRATION_RESULTS.md` (the chain is not re-runnable and had no
runner), `REGRESSION_RESULTS.md` (`pytest tests` failed while CI's command
passed), `KSA_PORTABILITY_RESULTS.md` (the portability guard did not scan
`scripts/`), `SESSION_REVOCATION_POSTGRES.md` (registration issued unusable
sessions; spent invite codes returned on restart).

## Not done, and gated

```
DATABASE_PROVISIONED=NO            GATE_LIVE_APPLY
SCHEMA_APPLIED_TO_PRODUCTION=NO    GATE_LIVE_APPLY
SECRET_CREATED=NO                  GATE_CREDENTIAL_ENTRY
IDENTITY_MIGRATION_APPLIED=NO      GATE_LIVE_APPLY + GATE_IRREVERSIBLE_ACTION
SEEDING_DECOMMISSIONED=NO          GATE_IRREVERSIBLE_ACTION
```

Nothing in `PRODUCTION_ACTIVATION_PACK.md` has been executed.
