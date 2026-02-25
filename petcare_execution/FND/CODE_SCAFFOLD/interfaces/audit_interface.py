"""
Audit Interface — PH24 Tenant-Scoped Audit Event Ledger Contract
PetCare KSA | Deterministic Tenant-Scoped Audit

Contract:
- Append-only ledger per tenant
- Deterministic hashing for checksums
- Hash-chained integrity (prev_checksum -> checksum)
- Query and export support (in-memory implementation)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    tenant_id: str
    sequence: int
    timestamp_utc: str
    event_name: str
    category: str
    severity: str
    actor_id: str
    actor_type: str
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    payload: Dict[str, Any]
    prev_checksum: Optional[str]
    checksum: str


@dataclass(frozen=True)
class AuditQuery:
    tenant_id: str
    start_time_utc: Optional[str] = None
    end_time_utc: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    actor_id: Optional[str] = None
    event_name: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class AuditExport:
    tenant_id: str
    export_id: str
    exported_at_utc: str
    event_count: int
    first_sequence: int
    last_sequence: int
    events: List[Dict[str, Any]]
    checksum: str


class IAuditLedger(Protocol):
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
        ...

    def query(self, query: AuditQuery) -> List[AuditEvent]:
        ...

    def get_by_id(self, tenant_id: str, event_id: str) -> Optional[AuditEvent]:
        ...

    def get_latest_sequence(self, tenant_id: str) -> int:
        ...

    def verify_chain(
        self,
        tenant_id: str,
        start_sequence: Optional[int] = None,
        end_sequence: Optional[int] = None,
    ) -> bool:
        ...

    def export(
        self,
        tenant_id: str,
        start_sequence: Optional[int] = None,
        end_sequence: Optional[int] = None,
    ) -> AuditExport:
        ...

    def count(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> int:
        ...


__all__ = [
    "AuditEvent",
    "AuditQuery",
    "AuditExport",
    "IAuditLedger",
]
