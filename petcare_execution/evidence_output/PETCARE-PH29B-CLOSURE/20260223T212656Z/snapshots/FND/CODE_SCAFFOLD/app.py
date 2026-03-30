from __future__ import annotations

import os
from typing import Optional, Dict, Any

from fastapi import FastAPI, Header, Depends, Request, HTTPException
from fastapi.responses import JSONResponse

from FND.CODE_SCAFFOLD.tenant_isolation_guard import (
    TenantIsolationError,
    TenantContext,
    TENANT_HEADER,
    require_tenant_context,
)

from FND.CODE_SCAFFOLD.storage.memory_store import MemoryStore
from FND.CODE_SCAFFOLD.storage.sqlite_store import SqliteStore
from FND.CODE_SCAFFOLD.storage.export_bundle import build_export_bundle

from FND.security.policy_guard import load_policy, evaluate_with_policy, enforce_evidence_export
from FND.security.actor_id import validate_actor_id


def _tenant_ctx_dependency(x_tenant_id: Optional[str] = Header(default=None, alias=TENANT_HEADER)) -> TenantContext:
    return require_tenant_context(x_tenant_id)


def _select_store():
    backend = (os.environ.get("PETCARE_STORE_BACKEND", "memory") or "memory").strip().lower()
    if backend == "sqlite":
        return SqliteStore()
    return MemoryStore()


def _auth_actor_dependency(request: Request) -> str:
    headers = {k: v for k, v in request.headers.items()}
    policy = load_policy()
    decision = evaluate_with_policy(headers=headers, policy=policy)

    if not decision.ok:
        raise HTTPException(status_code=int(decision.status_code), detail=str(decision.reason))

    actor = decision.actor_id or ""
    r = validate_actor_id(actor)
    if not bool(r.ok):
        raise HTTPException(status_code=400, detail=f"invalid_actor_id:{r.reason}")

    return actor


def create_app() -> FastAPI:
    app = FastAPI(title="PetCare Execution Scaffold")

    store = _select_store()

    @app.exception_handler(TenantIsolationError)
    async def _tenant_error_handler(_, exc: TenantIsolationError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.post("/api/platform-admin/storage/put")
    async def storage_put(
        payload: Dict[str, Any],
        ctx: TenantContext = Depends(_tenant_ctx_dependency),
        actor_header: str = Depends(_auth_actor_dependency),
    ):
        key = payload.get("key")
        value = payload.get("value")
        actor_id = str(payload.get("actor_id", actor_header))

        r = validate_actor_id(actor_id)
        if not bool(r.ok):
            raise HTTPException(status_code=400, detail=f"invalid_actor_id:{r.reason}")

        if actor_id != actor_header:
            raise HTTPException(status_code=403, detail="actor_mismatch")

        store.put(tenant_id=ctx.tenant_id, key=str(key), value=value, actor_id=str(actor_id))
        return {"ok": True}

    @app.post("/api/platform-admin/storage/get")
    async def storage_get(
        payload: Dict[str, Any],
        ctx: TenantContext = Depends(_tenant_ctx_dependency),
        _: str = Depends(_auth_actor_dependency),
    ):
        key = payload.get("key")
        v = store.get(tenant_id=ctx.tenant_id, key=str(key))
        return {"value": v}

    @app.post("/api/platform-admin/storage/delete")
    async def storage_delete(
        payload: Dict[str, Any],
        ctx: TenantContext = Depends(_tenant_ctx_dependency),
        actor_header: str = Depends(_auth_actor_dependency),
    ):
        key = payload.get("key")
        actor_id = str(payload.get("actor_id", actor_header))

        r = validate_actor_id(actor_id)
        if not bool(r.ok):
            raise HTTPException(status_code=400, detail=f"invalid_actor_id:{r.reason}")

        if actor_id != actor_header:
            raise HTTPException(status_code=403, detail="actor_mismatch")

        existed = store.delete(tenant_id=ctx.tenant_id, key=str(key), actor_id=str(actor_id))
        return {"deleted": existed}

    @app.post("/api/platform-admin/storage/list")
    async def storage_list(
        payload: Dict[str, Any],
        ctx: TenantContext = Depends(_tenant_ctx_dependency),
        _: str = Depends(_auth_actor_dependency),
    ):
        prefix = str(payload.get("prefix", ""))
        keys = store.list_keys(tenant_id=ctx.tenant_id, prefix=prefix)
        return {"keys": keys}

    @app.post("/api/platform-admin/storage/export")
    async def storage_export(
        payload: Dict[str, Any],
        ctx: TenantContext = Depends(_tenant_ctx_dependency),
        request: Request = None,
        _: str = Depends(_auth_actor_dependency),
    ):
        prefix = str(payload.get("prefix", ""))

        include_pii = bool(payload.get("include_pii", False))
        watermark = bool(payload.get("watermark", False))
        encryption = bool(payload.get("encryption", False))

        policy = load_policy()
        ok, reason, code = enforce_evidence_export(
            policy=policy,
            include_pii=include_pii,
            watermark=watermark,
            encryption=encryption,
        )
        if not ok:
            raise HTTPException(status_code=int(code), detail=str(reason))

        items = store.export_items(tenant_id=ctx.tenant_id, prefix=prefix)
        audit = store.audit_log(tenant_id=ctx.tenant_id)
        bundle = build_export_bundle(tenant_id=ctx.tenant_id, items=items, audit=audit)
        bundle["export_policy"] = {
            "include_pii": include_pii,
            "watermark": watermark,
            "encryption": encryption,
        }
        return bundle

    # BEGIN_PETCARE_PH29B_AUDIT_VERIFY_ROUTES
    try:
        from FND.CODE_SCAFFOLD.api.routes_audit_verify import register_audit_verify_routes

        register_audit_verify_routes(app)
    except Exception:
        pass
    # END_PETCARE_PH29B_AUDIT_VERIFY_ROUTES

    return app


app = create_app()


from typing import Dict as _Dict, Any as _Any

def health_check() -> _Dict[str, _Any]:
    return {"status": "ok"}
