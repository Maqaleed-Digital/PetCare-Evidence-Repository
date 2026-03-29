from __future__ import annotations

from dataclasses import asdict
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from petcare.ai_logging.service import build_default_trace_service


router = APIRouter(prefix="/api/ep05/ai-logging", tags=["ep05-ai-logging"])
service = build_default_trace_service()


class RegisterModelRequest(BaseModel):
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    status: str = Field(min_length=1)
    safety_level: str = Field(min_length=1)


class LogPromptRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    actor_role: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    pet_id: Optional[str] = None
    prompt_text: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    context_type: str = Field(min_length=1)


class LogOutputRequest(BaseModel):
    prompt_id: str = Field(min_length=1)
    output_text: str = Field(min_length=1)
    confidence: Optional[float] = None
    risk_flags: List[str] = Field(default_factory=list)
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None


@router.post("/models")
def register_model(payload: RegisterModelRequest) -> dict:
    record = service.register_model(**payload.model_dump())
    return asdict(record)


@router.get("/models")
def list_models() -> list[dict]:
    return [asdict(record) for record in service.list_models()]


@router.post("/prompts")
def log_prompt(payload: LogPromptRequest) -> dict:
    record = service.log_prompt(**payload.model_dump())
    return asdict(record)


@router.get("/prompts/{prompt_id}")
def get_prompt(prompt_id: str) -> dict:
    record = service.get_prompt(prompt_id)
    if record is None:
        raise HTTPException(status_code=404, detail="prompt_log_not_found")
    return asdict(record)


@router.post("/outputs")
def log_output(payload: LogOutputRequest) -> dict:
    try:
        record = service.log_output(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(record)


@router.get("/outputs/{output_id}")
def get_output(output_id: str) -> dict:
    record = service.get_output(output_id)
    if record is None:
        raise HTTPException(status_code=404, detail="output_log_not_found")
    return asdict(record)


@router.get("/cases/{case_id}")
def get_case_trace(case_id: str) -> dict:
    trace = service.get_case_trace(case_id)
    return {
        "case_id": trace["case_id"],
        "prompts": [asdict(record) for record in trace["prompts"]],
        "outputs": [asdict(record) for record in trace["outputs"]],
    }
