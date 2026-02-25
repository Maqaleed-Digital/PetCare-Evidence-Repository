"""
Audit Event Ledger — PH24 In-Memory Implementation
PetCare KSA | Deterministic Tenant-Scoped Append-Only Ledger

Properties:
- Append-only: no update/delete
- Tenant-scoped isolation
- Deterministic checksum and tamper-evident hash chain (prev_checksum -> checksum)
- Query + export supported
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from FND.CODE_SCAFFOLD.interfaces.audit_interface import AuditEvent, AuditExport, AuditQuery


class TenantRequiredError(ValueError):
    pass


def _utc_now_iso_ms() -> str:
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _stable_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _compute_event_checksum(content: Dict[str, Any]) -> str:
    return _sha256_hex(_stable_json(content))


def _compute_event_id(tenant_id: str, sequence: int, timestamp_utc: str, actor_id: str, event_name: str) -> str:
    base = f"{tenant_id}:{sequence}:{timestamp_utc}:{actor_id}:{event_name}"
    return _sha256_hex(base)[:32]


class MemoryAuditLedger:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: Dict[str, List[AuditEvent]] = {}
        self._index: Dict[str, Dict[str, AuditEvent]] = {}
        self._seq: Dict[str, int] = {}

    def _norm_tenant(self, tenant_id: str) -> str:
        if tenant_id is None or not str(tenant_id).strip():
            raise TenantRequiredError("tenant_id is required")
        return str(tenant_id).strip()

    def get_latest_sequence(self, tenant_id: str) -> int:
        tid = self._norm_tenant(tenant_id)
        return self._seq.get(tid, 0)

    def append(
        self,
        tenant_id: str,
        event_name: str,
        category: str,
        severity: str,
        actor_id: str,
        actor_type: str,
        action: str,
        payload: Dict[str, Any],
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> AuditEvent:
        tid = self._norm_tenant(tenant_id)

        with self._lock:
            seq = self._seq.get(tid, 0) + 1
            ts = _utc_now_iso_ms()

            prev_checksum: Optional[str] = None
            if tid in self._events and self._events[tid]:
                prev_checksum = self._events[tid][-1].checksum

            event_id = _compute_event_id(
                tenant_id=tid,
                sequence=seq,
                timestamp_utc=ts,
                actor_id=str(actor_id),
                event_name=str(event_name),
            )

            checksum_content = {
                "event_id": event_id,
                "tenant_id": tid,
                "sequence": seq,
                "timestamp_utc": ts,
                "event_name": str(event_name),
                "category": str(category),
                "severity": str(severity),
                "actor_id": str(actor_id),
                "actor_type": str(actor_type),
                "action": str(action),
                "resource_type": resource_type,
                "resource_id": resource_id,
                "payload": payload,
                "prev_checksum": prev_checksum,
            }
            checksum = _compute_event_checksum(checksum_content)

            ev = AuditEvent(
                event_id=event_id,
                tenant_id=tid,
                sequence=seq,
                timestamp_utc=ts,
                event_name=str(event_name),
                category=str(category),
                severity=str(severity),
                actor_id=str(actor_id),
                actor_type=str(actor_type),
                action=str(action),
                resource_type=resource_type,
                resource_id=resource_id,
                payload=payload,
                prev_checksum=prev_checksum,
                checksum=checksum,
            )

            self._events.setdefault(tid, []).append(ev)
            self._index.setdefault(tid, {})[event_id] = ev
            self._seq[tid] = seq

            return ev

    def get_by_id(self, tenant_id: str, event_id: str) -> Optional[AuditEvent]:
        tid = self._norm_tenant(tenant_id)
        return self._index.get(tid, {}).get(event_id)

    def query(self, query: AuditQuery) -> List[AuditEvent]:
        tid = self._norm_tenant(query.tenant_id)
        events = self._events.get(tid, [])

        out: List[AuditEvent] = []
        for ev in events:
            if query.category and ev.category != query.category:
                continue
            if query.severity and ev.severity != query.severity:
                continue
            if query.actor_id and ev.actor_id != query.actor_id:
                continue
            if query.event_name and ev.event_name != query.event_name:
                continue
            if query.resource_type and ev.resource_type != query.resource_type:
                continue
            if query.resource_id and ev.resource_id != query.resource_id:
                continue
            if query.start_time_utc and ev.timestamp_utc < query.start_time_utc:
                continue
            if query.end_time_utc and ev.timestamp_utc > query.end_time_utc:
                continue
            out.append(ev)

        start = max(0, int(query.offset))
        limit = max(0, int(query.limit))
        end = start + limit if limit else len(out)
        return out[start:end]

    def verify_chain(
        self,
        tenant_id: str,
        start_sequence: Optional[int] = None,
        end_sequence: Optional[int] = None,
    ) -> bool:
        tid = self._norm_tenant(tenant_id)
        events = self._events.get(tid, [])
        if not events:
            return True

        filtered = events
        if start_sequence is not None:
            filtered = [e for e in filtered if e.sequence >= start_sequence]
        if end_sequence is not None:
            filtered = [e for e in filtered if e.sequence <= end_sequence]

        filtered = sorted(filtered, key=lambda e: e.sequence)
        for i, ev in enumerate(filtered):
            if i == 0:
                if ev.sequence == 1 and ev.prev_checksum is not None:
                    return False
                continue
            prev = filtered[i - 1]
            if ev.prev_checksum != prev.checksum:
                return False
        return True

    def export(
        self,
        tenant_id: str,
        start_sequence: Optional[int] = None,
        end_sequence: Optional[int] = None,
    ) -> AuditExport:
        tid = self._norm_tenant(tenant_id)
        events = self._events.get(tid, [])

        if start_sequence is not None:
            events = [e for e in events if e.sequence >= start_sequence]
        if end_sequence is not None:
            events = [e for e in events if e.sequence <= end_sequence]

        events = sorted(events, key=lambda e: e.sequence)
        event_dicts = [asdict(e) for e in events]

        exported_at = _utc_now_iso_ms()
        export_id = uuid.uuid4().hex[:16]

        first_seq = events[0].sequence if events else 0
        last_seq = events[-1].sequence if events else 0

        export_checksum = ""
        if event_dicts:
            export_checksum = _sha256_hex(_stable_json({"tenant_id": tid, "events": event_dicts}))

        return AuditExport(
            tenant_id=tid,
            export_id=export_id,
            exported_at_utc=exported_at,
            event_count=len(events),
            first_sequence=first_seq,
            last_sequence=last_seq,
            events=event_dicts,
            checksum=export_checksum,
        )

    def count(self, tenant_id: str, category: Optional[str] = None, severity: Optional[str] = None) -> int:
        tid = self._norm_tenant(tenant_id)
        events = self._events.get(tid, [])
        c = 0
        for ev in events:
            if category and ev.category != category:
                continue
            if severity and ev.severity != severity:
                continue
            c += 1
        return c


_default: Optional[MemoryAuditLedger] = None


def get_audit_ledger() -> MemoryAuditLedger:
    global _default
    if _default is None:
        _default = MemoryAuditLedger()
    return _default


def reset_audit_ledger() -> None:
    global _default
    _default = None


__all__ = [
    "MemoryAuditLedger",
    "TenantRequiredError",
    "get_audit_ledger",
    "reset_audit_ledger",
]
