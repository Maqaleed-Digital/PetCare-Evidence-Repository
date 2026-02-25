from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol


class StorageInterface(Protocol):
    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
        ...

    def get(self, tenant_id: str, key: str) -> Optional[Any]:
        ...

    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
        ...

    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
        ...

    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
        ...

    def export_items(self, tenant_id: str, prefix: str = "") -> List[Dict[str, Any]]:
        ...
