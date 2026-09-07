# MVC-W0F-DATA-STORE-DECISION-001 — production serving data-store

**Date:** 2026-09-07 · **Authority:** CP-2 (Ratified) + Sponsor D.21 ruling
**Governs:** W0-F remaining scope item 1 · **Status:** decided, not provisioned

```
PRODUCTION_STORE=AWS_MANAGED_POSTGRESQL_COMPATIBLE_RELATIONAL_SYSTEM_OF_RECORD
PROVISIONED=NO  (GATE_LIVE_APPLY)
```

## The decision

A single AWS-managed PostgreSQL-compatible relational database is the
system-of-record for identity, tenancy, sessions and audit. No second persistence
paradigm is introduced.

## Why, from repository evidence rather than preference

**1 · The estate is already relational, with real migrations.**
`petcare_runtime/migrations/` holds 30 hand-written SQL migrations using
`CREATE TABLE`, `ALTER TABLE`, foreign keys and `CHECK` constraints. The W0-F pack
is explicit that these are canonical and that the port source's SQLAlchemy
`create_all` must not be carried across. Choosing anything other than a relational
store would strand thirty migrations and the schema they define.

**2 · The data model is relational in fact, not just in storage.**
`clinical_record_attestation` references `professional_authority_grant(grant_id)`;
`commercial_deduction_movement` references `partner_orders(order_id)`. These are
foreign keys enforcing invariants that W0-H and W0-I depend on. A document or
key-value store would move those invariants into application code — exactly where
W0-H's `REQ-FIN-S2` says they must *not* live ("enforced structurally, not by
convention or code review").

**3 · The controls already written need transactions.**
W0-I's authority model is time-bounded: a grant and its revocation must not be
observable in an inconsistent intermediate state, or `held_at()` answers wrongly
for the instant in between. W0-G's chain requires that an event and its
`prev_hash` link commit together, or a crash produces a chain gap indistinguishable
from tampering.

**4 · `CHECK` constraints are already load-bearing.**
Migration 0030 makes a silent sole-practitioner bootstrap unrepresentable via a
table-level `CHECK`. That control lives in the schema, not the application. A
store without declarative constraints would silently drop it.

**5 · It is the least-cost target for the mandated KSA migration.**
D.21 makes migration to KSA a scheduled certainty. A logical dump/restore between
two PostgreSQL-compatible endpoints is a solved, rehearsable operation. A bespoke
store would make the mandatory migration bespoke too.

**6 · Session revocation needs a transactional lookup.**
AC-7 requires individual and per-user revocation. That is an indexed read and a
single-row update — the operation relational stores are built for.

## What is deliberately NOT decided here

```
REGION / ENDPOINT     not decided. D.21 permits a temporary out-of-Kingdom
                      operating location; the region is deployment configuration
                      supplied per environment, never a code constant.
ENGINE VARIANT        RDS PostgreSQL vs Aurora PostgreSQL-compatible is an
                      operational sizing choice, deferred. Both satisfy every
                      requirement above; neither changes application code.
INSTANCE TOPOLOGY     sizing, replicas, backup windows — operational, gated.
```

Naming the *class* of store is the architectural decision. Naming the *instance*
is provisioning, and provisioning is `GATE_LIVE_APPLY`.

## Portability rule — binding on implementation

D.21 requires that

```
TEMPORARY_FOREIGN_REGION  ->  APPROVED_KSA_REGION/SITE
```

be reachable by controlled migration, never by application redesign. That imposes
four constraints, each guarded by
`tests/governance/test_w0f_architecture_contracts.py`:

1. **No region, endpoint or account identifier in domain models, tenancy logic,
   session logic, or migration files.** Hosting location enters only through
   environment configuration.
2. **No residency semantics in application code.** No branch reads "are we in KSA
   yet" — the application behaves identically in either location, and the only
   difference is where the endpoint points.
3. **Migrations stay portable SQL.** No provider-proprietary extension in a
   migration unless recorded here with its migration path.
4. **KSA target identifiers stay placeholders** until the site is approved:
   `TARGET_KSA_HOSTING_AUTHORITY`, `TARGET_KSA_REGION_OR_SITE`,
   `TARGET_KSA_DATABASE_ENDPOINT`. No value is invented for them.

## Connection contract

The application depends on a configuration contract, not a provider SDK:

```
PETCARE_DB_URL        full connection URL, supplied by environment
PETCARE_DB_SECRET_ID  identifier of the governed secret holding credentials
                      (see MVC-W0F-SECRET-SOURCE-DECISION-001)
```

Neither carries a default. A missing value fails closed at startup, matching the
W0-A precedent that a governed secret has no safe default — and for the same
reason: a default connection string is a silent connection to the wrong place.
