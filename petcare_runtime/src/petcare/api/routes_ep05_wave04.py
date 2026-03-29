from __future__ import annotations

from dataclasses import asdict
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from petcare.ai_runtime.service import build_default_ai_runtime_service


router = APIRouter(prefix="/api/ep05/ai-runtime", tags=["ep05-ai-runtime"])


class CreateAIIntakeRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    pet_id: Optional[str] = None
    actor_id: str = Field(min_length=1)
    actor_role: str = Field(min_length=1)
    species: str = Field(min_length=1)
    symptom_summary: str = Field(min_length=1)
    urgency_level: str = Field(min_length=1)
    red_flags: List[str] = Field(default_factory=list)
    structured_questions: List[str] = Field(default_factory=list)


class CreateVetCopilotDraftRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    pet_id: Optional[str] = None
    actor_id: str = Field(min_length=1)
    actor_role: str = Field(min_length=1)
    soap_subjective: str = Field(min_length=1)
    soap_objective: str = Field(min_length=1)
    soap_assessment: str = Field(min_length=1)
    soap_plan: str = Field(min_length=1)
    protocol_citations: List[str] = Field(default_factory=list)
    uncertainty_note: str = Field(min_length=1)


@router.post("/intake")
def create_ai_intake(payload: CreateAIIntakeRequest) -> dict:
    service = build_default_ai_runtime_service()
    record = service.create_ai_intake(**payload.model_dump())
    return asdict(record)


@router.get("/intake/{record_id}")
def get_ai_intake(record_id: str) -> dict:
    service = build_default_ai_runtime_service()
    record = service.get_intake(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="ai_intake_not_found")
    return asdict(record)


@router.get("/cases/{case_id}/intake")
def list_case_intake(case_id: str) -> dict:
    service = build_default_ai_runtime_service()
    return {
        "case_id": case_id,
        "records": [asdict(record) for record in service.list_case_intake(case_id)],
    }


@router.post("/vet-copilot")
def create_vet_copilot_draft(payload: CreateVetCopilotDraftRequest) -> dict:
    service = build_default_ai_runtime_service()
    record = service.create_vet_copilot_draft(**payload.model_dump())
    return asdict(record)


@router.get("/vet-copilot/{record_id}")
def get_vet_copilot_draft(record_id: str) -> dict:
    service = build_default_ai_runtime_service()
    record = service.get_vet_copilot_draft(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="vet_copilot_draft_not_found")
    return asdict(record)


@router.get("/cases/{case_id}/vet-copilot")
def list_case_vet_copilot_drafts(case_id: str) -> dict:
    service = build_default_ai_runtime_service()
    return {
        "case_id": case_id,
        "records": [asdict(record) for record in service.list_case_vet_copilot_drafts(case_id)],
    }
