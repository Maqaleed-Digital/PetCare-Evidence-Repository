# MVC-W0J — password KDF and migration-invariant CI

**Authority:** CP-2 `MVC-CP2-PACK-001 V1.0` · `MVC-EXEC-001 V1.0 §8` · V3.2 §33/§34/§36
**Base:** `28c4f45d2f7151cba174db1ebd8a2ea41b538c9f`
**Scope:** NON_PRODUCTION_ONLY · `LIVE_GATE=NO`

| CP-2 W0-J target | Status |
|---|---|
| governed password KDF (salted, work-factored) | **DELIVERED** |
| CI gate enforcing the six migration invariants | **DELIVERED** — all six armed |
| `T-PW-01` unsalted/unstretched hash rejected by CI | **DELIVERED** |
| `T-MIG-01` a violating migration FAILS the gate | **DELIVERED** |
| purpose limitation ported | **ALREADY PRESENT** — see below |
| user store persisted | **BLOCKED** — W0-F |

## The KDF, and why now was the safe moment

`_hash_password` was `hashlib.sha256(password.encode()).hexdigest()` — unsalted
and unstretched.

Unsalted means identical passwords produce identical digests, so one rainbow
table breaks every account at once, and equal hashes reveal which users share a
password. Unstretched means a commodity GPU tries billions of candidates a
second: a fast hash is simply the wrong primitive here, and SHA-256 is fast by
design.

Replaced with **scrypt** (stdlib, so no new dependency to audit), salted per
credential, with the work factors stored in the hash string:

```
scrypt$16384$8$1$<salt>$<dk>
```

scrypt rather than PBKDF2 because it is **memory-hard**: specialised hardware
buys an attacker much less over general-purpose hardware. Storing the parameters
is what makes the work factor upgradable — raising `n` later leaves every
existing credential verifiable.

**Why this was safe to do now, despite CP-2 listing W0-F as a dependency.** The
W0-F pack warns that this must be *"a credential migration with a rehash-on-next-login
path, not a silent copy"*. That warning is about **persisted** credentials. There
are none: the user store is still in-memory and re-seeded at startup, so there is
no stored credential to migrate and no window in which two formats disagree. This
is the cheapest moment this change will ever have. Doing it after persistence
lands would mean migrating real credentials.

The rehash-on-next-login path is implemented anyway, because it is what makes the
change safe *when* persistence arrives:

- legacy SHA-256 and bcrypt hashes still **verify**, so no account locks out;
- any credential not in the current format is flagged `needs_rehash`;
- the caller re-hashes on successful sign-in — the one moment the plaintext is
  legitimately in hand. No batch job, no window, and the plaintext is never
  stored or handled anywhere else.

A stale *work factor* is treated the same way, so raising `n` in future upgrades
credentials rather than invalidating them.

Comparison is `hmac.compare_digest`. A timing-variable comparison leaks the
digest a byte at a time, which is enough to forge a match without knowing the
password.

## The six migration invariants — and one interpretation, declared

`MVC-EXEC-001 §8`:

```
I-1  audit partition present in the FIRST migration
I-2  seller identity non-nullable on every commercial record
I-3  no migration destructively deletes anchored evidence
I-4  every migration reversible, or explicitly recorded irreversible with a Sponsor reference
I-5  role catalogue changes only by migration carrying a Sponsor-decision reference
I-6  audit chain columns backfilled with an explicit, recorded decision for pre-existing rows
```

**I-2 is enforced as staged, and this is an interpretation — recorded as one.**

Read literally, I-2 demands `NOT NULL` today. That would fail the W0-H migration
this programme just merged, which CP-2's own `MIGRATION_DESIGN` instructs be
written additively: *additive first -> deterministic classification where
provable -> rows that cannot be classified recorded as UNRESOLVED, never guessed
-> validate -> only then enforce NOT NULL if safe.*

Worse, a literal gate would push authors toward inventing seller values for
historical rows in order to pass — the exact outcome W0-H forbids, since seller
identity cannot be inferred from payment routing (`REQ-FIN-S3`).

The gate therefore requires seller identity to be **present, and either enforced
or carrying a recorded enforcement plan with its precondition**. That keeps
"non-nullable eventually" a checkable claim rather than an aspiration, without
rewarding a guess. If the Sponsor reads I-2 strictly, this gate is the thing to
change, and it is one assertion.

**I-2 is also structural rather than a table-name list.** Seller identity is
carried once on the record bearing the consideration and inherited by rows
referencing it; settlement preparation, review and export are processing stages
over an order, not separate sales. Duplicating the seller onto each would create
several mutable copies of a field `REQ-FIN-S1` requires to be immutable. So the
rule is "carries seller identity, or references a record that does" — an
exclusion list would grow with every new table and would eventually hide a real
gap.

## Purpose limitation — already present, not ported

CP-2 records `purpose_limitation exists in B only`. That is drift: `purpose_of_use`
is already a first-class field on `AccessContext` in
`petcare_runtime/src/petcare/auth/access_control.py`, with six defined purposes,
and it drives access decisions rather than being carried alongside them.

Re-porting it would have duplicated a working control. Recorded here instead.

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO   MIGRATION_APPLIED=NO
CREDENTIALS_MIGRATED=NO (no persisted credentials exist to migrate)
```
