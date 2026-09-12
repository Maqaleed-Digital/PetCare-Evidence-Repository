"""W0-G — the audit chain, persisted.

CP-2 defines W0-G as integration work, and its receipt records exactly one
target as not delivered:

```
| chain **persisted**  | NO — requires W0-F, Sponsor-gated |
```

W0-F is done. That row is now non-production engineering, and this module is it.
Nothing about the hashing changes: `petcare_execution/FND/security/audit_chain.py`
is reused unmodified, per W0-G's disposition *"REUSE the algorithm — do NOT
reinvent hashing."*

## What persistence adds, and what it does not

W0-G made tampering **detectable**. It did not make the log **durable**: the
store was `_audit_log`, a list that died with the process and was not shared
between instances. Those are two different properties and the service reports
them as two fields precisely so neither can be mistaken for the other.

This module closes durability. It does **not** close the open question W0-G
carried forward — whether ARCH-01 requires signatures or external anchoring
beyond a hash chain. A hash chain detects tampering by anyone without write
access to the whole log; it does not defend against an actor who can rewrite
every row and recompute every digest. That remains open and is not claimed here.

## The hashed record is EXACTLY the governed fields

`verify_hash_chain` recomputes a digest over the record with `hash` and
`prev_hash` removed. So any field that reaches the stored record but not the
hashed record — or the reverse — produces a chain that links correctly and
verifies as BROKEN every time.

That is not hypothetical: W0-G's own receipt records the first implementation
hashing the record *after* attaching `prev_hash`, giving a chain that looked
wired and could never verify. `GOVERNED_EVENT_FIELDS` exists so that the write
path and the verify path cannot disagree about which fields are covered.
`chain_seq` is deliberately NOT among them — it is storage ordering, not content.

## Why the repository owns chain linkage

`prev_hash` is "the previous event's digest", which is a read-then-write. Two
concurrent appends that both read the same head produce a fork — two events
claiming the same predecessor — and `verify_hash_chain` reports that as
`prev_hash_mismatch`, i.e. as tampering. A correct log would be indistinguishable
from an attacked one.

So linkage happens inside the repository, inside one transaction, serialised on a
single head row. A caller cannot get it wrong because a caller cannot do it.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Iterable, Mapping, Optional, Protocol

# The governed algorithm lives in the foundations tree and is REUSED, never
# reimplemented (CP-2 W0-G DISPOSITION).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from petcare_execution.FND.security.audit_chain import (  # noqa: E402
    compute_event_hash,
    verify_hash_chain,
)

#: The chain's starting digest. Named in one place so the serving path and the
#: persisted store cannot drift apart on it.
AUDIT_CHAIN_GENESIS = "GENESIS"

#: The single chain. A second chain id would mean two orderings of one log, and
#: nothing could then say which came first across them.
DEFAULT_CHAIN_ID = "default"

#: Exactly the fields the digest covers, in the order the record is built.
#:
#: Changing this set changes every future digest and invalidates verification of
#: every existing row, so it is a schema-and-chain migration, never an edit.
GOVERNED_EVENT_FIELDS = (
    "audit_event_id",
    "event_name",
    "actor_id",
    "actor_role",
    "tenant_id",
    "clinic_id",
    "resource_type",
    "resource_id",
    "action_result",
    "reason_code",
    "correlation_id",
    "occurred_at",
)


class AuditWriteFailed(RuntimeError):
    """An audit event could not be recorded.

    Raised rather than swallowed, and callers must not catch it to continue. An
    action that mutates state while its audit write silently fails is an
    unaudited mutation — and afterwards it is indistinguishable from an action
    that never happened. Failing the request is the direction that keeps the log
    a record of what occurred.
    """


class AuditReadDenied(Exception):
    """A read was refused because it would cross a tenant boundary."""


def core_record(record: Mapping[str, Any]) -> dict:
    """The governed fields only, in governed order.

    Anything else the caller passes is dropped rather than hashed. A record that
    silently grew a field would change every subsequent digest, and the resulting
    verification failure would point at the chain rather than at the new field.
    """
    return {field: record.get(field) for field in GOVERNED_EVENT_FIELDS}


def adapt_for_verifier(stored: Mapping[str, Any]) -> dict:
    """A stored row in the shape `verify_hash_chain` expects.

    The algorithm names the digest `hash`; the governed schema names the column
    `event_hash` (CP-2 W0-G SCHEMA_IMPACT). Adapted at this boundary rather than
    by editing the algorithm, because W0-G's disposition is REUSE.
    """
    core = core_record(stored)
    core["prev_hash"] = stored.get("prev_hash")
    core["hash"] = stored.get("event_hash")
    return core


def verify_chain_over(events: Iterable[Mapping[str, Any]]) -> dict:
    """Verify a sequence of stored rows. Reports a break; never repairs one."""
    adapted = [adapt_for_verifier(e) for e in events]
    result = verify_hash_chain(adapted, genesis=AUDIT_CHAIN_GENESIS)
    return {
        "ok": result.ok,
        "reason": result.reason,
        "index": result.index,
        "expected": result.expected,
        "actual": result.actual,
        "events": len(adapted),
    }


class AuditRepository(Protocol):
    """What the serving path depends on. No SQL at a call site, ever."""

    #: Whether events written here survive the process.
    durable: bool

    def append_event(self, record: Mapping[str, Any]) -> dict:
        """Link and store one event. Returns the stored record."""
        ...

    def get_event(self, audit_event_id: str, *, tenant_id: str) -> Optional[dict]:
        """One event, only within the caller's tenant."""
        ...

    def query_events_for_tenant(self, tenant_id: str, *, limit: int = 100) -> list[dict]:
        """A tenant's events, and no other tenant's."""
        ...

    def all_events(self) -> list[dict]:
        """The whole chain, in chain order. PRIVILEGED — see below."""
        ...

    def verify_chain(self) -> dict: ...

    def count(self) -> int: ...


# ---------------------------------------------------------------------------
# In memory — non-production, and dying with the process is the point
# ---------------------------------------------------------------------------

class InMemoryAuditRepository:
    """The prior behaviour, behind the boundary.

    Kept because the test suite and local development run on it, and because
    every W0-G chain control was written against it — so the persistent
    implementation is held to semantics that already exist rather than to new
    ones. What it does not provide is durability, which is the whole of this
    module's purpose.
    """

    durable = False

    def __init__(self) -> None:
        self._events: list[dict] = []

    def append_event(self, record: Mapping[str, Any]) -> dict:
        core = core_record(record)
        prev_hash = self._events[-1]["event_hash"] if self._events else AUDIT_CHAIN_GENESIS
        stored = dict(core)
        stored["prev_hash"] = prev_hash
        stored["event_hash"] = compute_event_hash(prev_hash, core)
        stored["chain_seq"] = len(self._events) + 1
        self._events.append(stored)
        return stored

    def get_event(self, audit_event_id: str, *, tenant_id: str) -> Optional[dict]:
        for e in self._events:
            if e["audit_event_id"] == audit_event_id:
                # Not found and not yours are ONE answer. Telling a caller that
                # an id exists in another tenant is a cross-tenant oracle.
                return e if e.get("tenant_id") == tenant_id else None
        return None

    def query_events_for_tenant(self, tenant_id: str, *, limit: int = 100) -> list[dict]:
        return [e for e in self._events if e.get("tenant_id") == tenant_id][:limit]

    def all_events(self) -> list[dict]:
        return list(self._events)

    def verify_chain(self) -> dict:
        return verify_chain_over(self._events)

    def count(self) -> int:
        return len(self._events)


# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

#: `audit_event` names two columns with a `_nullable` suffix that the governed
#: record does not. Mapped explicitly here: a mismatch would store the event
#: under a key the hash never covered, and verification would fail against a row
#: that was written correctly.
_COLUMN_BY_FIELD = {
    "clinic_id": "clinic_id_nullable",
    "reason_code": "reason_code_nullable",
}


def _column(field: str) -> str:
    return _COLUMN_BY_FIELD.get(field, field)


_SELECT_COLUMNS = ", ".join(
    f"{_column(f)}" for f in GOVERNED_EVENT_FIELDS
) + ", prev_hash, event_hash, chain_seq"


def _row_to_record(row: Any) -> dict:
    out = {field: row[i] for i, field in enumerate(GOVERNED_EVENT_FIELDS)}
    n = len(GOVERNED_EVENT_FIELDS)
    out["prev_hash"] = row[n]
    out["event_hash"] = row[n + 1]
    out["chain_seq"] = row[n + 2]
    return out


class PostgresAuditRepository:
    """`AuditRepository` backed by `audit_event` + `audit_chain_head`.

    The semantics are the in-memory ones. Durability is what is added.
    """

    durable = True

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    def append_event(self, record: Mapping[str, Any]) -> dict:
        """Link and store, atomically, serialised on the chain head.

        The `FOR UPDATE` on a single head row is what makes concurrent appends
        safe. Without it two writers read the same head, both link to it, and the
        verifier reports `prev_hash_mismatch` — a correct log indistinguishable
        from an attacked one.
        """
        core = core_record(record)
        try:
            with self._pool.connection() as conn:
                with conn.transaction():
                    head = conn.execute(
                        "SELECT head_hash, next_seq FROM audit_chain_head "
                        "WHERE chain_id = %s FOR UPDATE",
                        (DEFAULT_CHAIN_ID,),
                    ).fetchone()
                    if head is None:
                        raise AuditWriteFailed(
                            "the audit chain head row is missing; refusing to "
                            "start a second chain, which would leave two "
                            "orderings of one log"
                        )
                    prev_hash, seq = head[0], head[1]
                    event_hash = compute_event_hash(prev_hash, core)

                    cols = ", ".join(_column(f) for f in GOVERNED_EVENT_FIELDS)
                    marks = ", ".join(["%s"] * len(GOVERNED_EVENT_FIELDS))
                    conn.execute(
                        f"INSERT INTO audit_event ({cols}, prev_hash, event_hash, chain_seq) "
                        f"VALUES ({marks}, %s, %s, %s)",
                        tuple(core[f] for f in GOVERNED_EVENT_FIELDS)
                        + (prev_hash, event_hash, seq),
                    )
                    conn.execute(
                        "UPDATE audit_chain_head SET head_hash = %s, next_seq = %s, "
                        "updated_at = CURRENT_TIMESTAMP WHERE chain_id = %s",
                        (event_hash, seq + 1, DEFAULT_CHAIN_ID),
                    )
        except AuditWriteFailed:
            raise
        except Exception as exc:
            # Never swallowed. An unaudited mutation is indistinguishable
            # afterwards from one that never happened.
            raise AuditWriteFailed(
                f"the audit event could not be recorded ({type(exc).__name__}); "
                "the action it describes must not be reported as successful"
            ) from None

        stored = dict(core)
        stored["prev_hash"] = prev_hash
        stored["event_hash"] = event_hash
        stored["chain_seq"] = seq
        return stored

    def get_event(self, audit_event_id: str, *, tenant_id: str) -> Optional[dict]:
        with self._pool.connection() as conn:
            row = conn.execute(
                f"SELECT {_SELECT_COLUMNS} FROM audit_event "
                "WHERE audit_event_id = %s AND tenant_id = %s",
                (audit_event_id, tenant_id),
            ).fetchone()
        return _row_to_record(row) if row else None

    def query_events_for_tenant(self, tenant_id: str, *, limit: int = 100) -> list[dict]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                f"SELECT {_SELECT_COLUMNS} FROM audit_event "
                "WHERE tenant_id = %s ORDER BY chain_seq LIMIT %s",
                (tenant_id, limit),
            ).fetchall()
        return [_row_to_record(r) for r in rows]

    def all_events(self) -> list[dict]:
        """The whole chain, in chain order.

        PRIVILEGED and cross-tenant by necessity: the chain is one sequence over
        every tenant, so verifying it requires reading all of it. Authorization
        for that lives on the route (`require_admin`), not here — a repository
        that decided authorization would be a second place for an authorization
        bug to live.

        Ordered by `chain_seq`, never by `occurred_at`: two events in the same
        instant would tie, and a tie reorders the chain into a verification
        failure that looks exactly like tampering.
        """
        with self._pool.connection() as conn:
            rows = conn.execute(
                f"SELECT {_SELECT_COLUMNS} FROM audit_event "
                "WHERE chain_seq IS NOT NULL ORDER BY chain_seq"
            ).fetchall()
        return [_row_to_record(r) for r in rows]

    def verify_chain(self) -> dict:
        return verify_chain_over(self.all_events())

    def count(self) -> int:
        with self._pool.connection() as conn:
            return conn.execute(
                "SELECT count(*) FROM audit_event WHERE chain_seq IS NOT NULL"
            ).fetchone()[0]
