# MVC-W0F-PRODUCTION-ACTIVATION-001 — production activation pack

**Status:** PREPARED · **NOTHING IN THIS DOCUMENT HAS BEEN EXECUTED**
**Date:** 2026-09-12 · **Authority:** CP-2 (Ratified, immutable),
`MVC-W0F-DATA-STORE-DECISION-001`, `MVC-W0F-SECRET-SOURCE-DECISION-001`,
`MVC-W0F-IDENTITY-MIGRATION-PLAN-001`, `MVC-W0F-KSA-MIGRATION-READINESS-001`,
Sponsor D.21 ruling.

```
DATABASE_PROVISIONED=NO
SECRET_CREATED=NO
SCHEMA_APPLIED=NO
IDENTITY_MIGRATED=NO
SERVING_BOUND_TO_POSTGRES=NO
```

Every command below is written to be run as written. Where a value is not yet
decided it appears as an explicit placeholder in angle brackets, and **no value is
invented** — in particular no region, endpoint, account or KSA target.

---

## Preconditions that are NOT gates, and must be resolved BEFORE the window

Recorded first because each is a decision somebody has to make, and a cutover
window is the worst place to discover one.

### PRE-1 · Sponsor tenant assignment — **BLOCKING for P4**

The dry-run against the live source returns `0` migratable and `3` quarantined,
all `UNRESOLVED_NO_TENANT`. The pilot identities carry no tenant, and the
migration plan forbids inferring one. P4 would migrate nobody.

Required: the Sponsor assigns a tenant to each pilot identity, or states that
production identity is a different set that will be exported separately.

### PRE-2 · CONF-01 role vocabulary — **BLOCKING for a usable P5**

`main.py` seeds `platform_admin` / `veterinarian` / `owner`; `require_role()`
accepts only `Platform Admin` / `Veterinarian` / `Owner`. Seeded identities
authenticate and are then refused by every protected route with
`403 Unknown role`. Binding the serving path to a durable store does not fix
this — it makes it durable.

Required: a Sponsor decision on one vocabulary, and a migration to carry it.
Not taken by any agent lane: it changes who may act.

### PRE-3 · W0-G residue

`W0G_STATUS=RESIDUE_REMAINING`. The audit writer is not wired to the persistence
boundary. It is non-production engineering and needs no gate — but going live
with `audit_chain_persisted=false` is a posture decision that should be made
deliberately rather than noticed afterwards.

### PRE-4 · Session treatment at cutover

`MVC-W0F-KSA-MIGRATION-READINESS-001` §6 requires this be chosen and recorded,
not defaulted. Recommended: **invalidate all sessions** at cutover by rotating
the signing key. AC7-07 is proven on PostgreSQL, so rotation is known to revoke
everything.

### PRE-5 · Engine variant and sizing

`RDS PostgreSQL` vs `Aurora PostgreSQL-compatible` is deferred by the data-store
decision and changes no application code. Someone still has to choose.

---

## PHASE P0 — PRECHECK (read-only; no gate)

```bash
# P0.1 · The approved production account, named by the Sponsor — never inferred
#        from a repository name or a previous session.
aws sts get-caller-identity --profile <APPROVED_PRODUCTION_PROFILE>

# P0.2 · The temporary operating location, per D.21. Recorded, not chosen here.
echo "TEMPORARY_OPERATING_REGION=<APPROVED_TEMPORARY_REGION>"
echo "TARGET_KSA_HOSTING_AUTHORITY=<unapproved>"
echo "TARGET_KSA_REGION_OR_SITE=<unapproved>"
echo "TARGET_KSA_DATABASE_ENDPOINT=<unapproved>"

# P0.3 · The migration chain is intact and matches this commit.
python -m pytest tests/governance/test_migration_invariants.py -q
python scripts/governance/verify_evidence_bundles.py

# P0.4 · The chain replays from empty against a throwaway database.
#        Rehearsed here, so P3 is not the first time it is attempted.
python -m pytest petcare_api/tests/test_postgres_integration.py -q

# P0.5 · Rollback destination exists BEFORE anything is created.
echo "ROLLBACK_PLAN=<snapshot id or 'none yet — P1 creates the first'>"
```

**Exit criterion:** every command above passes and PRE-1..PRE-5 are dispositioned.

---

## PHASE P1 — LIVE DATABASE

> ### ⛔ GATE_LIVE_APPLY
> Provisioning a database is a live apply. Requires Sponsor authorization.

```bash
# P1.1 · Provision. Engine variant per PRE-5; sizing per the operational decision.
aws rds create-db-instance \
  --db-instance-identifier <DB_IDENTIFIER> \
  --engine postgres --engine-version 16 \
  --db-instance-class <INSTANCE_CLASS> \
  --allocated-storage <GB> \
  --master-username <MASTER_USER> \
  --manage-master-user-password \
  --db-subnet-group-name <PRIVATE_SUBNET_GROUP> \
  --vpc-security-group-ids <SG_ID> \
  --no-publicly-accessible \
  --storage-encrypted --kms-key-id <KMS_KEY> \
  --backup-retention-period <DAYS> \
  --enable-performance-insights \
  --region <APPROVED_TEMPORARY_REGION> \
  --profile <APPROVED_PRODUCTION_PROFILE>

# P1.2 · Private access only. Assert it rather than assume it.
aws rds describe-db-instances --db-instance-identifier <DB_IDENTIFIER> \
  --query 'DBInstances[0].{public:PubliclyAccessible,encrypted:StorageEncrypted,backup:BackupRetentionPeriod}'
# REQUIRED: public=false, encrypted=true, backup>0

# P1.3 · Force TLS.
aws rds modify-db-parameter-group --db-parameter-group-name <PG_NAME> \
  --parameters "ParameterName=rds.force_ssl,ParameterValue=1,ApplyMethod=pending-reboot"

# P1.4 · First snapshot, BEFORE any schema. This is P3's rollback point.
aws rds create-db-snapshot --db-instance-identifier <DB_IDENTIFIER> \
  --db-snapshot-identifier <DB_IDENTIFIER>-pre-schema
```

**⚠️ `rds.force_ssl` and the client trust store.** Forcing TLS server-side is not
enough on its own: a client whose trust store lacks the RDS root CA fails to
connect, and the failure reads as a wrong credential. `psycopg` uses the system
trust store; the RDS CA bundle must be present on the runtime image and named in
the connection string (`sslrootcert=`), with `sslmode=verify-full`. Verify with a
throwaway connection before P3 rather than during it.

**Exit criterion:** `describe-db-instances` shows `available`, not public,
encrypted, with backups; a pre-schema snapshot exists.

---

## PHASE P2 — LIVE SECRETS

> ### ⛔ GATE_CREDENTIAL_ENTRY
> Creating or entering secret material is a human act. No agent lane performs it.

```bash
# P2.1 · The database credential. `--manage-master-user-password` in P1.1 already
#        creates one in Secrets Manager; capture its ARN rather than making a
#        second copy. Two copies of one credential means two rotation paths, and
#        a rotation that updates one leaves the other working — indistinguishable
#        from an unrevoked key.
aws rds describe-db-instances --db-instance-identifier <DB_IDENTIFIER> \
  --query 'DBInstances[0].MasterUserSecret.SecretArn'

# P2.2 · The session signing key. Created by a human, never printed.
#        The value must satisfy the provider: non-empty, not a placeholder, and
#        not the retired key — whose fingerprint is in RETIRED_KEY_FINGERPRINTS.
aws secretsmanager create-secret \
  --name <PETCARE_SESSION_SECRET_NAME> \
  --description "MyVetiCare session signing key (W0-A / W0-F)" \
  --kms-key-id <KMS_KEY> \
  --secret-string "<ENTERED_BY_A_HUMAN_AT_THE_TERMINAL>"

# P2.3 · Rotation. Managed rotation is the reason Secrets Manager was chosen
#        over Parameter Store; leaving it unconfigured discards that reason.
aws secretsmanager rotate-secret --secret-id <PETCARE_SESSION_SECRET_NAME> \
  --rotation-rules AutomaticallyAfterDays=<DAYS>

# P2.4 · Bind IDENTIFIERS into the runtime. These are configuration, not secrets:
#        knowing a secret's name grants nothing without permission to read it.
PETCARE_SECRET_MODE=aws_secrets_manager
PETCARE_AWS_REGION=<APPROVED_TEMPORARY_REGION>
PETCARE_SESSION_SECRET_ID=<PETCARE_SESSION_SECRET_NAME>
PETCARE_DB_SECRET_ID=<SECRET_ARN_FROM_P2.1>
PETCARE_PERSISTENCE_MODE=postgres
```

**Do not set `SECRET_KEY` or `PETCARE_DB_URL` in production.** Under
`PETCARE_SECRET_MODE=aws_secrets_manager` the identifiers above are required and
the environment cannot supply the values — that is SEC-SECRET-05 and it is
enforced, not conventional.

**Exit criterion:** the runtime task role can `GetSecretValue` on both secrets and
on nothing else; a throwaway job resolves both and connects.

---

## PHASE P3 — SCHEMA APPLY

> ### ⛔ GATE_LIVE_APPLY

```bash
# P3.1 · Preflight. Reports what WOULD be applied and applies nothing.
python scripts/governance/apply_migrations.py --dry-run
# EXPECT: MIGRATION_TOTAL=36  MIGRATION_PENDING=36  MIGRATION_APPLIED_NOW=0

# P3.2 · Apply. Each migration runs once, in its own transaction, recorded with
#        its SHA-256 in schema_migration.
python scripts/governance/apply_migrations.py
# EXPECT: MIGRATION_APPLIED_NOW=36

# P3.3 · Idempotency, proven on the live target rather than assumed.
python scripts/governance/apply_migrations.py
# EXPECT: MIGRATION_APPLIED_NOW=0  MIGRATION_ALREADY_APPLIED=36

# P3.4 · Verify the schema the application depends on.
psql "$TARGET" -c "\dt user_identity"
psql "$TARGET" -c "\dt app_session"
psql "$TARGET" -c "\dt invite_code"
psql "$TARGET" -c "\dt identity_migration_quarantine"
psql "$TARGET" -tc "SELECT count(*) FROM information_schema.table_constraints
                    WHERE constraint_type='CHECK' AND table_name IN
                    ('user_identity','app_session','invite_code',
                     'identity_migration_quarantine');"
# REQUIRED: >= 10. The CHECK constraints are the structural half of DB-03..DB-05.

# P3.5 · Rollback checkpoint.
aws rds create-db-snapshot --db-instance-identifier <DB_IDENTIFIER> \
  --db-snapshot-identifier <DB_IDENTIFIER>-post-schema
```

**Never run the raw chain with `psql -f` in a loop.** `0001` and `0002` create
nine tables with unguarded `CREATE TABLE`; a re-run fails with `DuplicateTable`
partway through. The runner exists because of this.

**Rollback:** restore `<DB_IDENTIFIER>-pre-schema`. The schema is additive, so
the alternative — removing the four W0-F tables — also works, but a restore is
the rehearsed path.

---

## PHASE P4 — IDENTITY MIGRATION

> ### ⛔ GATE_LIVE_APPLY + GATE_IRREVERSIBLE_ACTION (at step 6)
> **Blocked on PRE-1.** Today this phase migrates 0 and quarantines 3.

```bash
# P4.1 · Snapshot the source. The source is process memory, so "snapshot" means
#        export it to a file that the dry-run and the apply both read — otherwise
#        the set that was reviewed is not the set that is applied.
python scripts/governance/identity_migration_dryrun.py \
  --report evidence/identity-migration-preflight.md

# P4.2 · Dry-run against that snapshot, with the Sponsor-approved tenant map.
python scripts/governance/identity_migration_dryrun.py \
  --source-json <SOURCE_EXPORT.json> \
  --tenant-map <SPONSOR_APPROVED_TENANT_MAP.json> \
  --report evidence/identity-migration-dryrun.md
# REQUIRED: every reconciliation check PASS.

# P4.3 · ⛔ SPONSOR REVIEW of the quarantine set. Every quarantined record gets a
#        recorded disposition. A quarantined identity cannot authenticate, which
#        is the safe direction — leaving one unresolved is a choice, not a
#        pending task.

# P4.4 · Snapshot before the write.
aws rds create-db-snapshot --db-instance-identifier <DB_IDENTIFIER> \
  --db-snapshot-identifier <DB_IDENTIFIER>-pre-identity

# P4.5 · Apply. The target is named EXPLICITLY and is never resolved from
#        configuration — a tool that could find production by reading the same
#        configuration the application reads is one flag away from writing to it.
python scripts/governance/identity_migration_dryrun.py \
  --source-json <SOURCE_EXPORT.json> \
  --tenant-map <SPONSOR_APPROVED_TENANT_MAP.json> \
  --apply --database-url "<EXPLICIT_TARGET_URL>" \
  --report evidence/identity-migration-applied.md

# P4.6 · Reconcile against the database.
psql "$TARGET" -tc "SELECT count(*) FROM user_identity WHERE provenance='IDENTITY_MIGRATION';"
psql "$TARGET" -tc "SELECT reason, count(*) FROM identity_migration_quarantine GROUP BY reason;"
psql "$TARGET" -tc "SELECT count(*) FROM user_identity WHERE tenant_id IS NULL AND provenance='IDENTITY_MIGRATION';"
# REQUIRED: the third is 0 — and the database refuses to let it be anything else.

# P4.7 · No privilege elevation. Compare every migrated role against the source
#        export. `no_role_elevated` in the report asserts it; assert it again
#        here against the rows that actually landed.
```

**⛔ GATE_IRREVERSIBLE_ACTION** applies to decommissioning the in-memory seeding
(plan §9 step 6). That is deliberately last and separately gated; it is **not**
part of this phase.

---

## PHASE P5 — SERVING BINDING

> ### ⛔ GATE_EXTERNAL_DASHBOARD_CONFIG (if the runtime configuration is changed
> through a provider console rather than through infrastructure code)

```bash
# P5.1 · Switch persistence mode and bind identifiers (see P2.4).
#        There is no rollout-by-percentage here: a process either reaches the
#        store or refuses to start.

# P5.2 · Health. A process that cannot reach the store does NOT start, so a task
#        that is running has already proven the connection.
curl -fsS https://<SERVICE>/api/governance/status | jq .

# P5.3 · Sign-in against the persisted store.
curl -fsS -X POST https://<SERVICE>/api/auth/sign-in \
  -H 'content-type: application/json' \
  -d '{"email":"<PILOT_EMAIL>","password":"<ENTERED_BY_A_HUMAN>"}' -i

# P5.4 · The session is a ROW, not an object. Assert it.
psql "$TARGET" -tc "SELECT count(*) FROM app_session WHERE revoked_at IS NULL;"

# P5.5 · Tenant isolation — a session in tenant A must be refused in tenant B
#        with 403 TENANT_SCOPE_DENIED (AC7-02).

# P5.6 · Revocation — revoke one session and confirm the same cookie is refused
#        with 401 SESSION_REVOKED_OR_EXPIRED (AC7-01), and that another user's
#        session still works (AC7-05).

# P5.7 · Emergency key rotation, REHEARSED not executed: rotating
#        PETCARE_SESSION_SECRET_ID invalidates every session while their store
#        records stay active (AC7-07). Record who may trigger it and how long it
#        takes to propagate.
```

**Verify the object state, not the wrapper exit.** A 2xx from a deployment API
means the request was accepted. The assertions above read the database and the
service.

---

## PHASE P6 — CUTOVER

```bash
# P6.1 · Production smoke: the AC-7 suite, run against production as read-mostly
#        checks. Sign-in, protected route, revoke, re-present, confirm denial.
# P6.2 · Rollback decision point.
#          revert P5 configuration        -> back to the previous serving mode
#          restore <DB_IDENTIFIER>-pre-identity -> back to schema-only
#          restore <DB_IDENTIFIER>-pre-schema   -> back to an empty database
#        The seeded in-memory path still exists and is revertible (plan §10).
# P6.3 · Capture evidence: every command's output, the reconciliation reports,
#        the schema_migration ledger, and the snapshot identifiers.
```

---

## PHASE P7 — POST-CUTOVER

```
P7.1  Monitor: connection saturation, session-table growth, expired-session
      accumulation (idx_app_session_expires serves the housekeeping read).
P7.2  Seal evidence. Never rewrite a sealed bundle.
P7.3  The KSA migration obligation remains OPEN.

      D21_CURRENT_STATE=TEMPORARY_OUT_OF_KINGDOM_ALLOWED
      D21_TARGET_STATE=KSA_MIGRATION_MANDATORY_WHEN_APPROVED_KSA_SITE_READY

      Going live does not discharge it and does not extend the temporary
      permission. `MVC-W0F-KSA-MIGRATION-READINESS-001` governs the move;
      KSA-01..06 prove that relocating is a configuration change.
P7.4  W0-G residue remains open (RESIDUE_CLASSIFICATION.md). Until it closes the
      service correctly reports audit_chain_persisted=false.
```

---

## Gate summary

| Phase | Gate |
|---|---|
| P0 | none — read-only |
| P1 | `GATE_LIVE_APPLY` |
| P2 | `GATE_CREDENTIAL_ENTRY` |
| P3 | `GATE_LIVE_APPLY` |
| P4 | `GATE_LIVE_APPLY`; step 6 of plan §9 is `GATE_IRREVERSIBLE_ACTION` |
| P5 | `GATE_EXTERNAL_DASHBOARD_CONFIG` if configured through a console |
| P6 | covered by P4/P5; a cutover that cannot roll back is `GATE_IRREVERSIBLE_ACTION` |
| P7 | none |

```
NEXT_GENUINE_GATE=GATE_LIVE_APPLY (P1 — provision the database)
```

No sixth gate is introduced. Nothing above has been executed.
