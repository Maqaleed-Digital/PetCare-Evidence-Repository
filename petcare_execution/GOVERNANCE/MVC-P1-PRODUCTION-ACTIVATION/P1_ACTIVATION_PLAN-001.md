# MVC-P1-ACTIVATION-PLAN-001 — the exact P1 runbook

**Status:** PREPARED · **NOTHING BELOW HAS BEEN EXECUTED**
**Prepared:** 2026-09-12 · **Evidence base:** `1531d2c79df67368a910d4681d376be0e9eab794`
**Authority consumed:** `RATIFICATION-001` · `RATIFICATION-002` · `RATIFICATION-003`

```
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
```

Every value below is either taken from a ratified record or marked
`<INPUT_REQUIRED>`. **Nothing is invented.** AWS read-only discovery returned
`NOT_AVAILABLE` — the CLI is installed and no credentials are configured, and
none were requested — so no account, VPC, subnet, security-group or endpoint
identifier could be read. Each therefore appears as an input, not a decision.

---

## Ratified inputs — settled, do not re-decide

```
ENGINE_VARIANT=RDS_POSTGRESQL              RATIFICATION-002 item 5
POSTGRESQL_MAJOR_VERSION=16                RATIFICATION-002 item 5
SESSION_POLICY=INVALIDATE_ALL              RATIFICATION-002 item 4
PREVIOUS_KEY_ACCEPTANCE_LIST=NOT_AUTHORIZED
TENANT_ASSIGNMENT_AUTHORITY=platform_admin RATIFICATION-002 item 3
AUDIT_MODEL=TWO_EVENT
FIRST_PRODUCTION_TENANT_ID=pharmacare_riyadh          RATIFICATION-003
FIRST_PRODUCTION_TENANT_DISPLAY_NAME=Pharma Care Pharmacies — Riyadh
SEED_IDENTITIES=DISCARDED                  RATIFICATION-001 (PRE-1 1-B)
ROLE_AUTHORITY=machine ids only            RATIFICATION-001 (PRE-2 2-C)
RESIDENCY=TEMPORARY_OUT_OF_KINGDOM_ALLOWED, KSA migration mandatory when the
          approved site is ready                              D.21
```

## Operational inputs — REQUIRED, and deliberately not chosen here

The ruling reserves each of these to P1 and does not select them. None can be
derived from the repository, and AWS discovery was unavailable, so each is an
input the Sponsor or the operator supplies:

```
<INPUT_REQUIRED> AWS_ACCOUNT / PROFILE            approved production account
<INPUT_REQUIRED> REGION                            the approved temporary
                                                   operating location (D.21)
<INPUT_REQUIRED> DB_INSTANCE_IDENTIFIER            naming convention
<INPUT_REQUIRED> INSTANCE_CLASS
<INPUT_REQUIRED> ALLOCATED_STORAGE / MAX / TYPE
<INPUT_REQUIRED> MULTI_AZ                          yes / no
<INPUT_REQUIRED> BACKUP_RETENTION_DAYS
<INPUT_REQUIRED> BACKUP_WINDOW / MAINTENANCE_WINDOW
<INPUT_REQUIRED> READ_REPLICAS                     none / count
<INPUT_REQUIRED> VPC_ID / DB_SUBNET_GROUP / SUBNET_IDS
<INPUT_REQUIRED> SECURITY_GROUP_IDS
<INPUT_REQUIRED> KMS_KEY_ID                        storage encryption
<INPUT_REQUIRED> DB_PARAMETER_GROUP                must carry rds.force_ssl=1
<INPUT_REQUIRED> MONITORING                        Performance Insights,
                                                   Enhanced Monitoring, alarms
<INPUT_REQUIRED> MASTER_USERNAME
```

Recording them as inputs rather than guessing is the point. A sizing value
invented here would be indistinguishable, once applied, from one somebody chose.

---

## PHASE A — preflight (read-only, no gate)

```bash
# A.1 · the evidence base is what was reviewed
git rev-parse HEAD          # must equal the SHA this plan was authorized against
git status --short          # must be clean

# A.2 · the post-ruling invariants, on the exact commit being deployed
python -m pytest tests petcare_runtime/tests petcare_api/tests -q
python -m pytest tests/governance/test_production_tenant_not_created.py -q
python scripts/governance/prohibited_literal_scan.py
python scripts/governance/secret_scan.py
python scripts/governance/verify_evidence_bundles.py

# A.3 · the identity migration must be EMPTY BY DESIGN, not merely quarantined
python scripts/governance/identity_migration_dryrun.py
# REQUIRED: IDENTITY_SOURCE_COUNT=0  MIGRATABLE=0  QUARANTINED=0

# A.4 · the account, named by the Sponsor — never inferred
aws sts get-caller-identity --profile <INPUT_REQUIRED:PROFILE>

# A.5 · rollback destination. There is none yet; B.4 creates the first.
```

**Exit:** every command passes and every `<INPUT_REQUIRED>` above is supplied.

---

## PHASE B — provision the database

> ### ⛔ GATE_LIVE_APPLY — the FIRST LIVE MUTATION of the whole programme is B.1

```bash
# B.1 · provision
aws rds create-db-instance \
  --db-instance-identifier <INPUT_REQUIRED:DB_INSTANCE_IDENTIFIER> \
  --engine postgres --engine-version 16 \
  --db-instance-class <INPUT_REQUIRED:INSTANCE_CLASS> \
  --allocated-storage <INPUT_REQUIRED:GB> \
  --master-username <INPUT_REQUIRED:MASTER_USERNAME> \
  --manage-master-user-password \
  --db-subnet-group-name <INPUT_REQUIRED:DB_SUBNET_GROUP> \
  --vpc-security-group-ids <INPUT_REQUIRED:SECURITY_GROUP_IDS> \
  --no-publicly-accessible \
  --storage-encrypted --kms-key-id <INPUT_REQUIRED:KMS_KEY_ID> \
  --backup-retention-period <INPUT_REQUIRED:DAYS> \
  --db-parameter-group-name <INPUT_REQUIRED:DB_PARAMETER_GROUP> \
  --multi-az <INPUT_REQUIRED> \
  --region <INPUT_REQUIRED:REGION> --profile <INPUT_REQUIRED:PROFILE>

# B.2 · assert the posture rather than assume it
aws rds describe-db-instances --db-instance-identifier <ID> \
  --query 'DBInstances[0].{public:PubliclyAccessible,encrypted:StorageEncrypted,
           backup:BackupRetentionPeriod,engine:EngineVersion,multiAz:MultiAZ}'
# REQUIRED: public=false · encrypted=true · backup>0 · engine 16.x

# B.3 · force TLS
aws rds modify-db-parameter-group --db-parameter-group-name <PG> \
  --parameters "ParameterName=rds.force_ssl,ParameterValue=1,ApplyMethod=pending-reboot"

# B.4 · the first snapshot, BEFORE any schema. This is Phase D's rollback point.
aws rds create-db-snapshot --db-instance-identifier <ID> \
  --db-snapshot-identifier <ID>-pre-schema
```

**⚠️ TLS and the client trust store.** `rds.force_ssl` is not sufficient on its
own: a runtime whose trust store lacks the RDS root CA fails to connect, and the
failure presents as a wrong credential. The CA bundle must be on the runtime
image and named in the connection string (`sslrootcert=`) with
`sslmode=verify-full`. Verify with a throwaway connection **before** Phase D.

**Rollback:** delete the instance. Nothing else exists yet.

---

## PHASE C — secrets

> ### ⛔ GATE_CREDENTIAL_ENTRY — a human act. No agent lane performs it.

Required production secrets, enumerated:

| Secret | Authority | Notes |
|---|---|---|
| database credential | AWS Secrets Manager | `--manage-master-user-password` in B.1 already creates one — capture its ARN rather than making a second copy |
| session signing key | AWS Secrets Manager | created by a human, never printed |

Non-secret configuration, which is **not** a secret and must not be stored as
one (`MVC-W0F-SECRET-SOURCE-DECISION-001`): region, endpoint host, secret
**identifiers**, `PETCARE_SECRET_MODE`, `PETCARE_PERSISTENCE_MODE`.

```bash
# C.1 · capture the managed DB secret ARN
aws rds describe-db-instances --db-instance-identifier <ID> \
  --query 'DBInstances[0].MasterUserSecret.SecretArn'

# C.2 · the session signing key — entered by a human at the terminal.
#       It must satisfy the provider: non-empty, not a placeholder, and not the
#       retired key (refused by fingerprint in RETIRED_KEY_FINGERPRINTS).
aws secretsmanager create-secret --name <INPUT_REQUIRED:SESSION_SECRET_NAME> \
  --kms-key-id <INPUT_REQUIRED:KMS_KEY_ID> \
  --secret-string "<ENTERED_BY_A_HUMAN>"

# C.3 · rotation. Managed rotation is why Secrets Manager was chosen over
#       Parameter Store; leaving it unconfigured discards that reason.
aws secretsmanager rotate-secret --secret-id <SESSION_SECRET_NAME> \
  --rotation-rules AutomaticallyAfterDays=<INPUT_REQUIRED:DAYS>

# C.4 · bind IDENTIFIERS into the runtime — never values
PETCARE_SECRET_MODE=aws_secrets_manager
PETCARE_PERSISTENCE_MODE=postgres
PETCARE_AWS_REGION=<REGION>
PETCARE_SESSION_SECRET_ID=<SESSION_SECRET_NAME>
PETCARE_DB_SECRET_ID=<SECRET_ARN from C.1>
```

**Do not set `SECRET_KEY` or `PETCARE_DB_URL` in production.** Under
`aws_secrets_manager` the identifiers are required and the environment cannot
supply the values — `SEC-SECRET-05`, enforced rather than conventional.

---

## PHASE D — apply the schema

> ### ⛔ GATE_LIVE_APPLY

```bash
# D.1 · preflight. Reports what WOULD apply and applies nothing.
python scripts/governance/apply_migrations.py --dry-run
# EXPECT: MIGRATION_TOTAL=39  MIGRATION_PENDING=39  MIGRATION_APPLIED_NOW=0

# D.2 · apply. Each migration runs once, in its own transaction, recorded with
#       its SHA-256 in schema_migration.
python scripts/governance/apply_migrations.py
# EXPECT: MIGRATION_APPLIED_NOW=39

# D.3 · idempotency, proven on the live target rather than assumed
python scripts/governance/apply_migrations.py
# EXPECT: MIGRATION_APPLIED_NOW=0  MIGRATION_ALREADY_APPLIED=39

# D.4 · verify the schema the application depends on
psql "$TARGET" -c "\dt tenant"
psql "$TARGET" -c "\dt user_identity"
psql "$TARGET" -c "\dt app_session"
psql "$TARGET" -c "\dt audit_event"
psql "$TARGET" -c "\dt audit_chain_head"
psql "$TARGET" -tc "SELECT count(*) FROM tenant;"          # REQUIRED: 0
psql "$TARGET" -tc "SELECT count(*) FROM user_identity;"   # REQUIRED: 0
psql "$TARGET" -tc "SELECT head_hash, next_seq FROM audit_chain_head;"
                                                            # REQUIRED: GENESIS, 1
psql "$TARGET" -tc "SELECT pg_get_constraintdef(oid) FROM pg_constraint
                    WHERE conname='user_identity_role_check';"
# REQUIRED: exactly platform_admin, partner_clinic_admin, veterinarian, owner

# D.5 · rollback checkpoint
aws rds create-db-snapshot --db-instance-identifier <ID> \
  --db-snapshot-identifier <ID>-post-schema
```

**Never run the raw chain with `psql -f` in a loop.** `0001` and `0002` create
nine tables with unguarded `CREATE TABLE`; a re-run fails with `DuplicateTable`
partway through. The ledger runner exists because of this.

**Rollback:** restore `<ID>-pre-schema`.

---

## PHASE E — the first production tenant

> ### ⛔ GATE_LIVE_APPLY
>
> `RATIFICATION-003` establishes the **identity** and explicitly does **not**
> authorize creating the row. This step needs its own authorization.

```
tenant_id    = pharmacare_riyadh
display_name = Pharma Care Pharmacies — Riyadh
status       = ACTIVE (the schema default)
```

Created through the governed mechanism — `PostgresTenantRepository.create` or an
equivalent authorized act — and **never by a migration `INSERT`**. A migration
creates the row the moment the chain is applied, with no actor, no authorization
and no audit event; `tests/governance/test_production_tenant_not_created.py`
fails the build if one appears.

```bash
# E.1 · create, through the repository boundary
# E.2 · verify
psql "$TARGET" -tc "SELECT tenant_id, display_name, status, disabled_at
                    FROM tenant;"
# REQUIRED: exactly one row, ACTIVE, disabled_at NULL
psql "$TARGET" -tc "SELECT count(*) FROM tenant;"   # REQUIRED: 1
# E.3 · snapshot
aws rds create-db-snapshot --db-instance-identifier <ID> \
  --db-snapshot-identifier <ID>-post-tenant
```

**Rollback:** the tenant is referenced by nothing yet, so it can be removed —
but a removal is recorded, not silent. Restoring `<ID>-post-schema` is the
rehearsed path.

---

## PHASE F — production identities

> ### ⛔ GATE_LIVE_APPLY · **NOT authorized by any current ruling**

```
SEED_IDENTITIES=NONE                 PRE-1 1-B: discarded, never migrated
IDENTITY_MIGRATION=EMPTY BY DESIGN   SOURCE=0
```

Production identity is created **only** through the governed invite-gated
registration path, then assigned membership through the governed path:

```
POST /api/auth/register                                   (invite-gated)
POST /api/admin/identities/{user_id}/tenant               (platform_admin only)
     {"tenant_id": "pharmacare_riyadh", "reason": "<why>"}
```

The second produces the two-event audit record. Direct repository mutation is not
an authorized operating path.

**The first `platform_admin` is a bootstrap problem this plan does not solve.**
Membership assignment requires an existing `platform_admin`, and creating or
elevating one is *"a separate privilege-management authority"* that
`RATIFICATION-002` explicitly does not authorize. It must be ruled before Phase F
can complete.

```
OPEN: FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY
```

---

## PHASE G — serving binding

> ### ⛔ GATE_EXTERNAL_DASHBOARD_CONFIG if configured through a provider console

```bash
# G.1 · bind the identifiers from C.4. A process that cannot reach its store
#       does not start — there is no fallback to memory.
# G.2 · health
curl -fsS https://<SERVICE>/api/governance/status | jq .
# REQUIRED: audit_chain_persisted=true
#           audit_chain_durability contains DURABLE
# G.3 · sign-in, protected route, tenant isolation, revocation
# G.4 · emergency key rotation: REHEARSED, not executed. Record who may trigger
#       it and how long it propagates. AC7-07 proves rotation revokes.
```

---

## PHASE H — cutover and rollback

```
H.1  production smoke: sign-in, protected route, revoke, re-present, confirm denial
H.2  rollback decision point
       revert G configuration        -> previous serving mode
       restore <ID>-post-tenant      -> schema + tenant, no identities
       restore <ID>-post-schema      -> schema only
       restore <ID>-pre-schema       -> empty database
H.3  capture evidence: every command's output, the schema_migration ledger, the
     snapshot identifiers, and the audit chain verification result
```

### Where reversibility ends

| Step | Reversible |
|---|---|
| B provision | yes — delete the instance |
| C secrets | yes — a secret can be deleted; a **disclosed** value cannot be undisclosed |
| D schema | yes — restore `pre-schema` |
| E tenant row | yes — restore `post-schema` |
| F identities | yes while seeding-free; **a created credential is disclosed** |
| G binding | yes — revert configuration |
| H traffic cutover | the point past which rollback is a restore, not a revert |
| decommission seeding | `GATE_IRREVERSIBLE_ACTION`, deliberately last |

---

## Gates

| Phase | Gate | First live mutation? |
|---|---|---|
| A | none — read-only | |
| **B** | `GATE_LIVE_APPLY` | **YES — B.1 is the first live mutation** |
| **C** | `GATE_CREDENTIAL_ENTRY` | credential-entry gate |
| D | `GATE_LIVE_APPLY` | |
| E | `GATE_LIVE_APPLY` | separately, per `RATIFICATION-003` |
| F | `GATE_LIVE_APPLY` + an unruled bootstrap authority | |
| G | `GATE_EXTERNAL_DASHBOARD_CONFIG` if via a console | |
| H | cutover; decommissioning is `GATE_IRREVERSIBLE_ACTION` | |

```
P1_AUTHORIZED=NO
```

Nothing in this document has been executed.
