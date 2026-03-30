import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass(frozen=True)
class BackupResult:
    ok: bool
    out_db_path: Optional[str] = None
    reason: Optional[str] = None

def _wal_paths(db_path: str) -> Tuple[str, str]:
    return db_path + "-wal", db_path + "-shm"

def _safe_unlink(p: str) -> None:
    try:
        if os.path.exists(p):
            os.remove(p)
    except Exception:
        pass

def checkpoint_wal(db_path: str) -> Tuple[bool, str]:
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            conn.commit()
        finally:
            conn.close()
        return True, "ok"
    except Exception as e:
        return False, f"checkpoint_failed:{type(e).__name__}"

def ensure_no_wal_shm(db_path: str) -> None:
    wal, shm = _wal_paths(db_path)
    _safe_unlink(wal)
    _safe_unlink(shm)

def backup_sqlite_deterministic(
    db_path: str,
    out_dir: str,
    name_prefix: str = "backup",
    ts_utc: Optional[str] = None,
) -> BackupResult:
    if not os.path.exists(db_path):
        return BackupResult(ok=False, reason="db_missing")

    os.makedirs(out_dir, exist_ok=True)

    if ts_utc is None:
        ts_utc = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())

    out_db = os.path.join(out_dir, f"{name_prefix}_{ts_utc}.sqlite")
    tmp_db = out_db + ".tmp"

    ok, msg = checkpoint_wal(db_path)
    if not ok:
        return BackupResult(ok=False, reason=msg)

    ensure_no_wal_shm(db_path)

    try:
        src = sqlite3.connect(db_path, timeout=5)
        try:
            dst = sqlite3.connect(tmp_db, timeout=5)
            try:
                src.backup(dst)
                dst.commit()
            finally:
                dst.close()
        finally:
            src.close()
    except Exception as e:
        _safe_unlink(tmp_db)
        return BackupResult(ok=False, reason=f"backup_api_failed:{type(e).__name__}")

    os.replace(tmp_db, out_db)
    ensure_no_wal_shm(out_db)
    return BackupResult(ok=True, out_db_path=out_db, reason="ok")
