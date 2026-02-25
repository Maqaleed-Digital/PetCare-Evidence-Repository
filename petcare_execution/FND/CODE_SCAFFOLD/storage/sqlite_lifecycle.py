from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def normalize_tenant_id(tenant_id: str) -> str:
    s = str(tenant_id).strip()
    if not s:
        raise ValueError("tenant_id required")
    return s


def _resolve_base_dir(base_dir: Optional[str]) -> Path:
    if base_dir is None:
        base = (Path.cwd().resolve() / "data" / "tenants")
    else:
        base = Path(base_dir).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def _tenant_db_path(tenant_id: str, base_dir: Optional[str]) -> Path:
    base = _resolve_base_dir(base_dir)
    return (base / f"{normalize_tenant_id(tenant_id)}.sqlite").resolve()


def _wal_paths(db_path: Path) -> Tuple[Path, Path]:
    return Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")


def _safe_unlink(p: Path) -> None:
    try:
        if p.exists():
            p.unlink()
    except Exception:
        pass


def _checkpoint_wal(db_path: Path) -> Tuple[bool, str]:
    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            conn.commit()
        finally:
            conn.close()
        return True, "ok"
    except Exception as e:
        return False, f"checkpoint_failed:{type(e).__name__}"


def _ensure_clean_sidecars(db_path: Path) -> None:
    wal, shm = _wal_paths(db_path)
    _safe_unlink(wal)
    _safe_unlink(shm)


def integrity_check(tenant_id: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    db = _tenant_db_path(tenant_id, base_dir)
    if not db.exists():
        return {
            "tenant_id": normalize_tenant_id(tenant_id),
            "db_path": str(db),
            "results": ["missing_db"],
            "checked_at_utc": _utc_iso(),
        }

    try:
        conn = sqlite3.connect(str(db), timeout=5)
        try:
            r = conn.execute("PRAGMA integrity_check;").fetchone()
            msg = "ok" if r and str(r[0]).lower() == "ok" else (str(r[0]) if r else "unknown")
        finally:
            conn.close()
        return {
            "tenant_id": normalize_tenant_id(tenant_id),
            "db_path": str(db),
            "results": [msg],
            "checked_at_utc": _utc_iso(),
        }
    except Exception as e:
        return {
            "tenant_id": normalize_tenant_id(tenant_id),
            "db_path": str(db),
            "results": [f"error:{type(e).__name__}"],
            "checked_at_utc": _utc_iso(),
        }


def backup_tenant_db(tenant_id: str, out_dir: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    tid = normalize_tenant_id(tenant_id)
    src_db = _tenant_db_path(tid, base_dir)
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    backup_path = (out / f"{tid}.sqlite.backup").resolve()
    tmp_path = Path(str(backup_path) + ".tmp").resolve()

    if not src_db.exists():
        raise FileNotFoundError(f"tenant db not found: {src_db}")

    ok, msg = _checkpoint_wal(src_db)
    if not ok:
        raise RuntimeError(msg)

    _ensure_clean_sidecars(src_db)

    try:
        src_conn = sqlite3.connect(str(src_db), timeout=5)
        try:
            dst_conn = sqlite3.connect(str(tmp_path), timeout=5)
            try:
                src_conn.backup(dst_conn)
                dst_conn.commit()
            finally:
                dst_conn.close()
        finally:
            src_conn.close()
    except Exception:
        _safe_unlink(tmp_path)
        raise

    os.replace(str(tmp_path), str(backup_path))

    _ensure_clean_sidecars(backup_path)

    return {
        "tenant_id": tid,
        "db_path": str(src_db),
        "backup_path": str(backup_path),
        "backed_up_at_utc": _utc_iso(),
    }


def restore_tenant_db(tenant_id: str, backup_path: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    tid = normalize_tenant_id(tenant_id)
    src = Path(backup_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"backup not found: {src}")

    dst_db = _tenant_db_path(tid, base_dir)

    _ensure_clean_sidecars(dst_db)

    tmp = Path(str(dst_db) + ".restore.tmp").resolve()
    _safe_unlink(tmp)

    try:
        src_conn = sqlite3.connect(str(src), timeout=5)
        try:
            dst_conn = sqlite3.connect(str(tmp), timeout=5)
            try:
                src_conn.backup(dst_conn)
                dst_conn.commit()
            finally:
                dst_conn.close()
        finally:
            src_conn.close()
    except Exception:
        _safe_unlink(tmp)
        raise

    os.replace(str(tmp), str(dst_db))

    _ensure_clean_sidecars(dst_db)

    ok, _ = _checkpoint_wal(dst_db)
    if ok:
        _ensure_clean_sidecars(dst_db)

    return {
        "tenant_id": tid,
        "db_path": str(dst_db),
        "restored_from": str(src),
        "restored_at_utc": _utc_iso(),
    }


@dataclass(frozen=True)
class LifecycleConfig:
    base_dir: Optional[str] = None


class SqliteLifecycle:
    def __init__(self, config: Optional[LifecycleConfig] = None) -> None:
        self.config = config or LifecycleConfig()

    def tenant_db_path(self, tenant_id: str) -> str:
        return str(_tenant_db_path(tenant_id, self.config.base_dir))

    def integrity_check(self, tenant_id: str) -> Dict[str, Any]:
        return integrity_check(tenant_id=tenant_id, base_dir=self.config.base_dir)

    def backup_tenant_db(self, tenant_id: str, out_dir: str) -> Dict[str, Any]:
        return backup_tenant_db(tenant_id=tenant_id, out_dir=out_dir, base_dir=self.config.base_dir)

    def restore_tenant_db(self, tenant_id: str, backup_path: str) -> Dict[str, Any]:
        return restore_tenant_db(tenant_id=tenant_id, backup_path=backup_path, base_dir=self.config.base_dir)
