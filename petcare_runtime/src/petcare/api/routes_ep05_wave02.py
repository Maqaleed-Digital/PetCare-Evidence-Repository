from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from petcare.ai_hitl.service import build_default_hitl_service


router = APIRouter(prefix="/api/ep05/hitl", tags=["ep05-hitl"])


class DecideOutputRequest(BaseModel):
    output_id: str = Field(min_length=1)
    approver_id: str = Field(min_length=1)
    approver_role: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    reason_code: str = Field(min_length=1)
    notes: Optional[str] = None


@router.post("/evaluate/{output_id}")
def evaluate_output(output_id: str) -> dict:
    service = build_default_hitl_service()
    try:
        record = service.evaluate_output(output_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(record)


@router.get("/gates/{output_id}")
def get_gate(output_id: str) -> dict:
    service = build_default_hitl_service()
    record = service.get_gate(output_id)
    if record is None:
        raise HTTPException(status_code=404, detail="approval_gate_not_found")
    return asdict(record)


@router.post("/decide")
def decide_output(payload: DecideOutputRequest) -> dict:
    service = build_default_hitl_service()
    try:
        record = service.decide_output(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(record)


@router.get("/cases/{case_id}")
def get_case_gates(case_id: str) -> dict:
    service = build_default_hitl_service()
    return {
        "case_id": case_id,
        "gates": [asdict(record) for record in service.get_case_gates(case_id)],
    }


@router.get("/outputs/{output_id}/decisions")
def get_output_decisions(output_id: str) -> dict:
    service = build_default_hitl_service()
    return {
        "output_id": output_id,
        "decisions": [asdict(record) for record in service.get_output_decisions(output_id)],
    }
