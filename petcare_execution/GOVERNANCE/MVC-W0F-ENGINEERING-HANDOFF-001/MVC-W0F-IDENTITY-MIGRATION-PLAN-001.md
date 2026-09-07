# MVC-W0F-IDENTITY-MIGRATION-PLAN-001 — identity migration (prepare only)

**Date:** 2026-09-07 · **Status:** PREPARED · nothing applied
**Gates:** `GATE_IRREVERSIBLE_ACTION` + `GATE_LIVE_APPLY` remain closed

```
MIGRATION_APPLIED=NO
DRY_RUN_ONLY=YES
```

## 1 · Source-state inventory

The source is not a database. It is process memory:

```
petcare_api/routers/auth.py
  _users: dict[str, dict]          keyed by email, seeded at startup
  _invite_codes: dict[str, dict]   keyed by code, seeded at startup
petcare_api/main.py
  _audit_log: list[dict]           in-memory, dies with the process
```

**This is the single most important fact in the plan: there are no persisted
credentials today.** Everything is re-seeded at each start. The migration is
therefore not a data move at all in the current state — it is a change of where
future identity is written.

That has a consequence worth stating plainly: **taken now, this migration is
close to free; taken after production identity exists, it is a credential
migration with all the attendant risk.** The cost of this step is a function of
when it is taken.

## 2 · Target schema

New tables, additive, authored in a migration not yet applied:

```
user_identity        user_id PK · email UNIQUE · password_hash · role
                     · tenant_id · full_name · created_at · disabled_at NULL
invite_code          code PK · allowed_role · tenant_id · expires_at
                     · consumed_at NULL · consumed_by NULL
```

`tenant_id` is **NOT NULL on new rows** and is the field W0-C establishes as
server-side authority. `password_hash` carries the scrypt format W0-J already
produces.

## 3 · Field mapping

| Source (`_users[email]`) | Target (`user_identity`) | Note |
|---|---|---|
| `id` | `user_id` | preserved verbatim |
| `email` | `email` | unique key |
| `password_hash` | `password_hash` | already scrypt (W0-J); no re-hash, no plaintext |
| `role` | `role` | validated against `VALID_ROLES` |
| `tenant_id` | `tenant_id` | may be `None` — see §8 |
| `full_name` | `full_name` | |

No field is invented. No default is supplied for a missing value.

## 4 · Tenant mapping

Tenant is copied, never inferred. An identity whose `tenant_id` is `None` keeps
`NULL` and is quarantined (§8) — it is **not** assigned a tenant by proximity, by
role, or by any other signal.

This follows W0-H's precedent for seller identity, and for the same reason:
inferring a scope from surrounding data produces a value indistinguishable from a
verified one once written.

## 5 · Role mapping

Roles copy verbatim and are validated against `VALID_ROLES` at migration time.

```
INVARIANT  no migrated identity may hold a role it did not hold in the source
INVARIANT  the retired pharmacy_operator role cannot be introduced by migration
```

Both are guarded by `tests/governance/test_identity_migration_contracts.py`. Role
elevation during a migration is the failure this section exists to prevent: it
would be invisible afterwards, since the target would simply show the elevated
role as though it had always been held.

## 6 · Session-state treatment

Sessions are **not migrated**. They are stateless signed cookies today with no
server-side record to move. On cutover, existing cookies remain
cryptographically valid until TTL expiry unless the signing key is rotated.

The decision to rotate at cutover (invalidating all sessions) belongs with AC-7
and is recorded there, not defaulted here.

## 7 · Password and credential treatment

No credential is re-hashed, decrypted, or read in plaintext at any point. Hashes
move as opaque strings. W0-J's rehash-on-next-login path handles any legacy
format that survives, at the one moment the plaintext is legitimately available.

```
INVARIANT  the migration never has access to a plaintext password
```

## 8 · Invalid and legacy record disposition

Records that cannot be deterministically mapped are **quarantined, never
guessed**:

```
UNRESOLVED_NO_TENANT      tenant_id is NULL
UNRESOLVED_UNKNOWN_ROLE   role not in VALID_ROLES
UNRESOLVED_DUPLICATE      email collision between source records
```

Quarantined rows are written to `identity_migration_quarantine` with their
reason, and are **not** written to `user_identity`. They fail closed: an identity
that did not migrate cannot authenticate, which is the safe direction. Resolution
is manual and recorded.

## 9 · Migration ordering

```
1  apply additive schema (user_identity, invite_code, quarantine)   GATE_LIVE_APPLY
2  dry-run against a copy; produce the reconciliation report
3  Sponsor review of the quarantine set
4  cutover: write path switches to the store                        GATE_LIVE_APPLY
5  verify; retain in-memory seeding disabled but revertible
6  decommission seeding                                             separate gate
```

## 10 · Rollback

Steps 1–3 are reversible by construction: additive schema and a dry-run change
nothing the application reads. Step 4 is reversible by reverting the write-path
switch while the seeded path still exists. Step 6 is the irreversible one, and is
deliberately last and separately gated.

## 11 · Dry-run mechanism

`scripts/governance/identity_migration_dryrun.py` (PR-B) runs the full mapping
against an ephemeral SQLite database built by replaying the migration chain,
reports counts and quarantine reasons, and writes nothing durable. It is the
rehearsal AC-9 requires, executable without any live infrastructure.

## 12 · Reconciliation checks

```
source identity count == migrated + quarantined        (no row lost)
every migrated user_id exists in source                 (no row invented)
every migrated role appears in the source for that user (no elevation)
no migrated row carries NULL tenant_id                  (quarantine caught them)
no email appears twice in user_identity
scrypt prefix present on every migrated password_hash
```

## 13 · Evidence required before apply

```
dry-run report, with quarantine set enumerated
reconciliation checks all green
Sponsor disposition of every quarantined record
rollback rehearsal evidenced against a restore, not a backup (AC-9)
```

## 14 · Cutover gate

```
GATE_LIVE_APPLY           schema apply and write-path switch
GATE_IRREVERSIBLE_ACTION  seeding decommission
```

Neither is approached by this plan. Nothing here is executed.
