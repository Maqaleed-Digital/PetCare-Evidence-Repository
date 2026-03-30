from __future__ import annotations

from typing import Optional, Dict, Any

try:
    from fastapi import FastAPI, Header
    from fastapi.responses import JSONResponse
except Exception:
    FastAPI = None

from FND.CODE_SCAFFOLD.tenant_isolation_guard import TenantIsolationError, normalize_tenant_id
from FND.CODE_SCAFFOLD.storage.memory_store import MemoryStore


def create_app() -> Any:
    if FastAPI is None:
        return None

    app = FastAPI(title="PetCare Execution Scaffold")

    store = MemoryStore()

    @app.exception_handler(TenantIsolationError)
    async def _tenant_error_handler(_, exc: TenantIsolationError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.post("/api/platform-admin/storage/put")
    async def storage_put(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
        tenant_id = normalize_tenant_id(x_tenant_id)
        key = payload.get("key")
        value = payload.get("value")
        actor_id = payload.get("actor_id", "system")
        store.put(tenant_id=tenant_id, key=str(key), value=value, actor_id=str(actor_id))
        return {"ok": True}

    @app.post("/api/platform-admin/storage/get")
    async def storage_get(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
        tenant_id = normalize_tenant_id(x_tenant_id)
        key = payload.get("key")
        v = store.get(tenant_id=tenant_id, key=str(key))
        return {"value": v}

    @app.post("/api/platform-admin/storage/delete")
    async def storage_delete(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
        tenant_id = normalize_tenant_id(x_tenant_id)
        key = payload.get("key")
        actor_id = payload.get("actor_id", "system")
        existed = store.delete(tenant_id=tenant_id, key=str(key), actor_id=str(actor_id))
        return {"deleted": existed}

    @app.post("/api/platform-admin/storage/list")
    async def storage_list(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
        tenant_id = normalize_tenant_id(x_tenant_id)
        prefix = str(payload.get("prefix", ""))
        keys = store.list_keys(tenant_id=tenant_id, prefix=prefix)
        return {"keys": keys}

    return app
