from __future__ import annotations

from dataclasses import asdict
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from petcare.ai_eval.service import build_default_eval_service


router = APIRouter(prefix="/api/ep05/ai-eval", tags=["ep05-ai-eval"])
service = build_default_eval_service()


class RegisterEvalCaseRequest(BaseModel):
    species: str = Field(min_length=1)
    symptom_cluster: str = Field(min_length=1)
    context_type: str = Field(min_length=1)
    expected_risk_flags: List[str] = Field(default_factory=list)
    expected_requires_approval: bool = False
    expected_decision_class: str = Field(min_length=1)


class EvalCaseResultRequest(BaseModel):
    passed: bool
    approval_aligned: bool
    risk_flag_aligned: bool


class RunEvaluationRequest(BaseModel):
    suite_name: str = Field(min_length=1)
    suite_version: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    case_results: List[EvalCaseResultRequest]
    regression_threshold_pass_rate: float = Field(ge=0.0, le=1.0)


class RecordDriftSnapshotRequest(BaseModel):
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    baseline_pass_rate: float = Field(ge=0.0, le=1.0)
    current_pass_rate: float = Field(ge=0.0, le=1.0)
    baseline_approval_alignment_rate: float = Field(ge=0.0, le=1.0)
    current_approval_alignment_rate: float = Field(ge=0.0, le=1.0)
    baseline_risk_flag_alignment_rate: float = Field(ge=0.0, le=1.0)
    current_risk_flag_alignment_rate: float = Field(ge=0.0, le=1.0)


@router.post("/cases")
def register_eval_case(payload: RegisterEvalCaseRequest) -> dict:
    record = service.register_eval_case(**payload.model_dump())
    return asdict(record)


@router.get("/cases")
def list_eval_cases() -> list[dict]:
    return [asdict(record) for record in service.list_cases()]


@router.get("/cases/{case_id}")
def get_eval_case(case_id: str) -> dict:
    record = service.get_case(case_id)
    if record is None:
        raise HTTPException(status_code=404, detail="eval_case_not_found")
    return asdict(record)


@router.post("/runs")
def run_evaluation(payload: RunEvaluationRequest) -> dict:
    try:
        record = service.run_evaluation(
            suite_name=payload.suite_name,
            suite_version=payload.suite_version,
            model_name=payload.model_name,
            model_version=payload.model_version,
            provider=payload.provider,
            case_results=[item.model_dump() for item in payload.case_results],
            regression_threshold_pass_rate=payload.regression_threshold_pass_rate,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(record)


@router.get("/runs")
def list_eval_runs() -> list[dict]:
    return [asdict(record) for record in service.list_runs()]


@router.get("/runs/{run_id}")
def get_eval_run(run_id: str) -> dict:
    record = service.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="eval_run_not_found")
    return asdict(record)


@router.post("/drift")
def record_drift_snapshot(payload: RecordDriftSnapshotRequest) -> dict:
    record = service.record_drift_snapshot(**payload.model_dump())
    return asdict(record)


@router.get("/drift")
def list_drift_snapshots() -> list[dict]:
    return [asdict(record) for record in service.list_drift_snapshots()]


@router.get("/drift/{snapshot_id}")
def get_drift_snapshot(snapshot_id: str) -> dict:
    record = service.get_drift_snapshot(snapshot_id)
    if record is None:
        raise HTTPException(status_code=404, detail="drift_snapshot_not_found")
    return asdict(record)
