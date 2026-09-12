# P1 · the first-`platform_admin` genesis step — PREPARED, NOT AUTHORIZED

**Authority to prepare:** `MVC-GENESIS-PLATFORM-ADMIN-001` §8 — *"It also
authorizes preparation of the exact production genesis step for inclusion in the
P1/cutover runbook."*

**Authority to execute:** none.

```
PRODUCTION_GENESIS_EXECUTION=NOT_AUTHORIZED_BY_THIS_RULING
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
```

This document is a prepared step. Reading it, reviewing it and merging it are
not the act. Running §4 below is two gated acts at once — `GATE_LIVE_APPLY`
(a durable privileged write to production) and `GATE_CREDENTIAL_ENTRY` (the
administrator's credential) — and both are withheld.

## 1 — Where this sits in the plan

`P1_ACTIVATION_PLAN-001` phases:

| phase | | this step |
|---|---|---|
| B | provision · `aws rds create-db-instance` | must be complete |
| C | secrets · `C.2` is the credential-entry gate | must be complete |
| D | schema · apply the migration chain through `0035` | must be complete |
| **—** | **this step** | **establishes the first `platform_admin`** |
| F | tenant membership administration | was blocked on this step |

The authorization request already prepared covers **B–D only**. This step is
outside it and needs its own authorization, because §8 withholds execution even
though it authorizes the preparation you are reading.

Phase D must have applied `0035_genesis_platform_admin.sql`. That migration
creates the shape and nothing else — `PLATFORM_ADMIN_ROWS_CREATED=0`,
`GENESIS_CONSUMED=NO`. Applying the chain is not the genesis act.

## 2 — Inputs, none of which are known here

Every value below is `<INPUT_REQUIRED>` for the same reason the rest of the P1
plan is: `READ_ONLY_AWS_DISCOVERY=NOT_AVAILABLE`, and §2 withholds inventing the
identity or the credential.

| input | source | may it be invented? |
|---|---|---|
| `PETCARE_DATABASE_URL` | phase C secret store | no |
| `--user-id` | Sponsor, at the production-identity gate | no |
| `--email` | Sponsor, at the production-identity gate | no |
| `--full-name` | Sponsor, at the production-identity gate | no |
| `--ruling` | `MVC-GENESIS-PLATFORM-ADMIN-001` | fixed |
| the credential | typed at the terminal, `GATE_CREDENTIAL_ENTRY` | **no** — §2 |

There is deliberately no `--role`. §2 fixes the resulting role in the governed
procedure, and the script has no flag that could carry another.

## 3 — Preflight, read-only, consumes nothing

Run first. It is safe at any time and answers §5's two preconditions.

```bash
PETCARE_DATABASE_URL='<INPUT_REQUIRED>' \
  python scripts/governance/platform_admin_genesis.py --check
```

Required output before proceeding:

```
GENESIS_CONSUMED=NO
GENESIS_ADMIN_USER_ID=<none>
```

`GENESIS_CONSUMED=YES` means the authority has already been spent. **Stop.**
That is not a retry condition: a second genesis is prohibited, and creating or
replacing a `platform_admin` afterwards requires a separate
privilege-management authority that does not yet exist.

## 4 — The act · `GATE_LIVE_APPLY` + `GATE_CREDENTIAL_ENTRY`

**Do not run this without a current authorization naming this step.**

```bash
PETCARE_DATABASE_URL='<INPUT_REQUIRED>' \
  python scripts/governance/platform_admin_genesis.py \
    --user-id '<INPUT_REQUIRED>' \
    --email '<INPUT_REQUIRED>' \
    --full-name '<INPUT_REQUIRED>' \
    --ruling MVC-GENESIS-PLATFORM-ADMIN-001 \
    --confirm-single-use-genesis
```

The script prompts for the credential twice and does not echo it. It refuses a
non-terminal stdin on purpose: a piped credential comes from a file or a
variable that outlives the process, and this identity holds the highest role in
the system.

Expected output:

```
GENESIS_RESULT=APPLIED
GENESIS_ADMIN_USER_ID=<the id supplied above>
GENESIS_ADMIN_ROLE=platform_admin
GENESIS_AUDIT_EVENT_ID=<uuid>
GENESIS_RULING=MVC-GENESIS-PLATFORM-ADMIN-001
GENESIS_CONSUMED=YES
```

`GENESIS_RESULT=DENIED` or `UNAVAILABLE` means **nothing was written** — the act
is atomic with its audit evidence (§6), so a failure leaves no identity, no
event and no consumption record. Record the message and stop; do not retry
until the reported cause is understood, because a retry after a partially
understood failure is how a second privileged identity gets created.

## 5 — Acceptance, after the act

Each of these verifies an object-state transition rather than the wrapper's exit
status.

| # | check | required |
|---|---|---|
| A-1 | `--check` again | `GENESIS_CONSUMED=YES` and the administrator's id |
| A-2 | `SELECT count(*) FROM user_identity WHERE role='platform_admin'` | `1` |
| A-3 | `SELECT count(*) FROM platform_admin_genesis` | `1` |
| A-4 | `SELECT tenant_id FROM user_identity WHERE user_id='<id>'` | `NULL` — platform scope is the absence of a tenant |
| A-5 | `SELECT provenance FROM user_identity WHERE user_id='<id>'` | `GENESIS` |
| A-6 | the genesis `audit_event` row | `event_name='platform_admin.genesis'`, `actor_id='UNATTRIBUTED'`, `tenant_id='UNATTRIBUTED'`, `resource_id=<id>`, `reason_code='MVC-GENESIS-PLATFORM-ADMIN-001'` |
| A-7 | audit chain verification | `ok=true` — the act that establishes the administrator must not be the act that invalidates the log |
| A-8 | a second `--confirm-single-use-genesis` run with a **different** id | refused, `GENESIS_RESULT=DENIED`, and A-2/A-3 still `1` |

A-8 is the only acceptance probe that is itself an attempted mutation. It is
safe because the refusal is the property being proved and nothing is written on
that path — but it must be run with a *different* identity, or it proves
ordinary idempotence instead of single use.

## 6 — Rollback

There is none, and that is a property of the ruling rather than a gap.

`GENESIS_REUSE=PROHIBITED` means the authority cannot be re-consumed, so
deleting the consumption record would not restore a usable genesis path — it
would destroy the only durable evidence that the administrator was authorized,
while leaving the administrator in place. Deleting the identity as well would be
an irreversible production action (`GATE_IRREVERSIBLE_ACTION`) and would leave a
governed audit event describing an administrator who no longer exists.

If the wrong identity is established, the remedy is a new Sponsor act, not an
undo. Treat §4 as irreversible and confirm the inputs in §2 before running it.

## 7 — What this step does NOT do

* It creates no tenant. `PRODUCTION_TENANT_ROW_CREATED=NO` is unchanged, and
  `pharmacare_riyadh` still requires a separate Sponsor act
  (`RATIFICATION-003` ruled the identity only).
* It assigns nobody to a tenant. That is phase F, through the already-ratified
  governed tenant-assignment path.
* It grants no second administrator, and it opens no route: §7 withholds a
  reusable bootstrap endpoint, and `main.py` does not import the genesis module.
* It creates no session. The administrator signs in through the ordinary
  authentication path afterwards.
