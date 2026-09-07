# MVC-W0H — seller/taxpayer foundational invariant

**Authority:** CP-2 `MVC-CP2-PACK-001 V1.0` · Annex K §K.2 (`MVC-SPEC-001 V3.1`)
**Base:** `6a0c315549d33582ff41a06dcc18b60c0a0a7946`
**Scope:** NON_PRODUCTION_ONLY · `LIVE_GATE=NO for design; YES for any apply`

## What was delivered, and what was not

CP-2 records `CURRENT_STATE  ABSENT — zero seller|taxpayer|invoice in A's 32
migrations or in B`. That was re-measured and confirmed: one incidental match, in
a governance inventory test.

| CP-2 / Annex K target | Status |
|---|---|
| **security invariant** — payment layer holds no write authority over seller identity, enforced by a **static write-authority check** | **DELIVERED** |
| gross never stored net (`REQ-FIN-G1..G3`) | **DELIVERED** (structural + schema guard) |
| additive column + relation | **AUTHORED**, not applied |
| T-SELL-02, T-SELL-03 armed | **DELIVERED** |
| seller identity *populated* at creation from the clinic registration record | **BLOCKED** — needs W0-F |

The invariant is delivered ahead of the field it protects. That ordering is
deliberate and is the point: the guard is armed **before** the schema exists, so
the first component that acquires write authority fails the build rather than
acquiring it quietly. Adding the field first and the guard afterwards would leave
a window in which the defect is possible and undetected.

## Why the check is static

Annex K is explicit:

> **ACCEPTANCE.** A build in which any payment-layer component can write the
> seller-identity field FAILS. The test is a **static write-authority check**,
> not a runtime assertion.

A runtime assert only fires on paths that execute. A component retains write
*authority* whether or not any test happens to exercise it, so the property is
checked over the source. `REQ-FIN-S2` says the same thing directly — "enforced
structurally, not by convention or code review".

Four components are scanned, matching the four Annex K names — payment,
settlement, marketplace, fee collection:

```
petcare_runtime/src/petcare/payment_activation
petcare_runtime/src/petcare/financial_execution
petcare_runtime/src/petcare/financial_operations
petcare_runtime/src/petcare/partner_network
```

Three write routes are closed, not one:

1. **direct assignment** — `order.seller_id = …`, `row["taxpayer_id"] = …`
2. **writer call** — `repo.update_record(seller_taxpayer_id=…)`, which a check
   that only looked at assignment statements would miss entirely
3. **SQL** — `UPDATE … SET seller_id …`, regardless of the Python around it

## Gross-not-net

`REQ-FIN-G3` — net settlement is DERIVED, never stored as an authoritative fact.
Two guards, because there are two ways to break it:

- **structural** — no path subtracts from a stored gross value, in Python
  (`gross_value -= fee`) or SQL (`SET gross_value = gross_value - …`);
- **schema** — no migration introduces a stored net column, under any of its
  names (`net_value`, `net_settlement_amount`, `amount_net`, …).

The schema guard matters because a `net_value` column is a second source of truth
that can silently disagree with the movements it was derived from — and both
would look like facts.

## Migration — authored, not applied

`petcare_runtime/migrations/0029_w0h_seller_identity.sql`

Additive: three NULLable seller columns and `gross_value` on `partner_orders`,
plus a `commercial_deduction_movement` table. Nothing altered or dropped.

**Deductions are rows, not subtractions.** `REQ-FIN-G2` requires every deduction
to be a separate movement referencing the gross sale, which is why this is a
table and not a `net_value` column.

**EP-07 seal respected.** `partner_orders` is in the sealed marketplace domain.
This adds columns only — no catalogue, contract, pricing or settlement logic is
reimplemented and no sealed module is touched. Adding an attribute to a record is
not re-owning the domain that manages it.

**Pre-existing rows are marked `UNRESOLVED`, never guessed.** Seller identity
cannot be inferred from payment routing — `REQ-FIN-S3` states that the identity
of whoever receives funds first must never determine seller identity. Inferring a
seller from the routed partner would be exactly the reasoning that requirement
forbids, and once written it would be indistinguishable from a fact.

`NOT NULL` is written in as a commented future step with its precondition, not
enforced: it would fail closed against every row just marked `UNRESOLVED`.

Proven to apply by running all 29 migrations against a throwaway SQLite database
in scratch space; `net_value` confirmed absent. No live database was touched.

## Immutability is structural, not a CHECK constraint

`REQ-FIN-S1` requires seller identity to be immutable after creation. That is
enforced by denying write authority to every component that could change it,
which is stronger than a constraint: a CHECK can be dropped by a later migration,
whereas the static check fails the build the moment a component acquires the
ability to write the field at all.

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO   MIGRATION_APPLIED=NO
EP07_SEALED_MODULES_MODIFIED=NO
```
