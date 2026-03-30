from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from FND.CODE_SCAFFOLD.interfaces.storage_interface import StorageInterface
from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class MemoryStore(StorageInterface):
    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._audit: Dict[str, List[Dict[str, Any]]] = {}

    def _require_tenant(self, tenant_id: str) -> str:
        return normalize_tenant_id(tenant_id)

    def _require_key(self, key: str) -> str:
        k = (key or "").strip()
        if not k:
            raise ValueError("key is required")
        return k

    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
        t = self._require_tenant(tenant_id)
        k = self._require_key(key)
        self._data.setdefault(t, {})[k] = value
        self._audit.setdefault(t, []).append({"ts": _utc_iso(), "action": "put", "key": k, "actor_id": actor_id})

    def get(self, tenant_id: str, key: str) -> Optional[Any]:
        t = self._require_tenant(tenant_id)
        k = self._require_key(key)
        return self._data.get(t, {}).get(k)

    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
        t = self._require_tenant(tenant_id)
        k = self._require_key(key)
        existed = k in self._data.get(t, {})
        if existed:
            del self._data[t][k]
        self._audit.setdefault(t, []).append(
            {"ts": _utc_iso(), "action": "delete", "key": k, "actor_id": actor_id, "existed": existed}
        )
        return existed

    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
        t = self._require_tenant(tenant_id)
        p = prefix or ""
        keys = list(self._data.get(t, {}).keys())
        keys.sort()
        if not p:
            return keys
        return [k for k in keys if k.startswith(p)]

    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
        t = self._require_tenant(tenant_id)
        return list(self._audit.get(t, []))

    def export_items(self, tenant_id: str, prefix: str = "") -> List[Dict[str, Any]]:
        t = self._require_tenant(tenant_id)
        p = prefix or ""
        items: List[Dict[str, Any]] = []
        data = self._data.get(t, {})
        for k in sorted(data.keys()):
            if p and not k.startswith(p):
                continue
            items.append({"key": k, "value": data[k]})
        return items
