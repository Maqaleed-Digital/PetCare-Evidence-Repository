from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from FND.CODE_SCAFFOLD.interfaces.storage_interface import StorageInterface
from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id


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
        self._ensure_schema(conn)
        return conn

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
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
        conn.commit()

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
