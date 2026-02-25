"""
SQLite Audit Ledger — PH26 Persistence Adapter
PetCare KSA | Tenant-Scoped Append-Only SQLite Storage

Guarantees:
- Per-tenant SQLite DB files (hard isolation)
- Append-only semantics (adapter never UPDATE/DELETE)
- Monotonic per-tenant sequence
- Hash-chain linking via prev_checksum -> checksum
- Interface-compatible with repo's AuditEvent/AuditExport via dataclass field filtering

Storage Layout:
    data/audit/<tenant_id>.db
"""

import hashlib
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import asdict, fields, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Type, TypeVar

from ..interfaces.audit_interface import (
    IAuditLedger,
    AuditEvent,
    AuditQuery,
    AuditExport,
)

DEFAULT_DATA_DIR = "data/audit"
SCHEMA_VERSION = 1

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    tenant_id TEXT NOT NULL,
    event_name TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    action TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    payload TEXT NOT NULL,
    checksum TEXT NOT NULL,
    prev_checksum TEXT,
    created_at TEXT NOT NULL
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_events_tenant ON audit_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_events_sequence ON audit_events(tenant_id, sequence);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON audit_events(tenant_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_category ON audit_events(tenant_id, category);
CREATE INDEX IF NOT EXISTS idx_events_actor ON audit_events(tenant_id, actor_id);
"""

CREATE_METADATA_TABLE = """
CREATE TABLE IF NOT EXISTS ledger_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class TenantRequiredError(Exception):
    def __init__(self, message: str = "tenant_id is required"):
        super().__init__(message)


class ChainIntegrityError(Exception):
    def __init__(self, sequence: int, expected: str, actual: str):
        self.sequence = sequence
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Chain integrity violation at sequence {sequence}: expected {expected}, got {actual}"
        )


class DatabaseError(Exception):
    pass


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _stable_json_serialize(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _compute_checksum(data: Dict[str, Any]) -> str:
    serialized = _stable_json_serialize(data)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _compute_event_id(
    tenant_id: str,
    event_name: str,
    timestamp_utc: str,
    sequence: int,
    actor_id: str,
) -> str:
    id_input = f"{tenant_id}:{event_name}:{timestamp_utc}:{sequence}:{actor_id}"
    return hashlib.sha256(id_input.encode("utf-8")).hexdigest()[:32]


def _sanitize_tenant_id(tenant_id: str) -> str:
    sanitized = "".join(c if c.isalnum() or c in "-_" else "_" for c in tenant_id)
    return sanitized[:64]


T = TypeVar("T")


def _dataclass_field_names(cls: Type[Any]) -> List[str]:
    if not is_dataclass(cls):
        return []
    return [f.name for f in fields(cls)]


def _apply_timestamp_mapping(cls: Type[Any], data: Dict[str, Any], iso_ts: str) -> None:
    """
    No-guess timestamp mapping based on target dataclass fields:
    - AuditEvent requires timestamp_utc in this repo
    - AuditExport requires exported_at_utc in this repo
    - We set only fields that actually exist on the target dataclass
    """
    if not is_dataclass(cls):
        return

    names = set(_dataclass_field_names(cls))

    if "timestamp_utc" in names and "timestamp_utc" not in data:
        data["timestamp_utc"] = iso_ts

    if "timestamp" in names and "timestamp" not in data:
        data["timestamp"] = iso_ts

    if "exported_at_utc" in names and "exported_at_utc" not in data:
        data["exported_at_utc"] = iso_ts

    if "exported_at" in names and "exported_at" not in data:
        data["exported_at"] = iso_ts

    if "occurred_at" in names and "occurred_at" not in data:
        data["occurred_at"] = iso_ts

    if "event_time" in names and "event_time" not in data:
        data["event_time"] = iso_ts

    if "created_at" in names and "created_at" not in data:
        data["created_at"] = iso_ts

    if "ts" in names and "ts" not in data:
        data["ts"] = iso_ts


def _construct_dataclass(cls: Type[T], data: Dict[str, Any]) -> T:
    """
    No-guess constructor:
    - Applies timestamp mapping for required fields (timestamp_utc/exported_at_utc)
    - Only passes keys that exist in the target dataclass fields
    """
    if not is_dataclass(cls):
        return cls(**data)  # type: ignore

    iso_ts = (
        data.get("exported_at_utc")
        or data.get("exported_at")
        or data.get("timestamp_utc")
        or data.get("timestamp")
    )
    if iso_ts is None:
        iso_ts = _now_iso_utc()

    _apply_timestamp_mapping(cls, data, iso_ts)

    names = set(_dataclass_field_names(cls))
    filtered = {k: v for k, v in data.items() if k in names}
    return cls(**filtered)  # type: ignore


def _row_to_event(row: sqlite3.Row) -> AuditEvent:
    iso_ts = row["timestamp"]
    payload = json.loads(row["payload"])
    data: Dict[str, Any] = {
        "event_id": row["event_id"],
        "tenant_id": row["tenant_id"],
        "event_name": row["event_name"],
        "category": row["category"],
        "severity": row["severity"],
        "actor_id": row["actor_id"],
        "actor_type": row["actor_type"],
        "resource_type": row["resource_type"],
        "resource_id": row["resource_id"],
        "action": row["action"],
        "sequence": row["sequence"],
        "payload": payload,
        "checksum": row["checksum"],
        "prev_checksum": row["prev_checksum"],
        "timestamp_utc": iso_ts,
        "timestamp": iso_ts,
    }
    return _construct_dataclass(AuditEvent, data)


class SqliteAuditLedger(IAuditLedger):
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self._data_dir = data_dir
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()
        os.makedirs(self._data_dir, exist_ok=True)

    def _get_db_path(self, tenant_id: str) -> str:
        safe_id = _sanitize_tenant_id(tenant_id)
        return os.path.join(self._data_dir, f"{safe_id}.db")

    def _get_lock(self, tenant_id: str) -> threading.Lock:
        with self._global_lock:
            if tenant_id not in self._locks:
                self._locks[tenant_id] = threading.Lock()
            return self._locks[tenant_id]

    @contextmanager
    def _get_connection(self, tenant_id: str) -> Generator[sqlite3.Connection, None, None]:
        db_path = self._get_db_path(tenant_id)
        lock = self._get_lock(tenant_id)

        with lock:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                self._ensure_schema(conn, tenant_id)
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _ensure_schema(self, conn: sqlite3.Connection, tenant_id: str) -> None:
        cursor = conn.cursor()
        cursor.executescript(CREATE_EVENTS_TABLE)
        cursor.executescript(CREATE_INDEXES)
        cursor.executescript(CREATE_METADATA_TABLE)

        cursor.execute(
            """
            INSERT OR REPLACE INTO ledger_metadata (key, value, updated_at)
            VALUES ('schema_version', ?, ?)
            """,
            (str(SCHEMA_VERSION), _now_iso_utc()),
        )

        cursor.execute(
            """
            INSERT OR IGNORE INTO ledger_metadata (key, value, updated_at)
            VALUES ('tenant_id', ?, ?)
            """,
            (tenant_id, _now_iso_utc()),
        )

        conn.commit()

    def _validate_tenant_id(self, tenant_id: Optional[str]) -> str:
        if not tenant_id or not tenant_id.strip():
            raise TenantRequiredError()
        return tenant_id.strip()

    def _get_latest_event_row(self, conn: sqlite3.Connection, tenant_id: str) -> Optional[sqlite3.Row]:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM audit_events
            WHERE tenant_id = ?
            ORDER BY sequence DESC
            LIMIT 1
            """,
            (tenant_id,),
        )
        return cursor.fetchone()

    def _get_next_sequence(self, conn: sqlite3.Connection, tenant_id: str) -> int:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(MAX(sequence), 0) + 1 as next_seq
            FROM audit_events
            WHERE tenant_id = ?
            """,
            (tenant_id,),
        )
        row = cursor.fetchone()
        return row["next_seq"] if row else 1

    async def append(
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
        tenant_id = self._validate_tenant_id(tenant_id)

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()

            sequence = self._get_next_sequence(conn, tenant_id)
            latest = self._get_latest_event_row(conn, tenant_id)
            prev_checksum = latest["checksum"] if latest else None

            timestamp_utc = _now_iso_utc()
            event_id = _compute_event_id(tenant_id, event_name, timestamp_utc, sequence, actor_id)

            checksum_data = {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "event_name": event_name,
                "category": category,
                "severity": severity,
                "actor_id": actor_id,
                "actor_type": actor_type,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "timestamp_utc": timestamp_utc,
                "sequence": sequence,
                "payload": payload,
                "prev_checksum": prev_checksum,
            }
            checksum = _compute_checksum(checksum_data)

            cursor.execute(
                """
                INSERT INTO audit_events (
                    event_id, tenant_id, event_name, category, severity,
                    actor_id, actor_type, resource_type, resource_id,
                    action, timestamp, sequence, payload, checksum,
                    prev_checksum, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    tenant_id,
                    event_name,
                    category,
                    severity,
                    actor_id,
                    actor_type,
                    resource_type,
                    resource_id,
                    action,
                    timestamp_utc,
                    sequence,
                    _stable_json_serialize(payload),
                    checksum,
                    prev_checksum,
                    _now_iso_utc(),
                ),
            )

            conn.commit()

            data: Dict[str, Any] = {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "event_name": event_name,
                "category": category,
                "severity": severity,
                "actor_id": actor_id,
                "actor_type": actor_type,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "timestamp_utc": timestamp_utc,
                "timestamp": timestamp_utc,
                "sequence": sequence,
                "payload": payload,
                "checksum": checksum,
                "prev_checksum": prev_checksum,
            }
            return _construct_dataclass(AuditEvent, data)

    async def query(self, query: AuditQuery) -> List[AuditEvent]:
        tenant_id = self._validate_tenant_id(getattr(query, "tenant_id", None))

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()

            sql = "SELECT * FROM audit_events WHERE tenant_id = ?"
            params: List[Any] = [tenant_id]

            if getattr(query, "category", None):
                sql += " AND category = ?"
                params.append(query.category)

            if getattr(query, "severity", None):
                sql += " AND severity = ?"
                params.append(query.severity)

            if getattr(query, "actor_id", None):
                sql += " AND actor_id = ?"
                params.append(query.actor_id)

            if getattr(query, "resource_type", None):
                sql += " AND resource_type = ?"
                params.append(query.resource_type)

            if getattr(query, "resource_id", None):
                sql += " AND resource_id = ?"
                params.append(query.resource_id)

            if getattr(query, "event_name", None):
                sql += " AND event_name = ?"
                params.append(query.event_name)

            if getattr(query, "start_time", None):
                sql += " AND timestamp >= ?"
                params.append(query.start_time)

            if getattr(query, "end_time", None):
                sql += " AND timestamp <= ?"
                params.append(query.end_time)

            limit = int(getattr(query, "limit", 100))
            offset = int(getattr(query, "offset", 0))

            sql += " ORDER BY sequence ASC"
            sql += f" LIMIT {limit} OFFSET {offset}"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [_row_to_event(r) for r in rows]

    async def get_by_id(self, tenant_id: str, event_id: str) -> Optional[AuditEvent]:
        tenant_id = self._validate_tenant_id(tenant_id)

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM audit_events
                WHERE tenant_id = ? AND event_id = ?
                """,
                (tenant_id, event_id),
            )
            row = cursor.fetchone()
            return _row_to_event(row) if row else None

    async def get_sequence_range(self, tenant_id: str, start_sequence: int, end_sequence: int) -> List[AuditEvent]:
        tenant_id = self._validate_tenant_id(tenant_id)

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM audit_events
                WHERE tenant_id = ? AND sequence >= ? AND sequence <= ?
                ORDER BY sequence ASC
                """,
                (tenant_id, start_sequence, end_sequence),
            )
            rows = cursor.fetchall()
            return [_row_to_event(r) for r in rows]

    async def get_latest_sequence(self, tenant_id: str) -> int:
        tenant_id = self._validate_tenant_id(tenant_id)

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(MAX(sequence), 0) as max_seq
                FROM audit_events
                WHERE tenant_id = ?
                """,
                (tenant_id,),
            )
            row = cursor.fetchone()
            return row["max_seq"] if row else 0

    async def verify_chain(self, tenant_id: str, start_sequence: Optional[int] = None, end_sequence: Optional[int] = None) -> bool:
        tenant_id = self._validate_tenant_id(tenant_id)

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()

            sql = "SELECT * FROM audit_events WHERE tenant_id = ?"
            params: List[Any] = [tenant_id]

            if start_sequence is not None:
                sql += " AND sequence >= ?"
                params.append(start_sequence)

            if end_sequence is not None:
                sql += " AND sequence <= ?"
                params.append(end_sequence)

            sql += " ORDER BY sequence ASC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            if not rows:
                return True

            for i, row in enumerate(rows):
                if i == 0:
                    if row["sequence"] == 1 and row["prev_checksum"] is not None:
                        return False
                    continue

                prev_row = rows[i - 1]
                if row["prev_checksum"] != prev_row["checksum"]:
                    return False

            return True

    async def export(self, tenant_id: str, start_sequence: Optional[int] = None, end_sequence: Optional[int] = None, include_checksum: bool = True) -> AuditExport:
        tenant_id = self._validate_tenant_id(tenant_id)

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()

            sql = "SELECT * FROM audit_events WHERE tenant_id = ?"
            params: List[Any] = [tenant_id]

            if start_sequence is not None:
                sql += " AND sequence >= ?"
                params.append(start_sequence)

            if end_sequence is not None:
                sql += " AND sequence <= ?"
                params.append(end_sequence)

            sql += " ORDER BY sequence ASC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            events = [_row_to_event(r) for r in rows]

            event_dicts: List[Dict[str, Any]] = []
            for e in events:
                if is_dataclass(e):
                    event_dicts.append(asdict(e))
                else:
                    event_dicts.append(dict(e))  # type: ignore

            export_checksum = ""
            if include_checksum and event_dicts:
                export_checksum = _compute_checksum({"tenant_id": tenant_id, "events": event_dicts})

            export_id = hashlib.sha256(f"{tenant_id}:{_now_iso_utc()}".encode()).hexdigest()[:16]
            exported_at = _now_iso_utc()

            first_seq = events[0].sequence if events and hasattr(events[0], "sequence") else 0
            last_seq = events[-1].sequence if events and hasattr(events[-1], "sequence") else 0

            data: Dict[str, Any] = {
                "tenant_id": tenant_id,
                "export_id": export_id,
                "event_count": len(events),
                "first_sequence": first_seq,
                "last_sequence": last_seq,
                "events": event_dicts,
                "checksum": export_checksum,
                "exported_at_utc": exported_at,
                "exported_at": exported_at,
                "timestamp_utc": exported_at,
                "timestamp": exported_at,
                "created_at": exported_at,
            }

            return _construct_dataclass(AuditExport, data)

    async def count(self, tenant_id: str, category: Optional[str] = None, severity: Optional[str] = None) -> int:
        tenant_id = self._validate_tenant_id(tenant_id)

        with self._get_connection(tenant_id) as conn:
            cursor = conn.cursor()

            sql = "SELECT COUNT(*) as cnt FROM audit_events WHERE tenant_id = ?"
            params: List[Any] = [tenant_id]

            if category:
                sql += " AND category = ?"
                params.append(category)

            if severity:
                sql += " AND severity = ?"
                params.append(severity)

            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row["cnt"] if row else 0

    def close(self) -> None:
        return

    def delete_tenant_data(self, tenant_id: str) -> bool:
        tenant_id = self._validate_tenant_id(tenant_id)
        db_path = self._get_db_path(tenant_id)
        if os.path.exists(db_path):
            os.remove(db_path)
            return True
        return False


_default_sqlite_ledger: Optional[SqliteAuditLedger] = None


def get_sqlite_audit_ledger(data_dir: str = DEFAULT_DATA_DIR) -> SqliteAuditLedger:
    global _default_sqlite_ledger
    if _default_sqlite_ledger is None:
        _default_sqlite_ledger = SqliteAuditLedger(data_dir)
    return _default_sqlite_ledger


def reset_sqlite_audit_ledger() -> None:
    global _default_sqlite_ledger
    _default_sqlite_ledger = None


__all__ = [
    "SqliteAuditLedger",
    "TenantRequiredError",
    "ChainIntegrityError",
    "DatabaseError",
    "get_sqlite_audit_ledger",
    "reset_sqlite_audit_ledger",
    "DEFAULT_DATA_DIR",
]
