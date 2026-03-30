from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from petcare.ai_closure.service import build_default_ai_closure_service


router = APIRouter(prefix="/api/ep05/ai-closure", tags=["ep05-ai-closure"])


class SealEpicRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    epic_id: str = Field(min_length=1)
    source_commit: str = Field(min_length=1)
    sealed_by: str = Field(min_length=1)


@router.post("/checklist/{tenant_id}/{epic_id}")
def generate_ep_closure_checklist(tenant_id: str, epic_id: str) -> dict:
    service = build_default_ai_closure_service()
    return asdict(service.generate_ep_closure_checklist(tenant_id=tenant_id, epic_id=epic_id))


@router.get("/checklist/{tenant_id}/{epic_id}")
def get_checklist(tenant_id: str, epic_id: str) -> dict:
    service = build_default_ai_closure_service()
    record = service.get_checklist(tenant_id, epic_id)
    if record is None:
        raise HTTPException(status_code=404, detail="ep_closure_checklist_not_found")
    return asdict(record)


@router.post("/seal")
def seal_epic(payload: SealEpicRequest) -> dict:
    service = build_default_ai_closure_service()
    try:
        return asdict(
            service.seal_epic(
                tenant_id=payload.tenant_id,
                epic_id=payload.epic_id,
                source_commit=payload.source_commit,
                sealed_by=payload.sealed_by,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/seals/{record_id}")
def get_seal(record_id: str) -> dict:
    service = build_default_ai_closure_service()
    record = service.get_seal(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="ep_governance_seal_not_found")
    return asdict(record)


@router.get("/seals")
def list_seals() -> dict:
    service = build_default_ai_closure_service()
    return {
        "records": [asdict(item) for item in service.list_seals()],
    }
