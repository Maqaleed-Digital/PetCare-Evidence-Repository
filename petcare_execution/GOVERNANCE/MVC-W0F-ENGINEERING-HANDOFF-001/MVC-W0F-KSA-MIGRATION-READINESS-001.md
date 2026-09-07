# MVC-W0F-KSA-MIGRATION-READINESS-001 — KSA migration readiness

**Date:** 2026-09-07 · **Authority:** Sponsor D.21 ruling
**Status:** specification · nothing executed · target site not yet approved

```
D21_CURRENT_STATE=TEMPORARY_OUT_OF_KINGDOM_ALLOWED
D21_TARGET_STATE=KSA_MIGRATION_MANDATORY_WHEN_APPROVED_KSA_SITE_READY
KSA_MIGRATION_EXECUTED=NO
```

## Why this exists now rather than later

D.21 makes the KSA move a **scheduled certainty**. A migration known to be
mandatory but planned only when it becomes urgent is planned under the worst
conditions. Writing the specification while the temporary deployment is still
being designed is what keeps the two compatible — every constraint below is a
constraint on *today's* build, not a future task.

## Unapproved target — placeholders only

The KSA hosting site is not approved. No value is invented for any of these, and
`tests/governance/test_w0f_architecture_contracts.py` fails the build if one
acquires a value:

```
TARGET_KSA_HOSTING_AUTHORITY   <unapproved>
TARGET_KSA_REGION_OR_SITE      <unapproved>
TARGET_KSA_DATABASE_ENDPOINT   <unapproved>
```

A placeholder that quietly gains a value before approval is an unapproved
destination becoming load-bearing, and by the time anyone inspected it would look
indistinguishable from an approved one.

## Transition steps

### 1 · Logical database portability
Move by **logical** dump and restore, never by storage-level replication.
Storage-level copies bind the target to the source engine version and carry the
physical layout with them; a logical dump is portable and independently
verifiable. Portability is already enforced: migrations are plain SQL, and no
provider-proprietary extension is permitted without being recorded in
`MVC-W0F-DATA-STORE-DECISION-001`.

### 2 · Schema migration portability
The target is built by **replaying the migration chain**, not by cloning. The
chain is the canonical definition; a clone would carry any drift the source has
accumulated. Reconciliation compares the replayed schema against the source
schema and fails on any difference.

### 3 · Object and media data
Currently none. If object storage is introduced before cutover, it inherits this
specification and needs its own inventory and checksum reconciliation. Recorded
so the omission is deliberate rather than forgotten.

### 4 · Secret re-binding
Secrets are **re-created in the target**, never copied.
`MVC-W0F-SECRET-SOURCE-DECISION-001` gives the reason: copying material produces
two live credentials with no single revocation point. Sequence: create in target
→ bind application → verify → revoke in source. The source secret is revoked
**only after** the target is verified, so a failed cutover still has a working
rollback.

### 5 · DNS and service cutover
DNS TTL is lowered ahead of the window so rollback is minutes, not propagation
time. Cutover is a routing change, not a code change — which is exactly what the
portability rules in the data-store decision exist to guarantee.

### 6 · Session treatment — a decision, not a default
Two admissible options; one must be chosen and recorded before cutover:

- **Invalidate all sessions.** Every user re-authenticates. Simple, fail-closed,
  and free of cross-jurisdiction session-state transfer.
- **Controlled continuity.** Session state migrates with the database, sessions
  stay valid. Requires AC-7's server-side store to be live and the previous-key
  question to be settled.

Recommended: **invalidate**, unless continuity is a stated business requirement.
Re-authentication is a known cost; migrating live session state across a
jurisdiction boundary during a cutover is a novel one.

### 7 · Encryption and key transition
Target keys are generated in the target. Encryption at rest and in transit is
re-established there rather than transported. Any KMS key identifier is
configuration, never a code constant.

### 8 · Audit continuity — the hard one
W0-G's hash chain must survive the move. The chain links each event to its
predecessor's digest, so a logical restore preserves it **only if row order and
content are preserved exactly**.

The reconciliation step is therefore not optional: `verify_audit_chain()` must
return `ok` against the target **before** cutover completes. If it does not, the
migration has broken the tamper-evidence property and must roll back rather than
re-chain — silently rehashing in the target would destroy the evidence that the
move damaged the log, which is exactly the failure W0-G's T-CHAIN-04 forbids.

### 9 · Backup and restore validation
A restore is **tested in the target before cutover**, not merely configured. The
W0-F pack's AC-9 wording governs here: a rehearsed rollback against a restore,
not just a backup.

### 10 · Rollback
Rollback is DNS reversion plus source-secret retention, and it is available until
the source is decommissioned. Decommissioning the source is a separate,
explicitly gated act — never part of the cutover window.

### 11 · Reconciliation
Before cutover completes, all must hold:

```
row counts match per table
schema replay matches source schema
verify_audit_chain() ok in target
tenant isolation controls pass against target
professional-authority time-bounded queries return identical results
no UNRESOLVED identity or seller record silently resolved by the move
```

### 12 · Downtime and RTO
Not assumed. RTO is derived from measured dump/restore duration at the data
volume prevailing at cutover, and is recorded in the cutover evidence pack. A
figure invented now would be wrong and would be quoted later as though measured.

## Evidence required before KSA cutover

```
approved TARGET_KSA_HOSTING_AUTHORITY and region/site
measured dump/restore timings at production volume
restore test executed in target, evidenced
reconciliation results, all green
audit chain verification in target
session treatment decision, recorded
rollback rehearsal, evidenced
Sponsor authorization for GATE_LIVE_APPLY and GATE_IRREVERSIBLE_ACTION
```

## Gates

```
GATE_LIVE_APPLY            target provisioning, dump/restore, cutover
GATE_CREDENTIAL_ENTRY      target secret creation and binding
GATE_EXTERNAL_DASHBOARD    DNS, provider console
GATE_IRREVERSIBLE_ACTION   source decommissioning
```

None is approached by this specification.
