# Rule 18 — W0-G / W0-H / W0-J re-measured from live source

**Date:** 2026-09-12 · **Base:** `77d921e` (PR #21 + #22 merged)

Nothing below is inherited from a prior receipt. Each requirement was re-read
from current source, and each classification names the implementation path, the
serving path that reaches it, the persistence path, the test, and the
perturbation that proves the test binds.

---

## W0-G — audit chain

### Starting classification (measured BEFORE this lane's changes)

```
W0G_STARTING_CLASSIFICATION=RESIDUE_REMAINING
```

Verified from source, not assumed:

| CP-2 W0-G target | State at `77d921e` |
|---|---|
| chain computed on every audit write | delivered — `main.py::_audit` |
| verification surfaced | delivered — `GET /audit/chain/verify` |
| fork/gap detectable and reportable | delivered — T-CHAIN-01/02/03 |
| never silently healed | delivered — T-CHAIN-04 |
| `prev_hash`, `event_hash` columns | authored — `0028`, not applied |
| **chain persisted** | **NOT DELIVERED** |

The live finding: the authoritative writer was `_audit_log`, a module-level
Python list; no audit repository existed; no `audit_event` row was ever written
by any code path. W0-G's own receipt records why — *"requires W0-F,
Sponsor-gated"* — and W0-F is now complete, so that dependency is discharged and
the remaining work is non-production engineering needing no approval.

### Final classification

```
W0G_FINAL_STATUS=READY_PENDING_PRODUCTION_GATE
AUDIT_REPOSITORY_IMPLEMENTED=YES     petcare_api/audit_repository.py
AUDIT_POSTGRES_IMPLEMENTED=YES       0032_w0g_audit_chain_persistence.sql
AUDIT_SERVING_PATH_WIRED=YES         main.py::_audit -> AUDIT_REPO.append_event
AUDIT_BACKEND_TESTED=POSTGRESQL_AND_IN_MEMORY
```

| Element | Path |
|---|---|
| implementation | `petcare_api/audit_repository.py` — protocol, in-memory, PostgreSQL |
| serving path | `main.py::_audit()`, reached by 10 governed call sites and by `POST /audit/ui` |
| persistence | `audit_event` (+`0028` chain columns, +`0032` `chain_seq`), `audit_chain_head` |
| tests | `test_audit_persistence_postgres.py` (22), `test_audit_chain_wired.py` (6) |
| perturbations | 7, each proven applied — see `PERTURBATION_MATRIX.md` |

Only the production apply remains: no database is provisioned and `0032` is
authored, not applied. That is `GATE_LIVE_APPLY`.

### NOT rounded up — two items remain open and are not claimed closed

**1 · ARCH-01 — signatures or anchoring beyond the hash chain.** Carried forward
by W0-G's own receipt and untouched here. A hash chain detects tampering by
anyone without write access to the whole log; it does not defend against an
actor who can rewrite every row and recompute every digest. Persistence does not
change that, and `test_aud_09` asserts the limit explicitly rather than letting
the chain's verification imply more than it proves. This is a specification
question against V3.2 §25/§26, not implementation residue.

**2 · `AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN`.** `routers/auth.py` had its own `_audit`
— same name as the governed writer, and only a log line. Thirteen authentication
events (sign-in success and failure, registration, sign-out) are not hashed, not
linked, not persisted, not verifiable.

Renamed to `_log_auth_event` so the two can no longer be confused, and **not**
routed into the chain, because doing so would require inventing a tenant: a
governed record needs one (`audit_event.tenant_id` is `NOT NULL`) and a failed
sign-in has no authenticated actor, no established tenant, and often no identity.
A default tenant is exactly what W0-C removed. Closing this needs a governed
answer on how a tenantless security event is recorded — it is recorded as an open
gap rather than closed by guessing.

---

## W0-H — seller identity

```
W0H_LIVE_STATUS=READY_PENDING_PRODUCTION_GATE
```

Re-measured, not inherited:

| Element | Finding |
|---|---|
| implementation | `0029_w0h_seller_identity.sql` — `seller_id`, `seller_registration_id`, `seller_identity_source`, `gross_value` added to `partner_orders` |
| serving path | **none in `petcare_api`** — `seller_id` has 0 occurrences there; commerce lives in `petcare_runtime` |
| persistence | additive columns, NULLable; `ALTER ... SET NOT NULL` present as a commented step with its recorded precondition |
| test | `tests/governance/test_seller_identity_write_authority.py` — 7 controls |
| perturbation | covered by `test_migration_invariants.py` I-2/I-2b, which are perturbation-proven in the W0-J lane |

Nothing is blocked on design or on unwritten code. The enforcement step needs a
populated table to validate against, which is `GATE_LIVE_APPLY`. This is the
staged shape CP-2's W0-H `MIGRATION_DESIGN` prescribes — additive, then classify,
then record unresolved, then validate, then enforce — and demanding `NOT NULL`
today would push authors toward guessing values for historical rows.

---

## W0-J — password KDF and persisted identity

```
W0J_LIVE_STATUS=READY_PENDING_PRODUCTION_GATE
W0J_BLOCKED_ALSO_ON=PRE-1 (a Sponsor decision, not a gate)
```

| Element | Finding |
|---|---|
| KDF | `hashlib.scrypt`, n=2^14, r=8, p=1, parameters stored in the hash — `auth.py::_hash_password` |
| serving path | `POST /api/auth/sign-in`, `POST /api/auth/register` |
| persistence | `user_identity` (`0031`); rehash-on-next-login writes through `IDENTITY_REPO.set_password_hash` |
| test | `test_password_kdf.py` (7), `test_postgres_integration.py`, `test_identity_migration_*` (48) |
| perturbation | MIG-03/04/05/06/07 and the P-SEC/P-DB set, all proven applied |

Remaining: the identity migration apply, which is `GATE_LIVE_APPLY` +
`GATE_IRREVERSIBLE_ACTION` — and which, today, would migrate nobody. See
`PRE1_TENANT_DISCOVERY.md`.

---

## Summary

```
W0G_STATUS=READY_PENDING_PRODUCTION_GATE   (2 open items recorded, not claimed closed)
W0H_STATUS=READY_PENDING_PRODUCTION_GATE
W0J_STATUS=READY_PENDING_PRODUCTION_GATE   + PRE-1
```

None is `CLEAN`, and none is claimed to be.
