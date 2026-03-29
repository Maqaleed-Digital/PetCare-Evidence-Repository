from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from petcare.ai_resolution.service import build_default_ai_resolution_service


router = APIRouter(prefix="/api/ep05/ai-resolution", tags=["ep05-ai-resolution"])


class BindApprovalResolutionRequest(BaseModel):
    artifact_type: str = Field(min_length=1)
    artifact_id: str = Field(min_length=1)
    resolved_by: str = Field(min_length=1)
    resolved_role: str = Field(min_length=1)
    resolution_action: str = Field(min_length=1)
    resolution_notes: Optional[str] = None


class BindClinicalSignoffRequest(BaseModel):
    artifact_id: str = Field(min_length=1)
    veterinarian_id: str = Field(min_length=1)
    veterinarian_role: str = Field(min_length=1)
    final_note_text: str = Field(min_length=1)


@router.post("/resolve")
def bind_approval_resolution(payload: BindApprovalResolutionRequest) -> dict:
    service = build_default_ai_resolution_service()
    try:
        record = service.bind_approval_resolution(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(record)


@router.get("/resolutions/{record_id}")
def get_resolution(record_id: str) -> dict:
    service = build_default_ai_resolution_service()
    record = service.get_resolution(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="approval_resolution_not_found")
    return asdict(record)


@router.get("/cases/{case_id}/resolutions")
def list_case_resolutions(case_id: str) -> dict:
    service = build_default_ai_resolution_service()
    return {
        "case_id": case_id,
        "records": [asdict(record) for record in service.list_case_resolutions(case_id)],
    }


@router.post("/signoff")
def bind_clinical_signoff(payload: BindClinicalSignoffRequest) -> dict:
    service = build_default_ai_resolution_service()
    try:
        record = service.bind_clinical_signoff(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(record)


@router.get("/signoffs/{record_id}")
def get_signoff(record_id: str) -> dict:
    service = build_default_ai_resolution_service()
    record = service.get_signoff(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="clinical_signoff_not_found")
    return asdict(record)


@router.get("/cases/{case_id}/signoffs")
def list_case_signoffs(case_id: str) -> dict:
    service = build_default_ai_resolution_service()
    return {
        "case_id": case_id,
        "records": [asdict(record) for record in service.list_case_signoffs(case_id)],
    }
