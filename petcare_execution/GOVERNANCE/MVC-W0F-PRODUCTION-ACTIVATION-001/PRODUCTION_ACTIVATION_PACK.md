# MVC-W0F-PRODUCTION-ACTIVATION-001 — production activation pack

**Status:** PREPARED · **NOTHING IN THIS DOCUMENT HAS BEEN EXECUTED**
**Date:** 2026-09-12 · **Revised** 2026-09-12 after
`MVC-PREPROD-SPONSOR-DECISION-PACK-001` was ruled
(`PRE1=1-B`, `PRE2=2-C`, `PHARMACY_ROLE=REMOVE`,
`PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING`,
`TENANT_REGISTRY_STATUS=REQUIRED_FOUNDATION`) · **Authority:** CP-2 (Ratified, immutable),
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

## Preconditions — status after the ruling

### PRE-1 · tenant assignment — **CLOSED (ruled 1-B)**

The three seed identities are discarded. They are not migrated, the startup path
that created them is removed, and their published password is gone from serving
source. **The identity migration is now empty BY DESIGN**, not blocked.

A tenant registry foundation exists (`0034`) and ships **empty**: a tenant is now
a governed object that must exist before an identity can be assigned to it, and
no production tenant has been created.

### PRE-2 · CONF-01 role vocabulary — **CLOSED (ruled 2-C)**

Machine role IDs are the sole authorization authority. `require_role()`, the
storage catalogue (`0033`), registration, sessions and the web middleware all
compare the same four tokens. Display labels are presentation only, and
`ROLE-09` asserts that renaming one changes no authorization outcome.

Verified end to end: a registered identity now reaches its permitted route
instead of `403 Unknown role`.

### PRE-3 · W0-G residue — **CLOSED**

`W0G_STATUS=READY_PENDING_PRODUCTION_GATE`. The audit chain is persisted behind
a repository, proven on PostgreSQL. `audit_chain_persisted` is computed from the
configured store rather than asserted.

### PRE-2D · the pharmacy product surface — **OPEN, and not blocking**

`pharmacy` is no longer an authorization principal anywhere in the serving
surface. The product surface is retained and rebound: `/pharmacy` is now guarded
by the veterinarian, the actor the backend already proves may dispense.

What remains open is the surface's long-term disposition, and two occurrences in
`petcare_runtime` that authorize nothing today — a dead `ROLE_PHARMACY_OPERATOR`
constant and a HITL reviewer map naming `pharmacist`. Both are registered with
their reasons in `tests/governance/test_retired_role_family.py`.

### PRE-6 · tenant assignment — **AN AUTHORITY DECISION, not an engineering gap**

Registration establishes identity and never tenant authority (W0-C), and no route
assigns, changes or revokes tenant membership. The only path today is an operator
calling the identity repository directly — sufficient for a rehearsal, and not a
governed operating model: no audit event, no authorization check, no revocation
path.

**Reclassified.** This was recorded as a gap for engineering to close. It is
first a question of WHO may assign tenant membership, and that is constitutional:
tenant membership determines which data an identity can reach at all, which is a
stronger power than any route guard currently grants.

`platform_admin` is the obvious holder and that is precisely why it is not
assumed here. A least-effort answer adopted silently becomes constitutional
authority by accident.

The control path this needs, once the authority is decided:

```
authorized actor → governed assignment API → explicit identity → explicit tenant
  → authorization check → audit event → durable write → verification/revocation
```

Every element has an implementation to reach (`require_role`,
`AUDIT_REPO.append_event`, `PostgresIdentityRepository`, `tenants.is_assignable`).
What is missing is the ruling.

**P1 must not be authorized before this is decided**, because a run that
proceeded would arrive at P5 with tenant membership granted by whoever can reach
the repository. See `PREPROD_DECISION_BOARD-001.md` item 3.

### PRE-4 · Session treatment at cutover — **UNRESOLVED**

`MVC-W0F-KSA-MIGRATION-READINESS-001` §6 requires this be chosen and recorded,
not defaulted. Recommended there: **invalidate all sessions** by rotating the
signing key. AC7-07 is proven on PostgreSQL, so rotation is known to revoke
everything.

**Two corrections to how this was framed here.**

1 · **The continuity option is not currently implementable.** §6 makes it
conditional on "the previous-key question" being settled, and the serving path
has no previous-key acceptance list — `PREVIOUS_KEY_LIST_PRESENT=NO`, recorded in
the W0-F PR-B receipt and still true in live source. Choosing continuity selects
engineering work, not only a policy.

2 · **At go-live it is close to vacuous.** Sessions today live in process memory,
so switching to the persistent store leaves nothing to preserve. The decision
becomes live for the KSA migration and for any emergency key rotation after it.
It is a standing policy, not a go-live step.

See `MVC-PREPROD-SPONSOR-DECISION-001/PREPROD_DECISION_BOARD-001.md` item 4.

### PRE-5 · Engine variant and sizing — **UNRESOLVED**

`RDS PostgreSQL` vs `Aurora PostgreSQL-compatible` is deferred by the data-store
decision and changes no application code. Someone still has to choose.

Both offer PostgreSQL 16, which is the version this estate is proven against.
Both carry the same client-side TLS trap recorded in P1. Nothing in the
repository expresses a preference, and no code path branches on the variant —
which is the D.21 portability property working.

See `PREPROD_DECISION_BOARD-001.md` item 5.

---

## PHASE P0 — PRECHECK (read-only; no gate)

```bash
# P0.0 · The post-ruling invariants. Each is a control that already runs in CI;
#        listed here so a go-live operator verifies them on the exact commit
#        being deployed rather than trusting that they once passed.
python -m pytest petcare_api/tests/test_seed_retirement.py -q     # no runtime seed users,
                                                                  # no credential literal
python -m pytest petcare_api/tests/test_role_authority.py -q      # machine-role authority,
                                                                  # CONF-01 closed, no pharmacy role
python -m pytest petcare_api/tests/test_tenant_registry.py -q     # tenant is a governed object
python -m pytest tests/governance/test_retired_role_family.py -q  # no retired principal
python -m pytest petcare_api/tests/test_end_to_end_identity_postgres.py -q

# The identity rehearsal must be EMPTY. Not "zero migratable because everything
# quarantined" — zero source, because nothing is seeded (PRE1_RULING=1-B).
python scripts/governance/identity_migration_dryrun.py
# EXPECT: IDENTITY_SOURCE_COUNT=0  MIGRATABLE=0  QUARANTINED=0

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
#        its SHA-256 in schema_migration. The chain now includes the audit
#        persistence (0032), the canonical role catalogue (0033) and the tenant
#        registry (0034).
python scripts/governance/apply_migrations.py
# EXPECT: MIGRATION_APPLIED_NOW=39

# 0033 NARROWS the stored role catalogue and ADD CONSTRAINT validates existing
# rows. Against an empty database it cannot fail. Against a database that already
# holds identities, a failure here means a row carries a display spelling whose
# authority this ruling changed — and that failure is the finding, not an
# obstacle to work around.

# P3.3 · Idempotency, proven on the live target rather than assumed.
python scripts/governance/apply_migrations.py
# EXPECT: MIGRATION_APPLIED_NOW=0  MIGRATION_ALREADY_APPLIED=36

# P3.4 · Verify the schema the application depends on.
psql "$TARGET" -c "\dt tenant"
psql "$TARGET" -c "\dt audit_chain_head"
psql "$TARGET" -tc "SELECT count(*) FROM tenant;"
# REQUIRED: 0. The registry ships empty; creating a tenant is a Sponsor act.
psql "$TARGET" -tc "SELECT pg_get_constraintdef(oid) FROM pg_constraint
                    WHERE conname = 'user_identity_role_check';"
# REQUIRED: exactly platform_admin, partner_clinic_admin, veterinarian, owner.
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
>
> **PRE-1 is ruled 1-B: there is nothing to migrate.** The seed identities are
> discarded and the application seeds none, so the rehearsal reports
> `SOURCE=0, MIGRATABLE=0, QUARANTINED=0` — empty and correct.
>
> This phase therefore does NOT run at go-live unless a real identity export
> exists. If one ever does, every step below applies unchanged, and
> `TENANT-10` means each source tenant must be a registered tenant BEFORE the
> apply — the foreign key refuses the write otherwise.
>
> **Production identity is created through the governed invite-gated
> registration path**, then assigned a tenant deliberately. See PRE-6: that
> assignment has no governed API yet.

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
# P5.0 · Create the first tenant(s). A Sponsor act: the registry ships empty and
#        nothing infers a tenant. Until one exists, every identity is tenantless
#        and fails closed at require_tenant() with 403 NO_TENANT_AUTHORITY —
#        which is correct, and is not a defect to debug during the window.
#
#        ⛔ This is a live write. GATE_LIVE_APPLY.

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

## Authorization status

```
PRE_1_PRE_2_PHARMACY=RATIFIED   [SPONSOR] 12 September 2026
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
GATE_IRREVERSIBLE_ACTION=NOT_AUTHORIZED
```

The ratification states its own boundary: it ratifies the implementations merged
under PRE-1 and PRE-2 and authorizes no live apply, no secret creation, no
cutover and no irreversible action. Four board items remain open, and item 3 is
an authority decision that blocks a usable P5.

## What changed in this revision

```
PRE-1  CLOSED (1-B)   the migration is empty by design, not blocked
PRE-2  CLOSED (2-C)   one authority vocabulary; CONF-01 closed end to end
PRE-3  CLOSED         audit chain persisted
PRE-4  unchanged      session treatment at cutover — still a decision to record
PRE-5  unchanged      engine variant and sizing
PRE-2D OPEN           pharmacy surface disposition; not blocking
PRE-6  NEW            tenant assignment has no governed API; blocks a usable P5
```
