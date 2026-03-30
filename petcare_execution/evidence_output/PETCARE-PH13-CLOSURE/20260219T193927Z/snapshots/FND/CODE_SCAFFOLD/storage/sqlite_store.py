from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from FND.CODE_SCAFFOLD.interfaces.storage_interface import StorageInterface
from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id


SCHEMA_VERSION = 1


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _json_default(o: Any) -> Any:
    try:
        return str(o)
    except Exception:
        return "<unserializable>"


def _encode_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_json_default)


def _decode_value(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return s


def _require_key(key: str) -> str:
    k = (key or "").strip()
    if not k:
        raise ValueError("key is required")
    return k


class SqliteStore(StorageInterface):
    def __init__(self, base_dir: Optional[str] = None) -> None:
        root = Path(base_dir) if base_dir else Path(__file__).resolve().parents[3] / "data" / "tenants"
        self._base_dir = root.resolve()
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _db_path(self, tenant_id: str) -> Path:
        t = normalize_tenant_id(tenant_id)
        return (self._base_dir / f"{t}.sqlite").resolve()

    def _connect(self, tenant_id: str) -> sqlite3.Connection:
        db = self._db_path(tenant_id)
        db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        self._ensure_schema_and_migrate(conn)
        return conn

    def _ensure_schema_and_migrate(self, conn: sqlite3.Connection) -> None:
        self._ensure_meta_table(conn)
        current = self._read_schema_version(conn)
        target = int(SCHEMA_VERSION)

        migrations = self._migrations()
        for ver, fn in migrations:
            if int(ver) > current and int(ver) <= target:
                fn(conn)
                self._write_schema_version(conn, int(ver))
                self._set_meta(conn, "last_migrated_at_utc", _utc_iso())
                conn.commit()

        if current == 0:
            self._set_meta(conn, "created_at_utc", _utc_iso())
            self._set_meta(conn, "last_migrated_at_utc", _utc_iso())
            conn.commit()

        final = self._read_schema_version(conn)
        if final != target:
            raise RuntimeError(f"sqlite schema_version mismatch: have={final} want={target}")

    def _ensure_meta_table(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            """
        )
        conn.commit()

    def _get_meta(self, conn: sqlite3.Connection, key: str) -> Optional[str]:
        r = conn.execute("SELECT value FROM meta WHERE key=?;", (str(key),)).fetchone()
        if r is None:
            return None
        return str(r["value"])

    def _set_meta(self, conn: sqlite3.Connection, key: str, value: str) -> None:
        k = str(key)
        v = str(value)
        conn.execute(
            "INSERT INTO meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
            (k, v),
        )

    def _read_schema_version(self, conn: sqlite3.Connection) -> int:
        v = self._get_meta(conn, "schema_version")
        if v is None:
            return 0
        try:
            return int(v)
        except Exception:
            return 0

    def _write_schema_version(self, conn: sqlite3.Connection, version: int) -> None:
        self._set_meta(conn, "schema_version", str(int(version)))

    def _migrations(self) -> List[Tuple[int, Any]]:
        return [
            (1, self._migrate_v1),
        ]

    def _migrate_v1(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kv (
              key TEXT PRIMARY KEY,
              value_json TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts TEXT NOT NULL,
              action TEXT NOT NULL,
              key TEXT NOT NULL,
              actor_id TEXT NOT NULL,
              existed INTEGER
            );
            """
        )
        if self._get_meta(conn, "schema_version") is None:
            self._write_schema_version(conn, 1)

    def integrity_check(self, tenant_id: str) -> List[str]:
        t = normalize_tenant_id(tenant_id)
        with self._connect(t) as conn:
            rows = conn.execute("PRAGMA integrity_check;").fetchall()
            out: List[str] = []
            for r in rows:
                if len(r) >= 1:
                    out.append(str(r[0]))
            return out

    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
        t = normalize_tenant_id(tenant_id)
        k = _require_key(key)
        a = str(actor_id or "system")
        vj = _encode_value(value)

        with self._connect(t) as conn:
            conn.execute(
                "INSERT INTO kv(key,value_json) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json;",
                (k, vj),
            )
            conn.execute(
                "INSERT INTO audit(ts,action,key,actor_id,existed) VALUES(?,?,?,?,NULL);",
                (_utc_iso(), "put", k, a),
            )
            conn.commit()

    def get(self, tenant_id: str, key: str) -> Optional[Any]:
        t = normalize_tenant_id(tenant_id)
        k = _require_key(key)

        with self._connect(t) as conn:
            row = conn.execute("SELECT value_json FROM kv WHERE key=?;", (k,)).fetchone()
            if row is None:
                return None
            return _decode_value(str(row["value_json"]))

    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
        t = normalize_tenant_id(tenant_id)
        k = _require_key(key)
        a = str(actor_id or "system")

        with self._connect(t) as conn:
            row = conn.execute("SELECT 1 FROM kv WHERE key=?;", (k,)).fetchone()
            existed = row is not None
            if existed:
                conn.execute("DELETE FROM kv WHERE key=?;", (k,))
            conn.execute(
                "INSERT INTO audit(ts,action,key,actor_id,existed) VALUES(?,?,?,?,?);",
                (_utc_iso(), "delete", k, a, 1 if existed else 0),
            )
            conn.commit()
            return existed

    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
        t = normalize_tenant_id(tenant_id)
        p = str(prefix or "")

        with self._connect(t) as conn:
            if p:
                rows = conn.execute("SELECT key FROM kv WHERE key LIKE ? ORDER BY key;", (f"{p}%",)).fetchall()
            else:
                rows = conn.execute("SELECT key FROM kv ORDER BY key;").fetchall()
            return [str(r["key"]) for r in rows]

    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
        t = normalize_tenant_id(tenant_id)

        with self._connect(t) as conn:
            rows = conn.execute("SELECT ts,action,key,actor_id,existed FROM audit ORDER BY id;").fetchall()

            out: List[Dict[str, Any]] = []
            for r in rows:
                d: Dict[str, Any] = {
                    "ts": str(r["ts"]),
                    "action": str(r["action"]),
                    "key": str(r["key"]),
                    "actor_id": str(r["actor_id"]),
                }
                if r["existed"] is not None:
                    d["existed"] = bool(int(r["existed"]))
                out.append(d)
            return out

    def export_items(self, tenant_id: str, prefix: str = "") -> List[Dict[str, Any]]:
        t = normalize_tenant_id(tenant_id)
        p = str(prefix or "")

        with self._connect(t) as conn:
            if p:
                rows = conn.execute(
                    "SELECT key,value_json FROM kv WHERE key LIKE ? ORDER BY key;",
                    (f"{p}%",),
                ).fetchall()
            else:
                rows = conn.execute("SELECT key,value_json FROM kv ORDER BY key;").fetchall()

            items: List[Dict[str, Any]] = []
            for r in rows:
                items.append({"key": str(r["key"]), "value": _decode_value(str(r["value_json"]))})
            return items

def _pc__sqlite_store_base_dir(self) -> str:
    try:
        return str(self._base_dir)
    except Exception:
        return str(getattr(self, "_base_dir", ""))


def _pc__backup_tenant_db(self, tenant_id: str, out_dir: str) -> Dict[str, Any]:
    from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import backup_tenant_db as _backup
    return _backup(tenant_id=tenant_id, out_dir=out_dir, base_dir=_pc__sqlite_store_base_dir(self))


def _pc__restore_tenant_db(self, tenant_id: str, backup_path: str) -> Dict[str, Any]:
    from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import restore_tenant_db as _restore
    return _restore(tenant_id=tenant_id, backup_path=backup_path, base_dir=_pc__sqlite_store_base_dir(self))


def _pc__integrity_check(self, tenant_id: str) -> Dict[str, Any]:
    from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import integrity_check as _check
    return _check(tenant_id=tenant_id, base_dir=_pc__sqlite_store_base_dir(self))


SqliteStore.backup_tenant_db = _pc__backup_tenant_db  # type: ignore[attr-defined]
SqliteStore.restore_tenant_db = _pc__restore_tenant_db  # type: ignore[attr-defined]
SqliteStore.integrity_check = _pc__integrity_check  # type: ignore[attr-defined]

def _pc__sqlite_store_base_dir(self) -> str:
    try:
        return str(self._base_dir)
    except Exception:
        return str(getattr(self, "_base_dir", ""))


def _pc__backup_tenant_db(self, tenant_id: str, out_dir: Optional[str] = None, backup_path: Optional[str] = None, **_: Any) -> Dict[str, Any]:
    from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import backup_tenant_db as _backup
    target_out = out_dir if out_dir is not None else backup_path
    if target_out is None:
        raise TypeError("backup_tenant_db requires out_dir or backup_path")
    return _backup(tenant_id=tenant_id, out_dir=str(target_out), base_dir=_pc__sqlite_store_base_dir(self))


def _pc__restore_tenant_db(self, tenant_id: str, backup_path: Optional[str] = None, in_path: Optional[str] = None, **_: Any) -> Dict[str, Any]:
    from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import restore_tenant_db as _restore
    src = backup_path if backup_path is not None else in_path
    if src is None:
        raise TypeError("restore_tenant_db requires backup_path or in_path")
    return _restore(tenant_id=tenant_id, backup_path=str(src), base_dir=_pc__sqlite_store_base_dir(self))


def _pc__integrity_check(self, tenant_id: str, **_: Any) -> Dict[str, Any]:
    from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import integrity_check as _check
    return _check(tenant_id=tenant_id, base_dir=_pc__sqlite_store_base_dir(self))


SqliteStore.backup_tenant_db = _pc__backup_tenant_db  # type: ignore[attr-defined]
SqliteStore.restore_tenant_db = _pc__restore_tenant_db  # type: ignore[attr-defined]
SqliteStore.integrity_check = _pc__integrity_check  # type: ignore[attr-defined]

def _pc__restore_tenant_db(self, tenant_id: str, backup_path: Optional[Any] = None, in_path: Optional[Any] = None, **_: Any) -> Dict[str, Any]:
    from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import restore_tenant_db as _restore

    src = backup_path if backup_path is not None else in_path
    if src is None:
        raise TypeError("restore_tenant_db requires backup_path or in_path")

    if isinstance(src, dict):
        bp = src.get("backup_path")
        if not bp:
            raise TypeError("restore_tenant_db got dict but missing backup_path")
        src = bp

    return _restore(tenant_id=tenant_id, backup_path=str(src), base_dir=_pc__sqlite_store_base_dir(self))


SqliteStore.restore_tenant_db = _pc__restore_tenant_db  # type: ignore[attr-defined]

def _pc__meta_db_path(self, tenant_id: str):
    from pathlib import Path
    from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id

    base = _pc__sqlite_store_base_dir(self)
    t = normalize_tenant_id(tenant_id)
    return (Path(base) / f"{t}.sqlite").resolve()


def _pc__get_meta(self, tenant_id: str, key: str):
    import sqlite3

    db = _pc__meta_db_path(self, tenant_id)
    db.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db))
    try:
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            """
        )
        row = conn.execute("SELECT value FROM meta WHERE key=?;", (str(key),)).fetchone()
        if row is None:
            return None
        return str(row["value"])
    finally:
        conn.close()


def _pc__set_meta(self, tenant_id: str, key: str, value: str):
    import sqlite3

    db = _pc__meta_db_path(self, tenant_id)
    db.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db))
    try:
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "INSERT INTO meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
            (str(key), str(value)),
        )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


SqliteStore.get_meta = _pc__get_meta  # type: ignore[attr-defined]
SqliteStore.set_meta = _pc__set_meta  # type: ignore[attr-defined]
