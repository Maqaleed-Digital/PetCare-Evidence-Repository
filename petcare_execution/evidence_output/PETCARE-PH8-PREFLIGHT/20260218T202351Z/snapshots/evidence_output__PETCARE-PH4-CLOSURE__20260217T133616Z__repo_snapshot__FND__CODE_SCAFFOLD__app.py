from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import FastAPI, Header, Depends
from fastapi.responses import JSONResponse

from FND.CODE_SCAFFOLD.tenant_isolation_guard import (
    TenantIsolationError,
    TenantContext,
    TENANT_HEADER,
    require_tenant_context,
)
from FND.CODE_SCAFFOLD.storage.memory_store import MemoryStore
from FND.CODE_SCAFFOLD.storage.export_bundle import build_export_bundle


def _tenant_ctx_dependency(x_tenant_id: Optional[str] = Header(default=None, alias=TENANT_HEADER)) -> TenantContext:
    return require_tenant_context(x_tenant_id)


def create_app() -> FastAPI:
    app = FastAPI(title="PetCare Execution Scaffold")

    store = MemoryStore()

    @app.exception_handler(TenantIsolationError)
    async def _tenant_error_handler(_, exc: TenantIsolationError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.post("/api/platform-admin/storage/put")
    async def storage_put(payload: Dict[str, Any], ctx: TenantContext = Depends(_tenant_ctx_dependency)):
        key = payload.get("key")
        value = payload.get("value")
        actor_id = payload.get("actor_id", "system")
        store.put(tenant_id=ctx.tenant_id, key=str(key), value=value, actor_id=str(actor_id))
        return {"ok": True}

    @app.post("/api/platform-admin/storage/get")
    async def storage_get(payload: Dict[str, Any], ctx: TenantContext = Depends(_tenant_ctx_dependency)):
        key = payload.get("key")
        v = store.get(tenant_id=ctx.tenant_id, key=str(key))
        return {"value": v}

    @app.post("/api/platform-admin/storage/delete")
    async def storage_delete(payload: Dict[str, Any], ctx: TenantContext = Depends(_tenant_ctx_dependency)):
        key = payload.get("key")
        actor_id = payload.get("actor_id", "system")
        existed = store.delete(tenant_id=ctx.tenant_id, key=str(key), actor_id=str(actor_id))
        return {"deleted": existed}

    @app.post("/api/platform-admin/storage/list")
    async def storage_list(payload: Dict[str, Any], ctx: TenantContext = Depends(_tenant_ctx_dependency)):
        prefix = str(payload.get("prefix", ""))
        keys = store.list_keys(tenant_id=ctx.tenant_id, prefix=prefix)
        return {"keys": keys}

    @app.post("/api/platform-admin/storage/export")
    async def storage_export(payload: Dict[str, Any], ctx: TenantContext = Depends(_tenant_ctx_dependency)):
        prefix = str(payload.get("prefix", ""))
        items = store.export_items(tenant_id=ctx.tenant_id, prefix=prefix)
        audit = store.audit_log(tenant_id=ctx.tenant_id)
        bundle = build_export_bundle(tenant_id=ctx.tenant_id, items=items, audit=audit)
        return bundle

    return app


app = create_app()
