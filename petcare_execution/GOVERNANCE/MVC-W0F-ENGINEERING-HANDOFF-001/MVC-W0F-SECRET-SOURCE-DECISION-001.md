# MVC-W0F-SECRET-SOURCE-DECISION-001 — governed secret source

**Date:** 2026-09-07 · **Authority:** CP-2 (Ratified) · Sponsor direction
**Governs:** W0-F remaining scope item 3 · **Status:** decided, nothing created

```
SECRET_AUTHORITY=AWS_SECRETS_MANAGER
CONFIG_AUTHORITY=AWS_SSM_PARAMETER_STORE
SECRETS_CREATED=NO  (GATE_CREDENTIAL_ENTRY)
SECRETS_ROTATED=NO  (GATE_CREDENTIAL_ENTRY)
```

The W0-F pack deferred this to "the MyVetiCare AWS architecture decision" and
named exactly two candidates. This resolves it.

## The split, and the line between them

| Authority | Holds | Examples |
|---|---|---|
| **Secrets Manager** | material that *confers* authority | session signing key, database credentials, runtime application secrets, anything rotation-capable |
| **SSM Parameter Store** | material that *identifies* but confers nothing | region, endpoint hostname, feature flags, secret **identifiers**, log level |

The line is not sensitivity — it is **authority**. A value that lets its holder
act as someone is a secret. A value that merely says where to look is
configuration. `PETCARE_DB_SECRET_ID` is configuration: knowing the name of a
secret grants nothing without permission to read it.

## Why Secrets Manager for the signing key

The session signing key is the one value in this estate whose compromise forges
identity rather than merely revealing data. W0-A already establishes that it has
no safe default and that the process must refuse to start without it.

Two properties decide it:

1. **Managed rotation.** Parameter Store has no rotation primitive; rotation
   would be a bespoke operational procedure. Given that key rotation is currently
   the *only* revocation lever in the estate (see AC-7), a store that makes
   rotation a first-class managed operation is worth more here than elsewhere.
2. **Versioning with staged labels.** Rotation without a previous-version concept
   is an outage. Secrets Manager versions are what make a controlled key
   transition possible at all — and AC-7's decision about a previous-key
   acceptance list depends on that mechanism existing.

## One authority per secret — no dual sourcing

A secret is read from Secrets Manager or it is absent. It is never *also*
readable from Parameter Store, an environment default, or a file.

The reason is specific rather than tidy-minded: two sources for one secret means
two rotation paths, and a rotation that updates one and not the other leaves a
stale credential that still works. That is indistinguishable from an unrevoked
key, which is the failure AC-7 exists to prevent.

```
GUARD  no configuration path may supply secret material
GUARD  no SSM parameter may substitute for required secret material
```

## Application contract

Application code depends on a **provider abstraction**, never on a provider SDK
call at the point of use, and never on a literal:

```
secret_provider.get(secret_id: str) -> str        # raises if absent
```

Three properties are binding, and each is guarded:

1. **No default.** `get()` has no fallback value and no fallback source. A
   missing secret raises; it never returns a placeholder. This extends the W0-A
   precedent from the signing key to every governed secret.
2. **No region in the call.** The provider is configured with its region from
   environment; callers never name one. D.21 requires that moving to KSA is a
   configuration change, and a region literal at a call site defeats that.
3. **Fail closed at startup.** A process that cannot obtain a required secret
   does not start degraded. It refuses, as `_require_secret_key()` already does.

## What this decision does NOT do

```
No secret is created, read, written, or rotated by this run.
No AWS account, role, policy or KMS key is named or provisioned.
Secret CREATION and ENTRY remain GATE_CREDENTIAL_ENTRY.
```

Naming the authority is a decision. Putting a value into it is the gate.

## KSA migration consequence

Secrets do not migrate — they are **re-created** in the target account and region
and re-bound by identifier. `MVC-W0F-KSA-MIGRATION-READINESS-001` records secret
re-binding as a distinct cutover step, because copying secret *material* between
regions is the failure mode this ordering exists to avoid: it produces two live
copies of a credential with no single revocation point.
