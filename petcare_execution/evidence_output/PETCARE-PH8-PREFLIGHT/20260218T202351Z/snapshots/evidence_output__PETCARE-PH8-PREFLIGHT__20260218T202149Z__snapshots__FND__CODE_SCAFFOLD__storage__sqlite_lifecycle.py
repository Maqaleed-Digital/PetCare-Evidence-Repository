from __future__ import annotations

import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id


SCHEMA_VERSION = 1


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class LifecycleConfig:
    base_dir: Optional[str] = None


def _default_base_dir(base_dir: Optional[str]) -> Path:
    if base_dir:
        p = Path(base_dir)
    else:
        p = Path(__file__).resolve().parents[3] / "data" / "tenants"
    p = p.resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def tenant_db_path(tenant_id: str, base_dir: Optional[str] = None) -> Path:
    t = normalize_tenant_id(tenant_id)
    root = _default_base_dir(base_dir)
    return (root / f"{t}.sqlite").resolve()


class SqliteLifecycle:
    def __init__(self, config: Optional[LifecycleConfig] = None) -> None:
        cfg = config or LifecycleConfig()
        self._config = cfg
        self._base_dir = _default_base_dir(cfg.base_dir)

    @property
    def config(self) -> LifecycleConfig:
        return self._config

    def db_path(self, tenant_id: str) -> Path:
        return tenant_db_path(tenant_id, self._config.base_dir)

    def connect_path(self, db_path: Path) -> sqlite3.Connection:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        self.ensure_schema_and_migrate(conn)
        return conn

    def connect(self, tenant_id: str) -> sqlite3.Connection:
        return self.connect_path(self.db_path(tenant_id))

    def ensure_schema_and_migrate(self, conn: sqlite3.Connection) -> None:
        self._ensure_meta_table(conn)
        current = self._read_schema_version(conn)
        target = int(SCHEMA_VERSION)

        if current == 0:
            self._migrate_v1(conn)
            self._write_schema_version(conn, 1)
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


def integrity_check(tenant_id: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    db = tenant_db_path(tenant_id, base_dir)
    lc = SqliteLifecycle(LifecycleConfig(base_dir=base_dir))

    if not db.exists():
        return {
            "tenant_id": normalize_tenant_id(tenant_id),
            "db_path": str(db),
            "checked_at_utc": _utc_iso(),
            "results": ["ok"],
        }

    with lc.connect_path(db) as conn:
        rows = conn.execute("PRAGMA integrity_check;").fetchall()
        results: List[str] = []
        for r in rows:
            if len(r) >= 1:
                results.append(str(r[0]))
        if not results:
            results = ["ok"]

        return {
            "tenant_id": normalize_tenant_id(tenant_id),
            "db_path": str(db),
            "checked_at_utc": _utc_iso(),
            "results": results,
        }


def backup_tenant_db(tenant_id: str, out_dir: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    backup_path = (out / f"{normalize_tenant_id(tenant_id)}.sqlite.backup").resolve()
    src = tenant_db_path(tenant_id, base_dir)

    if not src.exists():
        sqlite3.connect(str(backup_path)).close()
    else:
        src_conn = sqlite3.connect(str(src))
        try:
            dst_conn = sqlite3.connect(str(backup_path))
            try:
                src_conn.backup(dst_conn)
                dst_conn.commit()
            finally:
                dst_conn.close()
        finally:
            src_conn.close()

    return {
        "tenant_id": normalize_tenant_id(tenant_id),
        "db_path": str(src),
        "backup_path": str(backup_path),
        "backed_up_at_utc": _utc_iso(),
    }


def restore_tenant_db(tenant_id: str, backup_path: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    src = Path(backup_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"backup not found: {src}")

    dst = tenant_db_path(tenant_id, base_dir)
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        try:
            os.remove(str(dst))
        except Exception:
            pass

    shutil.copyfile(str(src), str(dst))

    lc = SqliteLifecycle(LifecycleConfig(base_dir=base_dir))
    with lc.connect_path(dst) as conn:
        lc.ensure_schema_and_migrate(conn)
        conn.commit()

    return {
        "tenant_id": normalize_tenant_id(tenant_id),
        "db_path": str(dst),
        "restored_from": str(src),
        "restored_at_utc": _utc_iso(),
    }
