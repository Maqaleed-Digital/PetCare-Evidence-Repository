# A12 — W0-G / W0-H / W0-J, reclassified against the completed W0-F

**Date:** 2026-09-12 · **Basis:** live source inspection, not the prior receipt.

The previous receipt classified all three as `READY_PENDING_PRODUCTION_GATE`, on
the reading that each waited only on a gated apply. With W0-F's persistence
boundary now built, that reading can be checked rather than assumed — and for one
of the three it does not hold.

---

## W0-G — audit chain

```
W0G_STATUS=RESIDUE_REMAINING
REASON=the audit writer is not wired to the persistence boundary; that is
       non-production engineering, and it is not done
```

### What changed

The obstacle W0-G was recorded as waiting on — "the store provisioned and
migration `0028` applied" — is now only half the story. `0028` replays cleanly
against PostgreSQL 16 and the adapter that would carry the writes exists.

### What is actually missing

The serving path still appends to `main.py::_audit_log`, a list. There is no
audit repository, and nothing in `petcare_api` writes an `audit_event` row. The
service already reports this honestly:

```python
def _audit_chain_persisted() -> bool:
    return False
```

So W0-G's remaining dependency is **not** a gate. It is an unwritten adapter, and
calling it `READY_PENDING_PRODUCTION_GATE` would put a non-production engineering
task behind a Sponsor gate where it would wait for an approval that was never the
blocker.

### Why it was not done in this change

W0-G owns audit durability and `0028` is its migration. Writing a second audit
path here would create two writers for one chain, and a chain with two writers
cannot establish ordering — which is the single property the chain exists to
provide. See `ARCHITECTURE_STATE.md`.

### What closing it now requires

An `AuditRepository` behind the same boundary as the others, `_audit_log`
replaced by it, `_audit_chain_persisted()` computing from the store, and the
chain-continuity controls re-run against PostgreSQL. All non-production. None of
it needs a gate.

---

## W0-H — seller identity

```
W0H_STATUS=READY_PENDING_PRODUCTION_GATE
REASON=migration 0029 is authored and staged; the SET NOT NULL step carries a
       recorded precondition and needs a populated table to validate against
```

Verified rather than restated: `seller_id` appears nowhere in `petcare_api` —
commerce lives in `petcare_runtime`, and the serving API does not touch it. The
staged enforcement step in `0029` is commented with its precondition, which is the
shape `test_migration_invariants.py` I-2b requires and the shape CP-2's W0-H
`MIGRATION_DESIGN` prescribes (additive → classify → record unresolved → validate
→ only then enforce).

Nothing here is blocked on design or on unwritten code. It is blocked on a
database with rows in it, which is `GATE_LIVE_APPLY`.

---

## W0-J — password KDF and persisted identity

```
W0J_STATUS=READY_PENDING_PRODUCTION_GATE
REASON=the identity migration is rehearsed and its apply is gated
BLOCKED_ALSO_ON=a Sponsor tenant-assignment decision (see below)
```

### Materially advanced by this change

| Was | Now |
|---|---|
| `AC-8` satisfied by scrypt | unchanged |
| "persisted user store" absent | `user_identity` authored, adapter implemented, integration-proven |
| identity migration not authored | authored, rehearsed, reconciled, 10 controls |
| rehash-on-next-login **lost at every restart** | written through the repository; the upgrade now survives the process |

That fourth row was a silent defect, not merely missing durability: W0-J's
credential migration completed for nobody, because every upgraded hash was
discarded when the process restarted and the legacy hash came back.

### The precondition that is NOT a gate

The dry-run against the live source returns:

```
IDENTITY_SOURCE_COUNT=3
IDENTITY_MIGRATABLE_COUNT=0
IDENTITY_QUARANTINED_COUNT=3   (all UNRESOLVED_NO_TENANT)
```

All three pilot identities carry no tenant assignment, and the plan forbids
inferring one. **A production identity migration run today would migrate nobody
and quarantine everybody.**

This is the migration behaving correctly, and it means P4 of the activation pack
cannot produce a useful result until the Sponsor assigns tenants to the pilot
identities — or confirms that the production identity set is a different one.
That is a **decision**, not one of the five gates, and it is recorded here so it
is resolved before the window rather than inside it.

```
W0J_PRECONDITION=SPONSOR_TENANT_ASSIGNMENT_FOR_PILOT_IDENTITIES
```

---

## Summary

```
W0G_STATUS=RESIDUE_REMAINING          non-production engineering, no gate needed
W0H_STATUS=READY_PENDING_PRODUCTION_GATE
W0J_STATUS=READY_PENDING_PRODUCTION_GATE  + a Sponsor tenant decision
```

None is `CLEAN`, and none is claimed to be.
