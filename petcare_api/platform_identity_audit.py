"""SQ-1 (Sponsor act MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001) — the PLATFORM IDENTITY AUDIT CHAIN (v1.2 U26).

Ratified: registration and failed sign-in are account actions. Pre-tenant identity/security events go to a SEPARATE
platform identity audit chain — no fake/sentinel tenant, and the tenant chain's tenant-required invariant is not
weakened. A failed sign-in belongs to this chain even when the targeted identity has a tenant.

Same hashing as the tenant chain (`compute_event_hash` / `verify_hash_chain` from petcare_execution.FND.security.
audit_chain, genesis "GENESIS"); its own table and its own head row, serialised FOR UPDATE. There is no tenant field.
An unknown identity is recorded by the SHA-256 of its normalised e-mail, never the address itself.
"""
from __future__ import annotations

import hashlib
import os
import sys
from typing import Any, Mapping, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from petcare_execution.FND.security.audit_chain import compute_event_hash, verify_hash_chain  # noqa: E402

GENESIS = "GENESIS"
CHAIN_ID = "platform-identity"
FIELDS = ("event_id", "event_name", "subject_kind", "subject_ref", "outcome", "reason_code", "correlation_id",
          "occurred_at")
SUBJECT_IDENTITY, SUBJECT_UNKNOWN = "IDENTITY", "UNKNOWN_IDENTITY"


class PlatformAuditWriteFailed(RuntimeError):
    pass


def email_ref(email: str) -> str:
    return "email-sha256:" + hashlib.sha256((email or "").strip().lower().encode()).hexdigest()


def core(record: Mapping[str, Any]) -> dict:
    missing = [f for f in FIELDS if f not in record]
    if missing:
        raise PlatformAuditWriteFailed(f"missing fields {missing}")
    if "tenant_id" in record:
        raise PlatformAuditWriteFailed("the platform identity chain carries no tenant")
    return {f: record[f] for f in FIELDS}


def verify(events) -> dict:
    adapted = [{**{f: e[f] for f in FIELDS}, "prev_hash": e["prev_hash"], "hash": e["event_hash"]} for e in events]
    r = verify_hash_chain(adapted, genesis=GENESIS)
    return {"ok": r.ok, "count": len(adapted), **({} if r.ok else {"reason": getattr(r, "reason", None)})}


class InMemoryPlatformIdentityAudit:
    def __init__(self) -> None:
        self._events: list = []

    def append(self, record: Mapping[str, Any]) -> dict:
        c = core(record)
        prev = self._events[-1]["event_hash"] if self._events else GENESIS
        stored = {**c, "prev_hash": prev, "event_hash": compute_event_hash(prev, c), "chain_seq": len(self._events) + 1}
        self._events.append(stored)
        return stored

    def events(self, limit: Optional[int] = None) -> list:
        return list(self._events) if limit is None else self._events[-limit:]

    def verify(self) -> dict:
        return verify(self._events)
