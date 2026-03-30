from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id


def _utc_ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@dataclass(frozen=True)
class ExportBundle:
    tenant_id: str
    ts: str
    keys: List[str]
    records: int

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["keys"] = list(self.keys)
        return d


def build_export_bundle(tenant_id: str, keys: List[str], records: int) -> Dict[str, Any]:
    t = normalize_tenant_id(tenant_id)
    k = list(keys or [])
    k.sort()
    r = int(records)
    if r < 0:
        raise ValueError("records must be >= 0")
    b = ExportBundle(tenant_id=t, ts=_utc_ts_compact(), keys=k, records=r)
    return b.to_dict()
