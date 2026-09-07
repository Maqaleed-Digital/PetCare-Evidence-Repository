# W0-J perturbation — all six invariants plus the KDF

CP-2 W0-J `TESTS`: *"CI gate that FAILS on a migration violating any invariant
(**prove it can fail**)"*. Each invariant was violated by a probe migration and
had to be caught by its own assertion.

## The six invariants

| Invariant | Probe | Guard that fired |
|---|---|---|
| **I-1** | a migration sorting before `0001` that creates no audit partition | `test_i1_audit_partition_present_in_the_first_migration` |
| **I-2** | `CREATE TABLE clinic_invoice_run` with no seller and no order reference | `test_i2_every_commercial_record_has_seller_identity` |
| **I-3** | `DELETE FROM audit_event WHERE occurred_at < …` | `test_i3_no_migration_destructively_deletes_anchored_evidence` |
| **I-4** | `DROP TABLE partner_orders` with no Sponsor reference | `test_i4_irreversible_migrations_are_recorded_with_a_sponsor_reference` |
| **I-5** | `CREATE TABLE role_catalogue` with no Sponsor reference | `test_i5_role_catalogue_changes_carry_a_sponsor_decision_reference` |
| **I-6** | `ADD COLUMN prev_hash` with no recorded pre-existing-row decision | `test_i6_audit_chain_columns_carry_an_explicit_decision…` |

Each probe failed **exactly one** assertion. Baseline and restored: 8 passed.

I-5 is the one that matters most in this estate. W0-D retired
`pharmacy_operator`, and the standing prohibition is that it *"may never arrive
as a role-catalogue migration"*. I-5 is what makes that prohibition testable
rather than remembered.

## T-PW-01 — the KDF

| Probe | Result |
|---|---|
| `_hash_password` reverted to `hashlib.sha256(...).hexdigest()` | **5 failed** |

The five: salted-ness, work factors recorded, the AST check that
`_hash_password` calls `scrypt` and not `sha256`, the legacy rehash path, and
the stale-work-factor rehash path.

The AST check exists because a substring check does not work here.
`hashlib.sha256` legitimately appears elsewhere in the module — the W0-A2 key
fingerprint, where a fast hash over a high-entropy secret is correct. The guard
inspects the calls `_hash_password` actually makes, so it flags a real
regression rather than a docstring explaining why SHA-256 is the wrong
primitive. That distinction was found by the guard failing against its own
explanation.

Baseline and restored: `petcare_api` 64 passed.

```
PERTURBATION_GUARDS_PROVEN=7 (six invariants + T-PW-01)
WORKTREE_RESTORED=YES — no probe migration and no perturbation committed
```
