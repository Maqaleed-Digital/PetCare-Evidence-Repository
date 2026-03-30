from __future__ import annotations

import hashlib
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id


def _utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tenant_db_path(tenant_id: str, base_dir: Optional[str] = None) -> Path:
    t = normalize_tenant_id(tenant_id)
    root = Path(base_dir) if base_dir else Path(__file__).resolve().parents[3] / "data" / "tenants"
    return (root.resolve() / f"{t}.sqlite").resolve()


def integrity_check(tenant_id: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    db = tenant_db_path(tenant_id, base_dir=base_dir)
    if not db.exists():
        raise FileNotFoundError(str(db))

    conn = sqlite3.connect(str(db))
    try:
        rows = conn.execute("PRAGMA integrity_check;").fetchall()
        results: List[str] = []
        for r in rows:
            if len(r) >= 1:
                results.append(str(r[0]))
    finally:
        conn.close()

    st = db.stat()
    return {
        "tenant_id": normalize_tenant_id(tenant_id),
        "db_path": str(db),
        "bytes": int(st.st_size),
        "sha256": sha256_file(db),
        "results": results,
    }


def backup_tenant_db(tenant_id: str, out_dir: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    db = tenant_db_path(tenant_id, base_dir=base_dir)
    if not db.exists():
        raise FileNotFoundError(str(db))

    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    backup_name = f"{normalize_tenant_id(tenant_id)}_{_utc_compact()}.sqlite"
    backup_path = (out / backup_name).resolve()

    shutil.copy2(str(db), str(backup_path))

    st = backup_path.stat()
    return {
        "tenant_id": normalize_tenant_id(tenant_id),
        "source_db": str(db),
        "backup_path": str(backup_path),
        "bytes": int(st.st_size),
        "sha256": sha256_file(backup_path),
    }


def restore_tenant_db(tenant_id: str, backup_path: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    t = normalize_tenant_id(tenant_id)
    src = Path(backup_path).resolve()
    if not src.exists():
        raise FileNotFoundError(str(src))

    dst = tenant_db_path(t, base_dir=base_dir)
    dst.parent.mkdir(parents=True, exist_ok=True)

    tmp = dst.with_suffix(".sqlite.tmp")
    if tmp.exists():
        tmp.unlink()

    shutil.copy2(str(src), str(tmp))
    tmp.replace(dst)

    st = dst.stat()
    return {
        "tenant_id": t,
        "restored_from": str(src),
        "db_path": str(dst),
        "bytes": int(st.st_size),
        "sha256": sha256_file(dst),
    }


def purge_tenant_db(tenant_id: str, base_dir: Optional[str] = None, quarantine_dir: Optional[str] = None) -> Dict[str, Any]:
    t = normalize_tenant_id(tenant_id)
    db = tenant_db_path(t, base_dir=base_dir)

    existed = db.exists()
    if not existed:
        return {
            "tenant_id": t,
            "db_path": str(db),
            "existed": False,
            "purged": False,
        }

    before = {"bytes": int(db.stat().st_size), "sha256": sha256_file(db)}

    if quarantine_dir:
        q = Path(quarantine_dir).resolve()
        q.mkdir(parents=True, exist_ok=True)
        moved = (q / f"{t}_{_utc_compact()}.sqlite").resolve()
        db.replace(moved)
        return {
            "tenant_id": t,
            "db_path": str(db),
            "existed": True,
            "purged": True,
            "mode": "quarantine_move",
            "before": before,
            "quarantine_path": str(moved),
            "quarantine_sha256": sha256_file(moved),
            "quarantine_bytes": int(moved.stat().st_size),
        }

    db.unlink()
    return {
        "tenant_id": t,
        "db_path": str(db),
        "existed": True,
        "purged": True,
        "mode": "delete",
        "before": before,
    }
