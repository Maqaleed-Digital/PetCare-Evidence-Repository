from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.ai_eval.repository import FileAIEvalRepository
from petcare.ai_eval.service import AIEvalService


def build_service(tmp_path: Path) -> AIEvalService:
    repository = FileAIEvalRepository(tmp_path / "ai_eval")
    return AIEvalService(repository)


def test_register_eval_case_persists_expected_controls(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    record = service.register_eval_case(
        species="canine",
        symptom_cluster="vomiting",
        context_type="triage",
        expected_risk_flags=["review_required", "emergency_red_flag", "review_required"],
        expected_requires_approval=True,
        expected_decision_class="actionable",
    )

    assert record.species == "canine"
    assert record.context_type == "triage"
    assert record.expected_risk_flags == ["emergency_red_flag", "review_required"]
    assert record.expected_requires_approval is True
    assert record.expected_decision_class == "actionable"
    assert record.ai_execution_authority is False


def test_run_evaluation_computes_metrics_and_status(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    run = service.run_evaluation(
        suite_name="species-symptom-suite",
        suite_version="2026-03",
        model_name="gpt-5.4",
        model_version="2026-03",
        provider="openai",
        case_results=[
            {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
            {"passed": True, "approval_aligned": True, "risk_flag_aligned": False},
            {"passed": False, "approval_aligned": False, "risk_flag_aligned": False},
            {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
        ],
        regression_threshold_pass_rate=0.70,
    )

    assert run.total_cases == 4
    assert run.passed_cases == 3
    assert run.pass_rate == 0.75
    assert run.approval_alignment_rate == 0.75
    assert run.risk_flag_alignment_rate == 0.5
    assert run.status == "fail"
    assert run.ai_execution_authority is False


def test_record_drift_snapshot_alerts_on_threshold_breach(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    snapshot = service.record_drift_snapshot(
        model_name="gemini-pro",
        model_version="2026-03",
        provider="google",
        baseline_pass_rate=0.97,
        current_pass_rate=0.88,
        baseline_approval_alignment_rate=0.96,
        current_approval_alignment_rate=0.94,
        baseline_risk_flag_alignment_rate=0.95,
        current_risk_flag_alignment_rate=0.89,
    )

    assert snapshot.pass_rate_delta == -0.09
    assert snapshot.approval_alignment_delta == -0.02
    assert snapshot.risk_flag_alignment_delta == -0.06
    assert snapshot.alert_status == "alert"
    assert snapshot.ai_execution_authority is False


def test_api_round_trip_for_eval_and_drift(tmp_path: Path) -> None:
    eval_dir = tmp_path / "api_eval"
    os.environ["PETCARE_AI_EVAL_DIR"] = str(eval_dir)

    from petcare.api.routes_ep05_wave03 import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    case_response = client.post(
        "/api/ep05/ai-eval/cases",
        json={
            "species": "feline",
            "symptom_cluster": "respiratory_distress",
            "context_type": "emergency",
            "expected_risk_flags": ["emergency_red_flag", "review_required"],
            "expected_requires_approval": True,
            "expected_decision_class": "actionable",
        },
    )
    assert case_response.status_code == 200

    run_response = client.post(
        "/api/ep05/ai-eval/runs",
        json={
            "suite_name": "species-symptom-suite",
            "suite_version": "2026-03",
            "model_name": "claude-sonnet",
            "model_version": "2026-03",
            "provider": "anthropic",
            "case_results": [
                {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
                {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
                {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
                {"passed": True, "approval_aligned": True, "risk_flag_aligned": False},
            ],
            "regression_threshold_pass_rate": 0.95,
        },
    )
    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["status"] == "pass"

    drift_response = client.post(
        "/api/ep05/ai-eval/drift",
        json={
            "model_name": "claude-sonnet",
            "model_version": "2026-03",
            "provider": "anthropic",
            "baseline_pass_rate": 0.98,
            "current_pass_rate": 0.97,
            "baseline_approval_alignment_rate": 0.97,
            "current_approval_alignment_rate": 0.96,
            "baseline_risk_flag_alignment_rate": 0.96,
            "current_risk_flag_alignment_rate": 0.95,
        },
    )
    assert drift_response.status_code == 200
    drift_payload = drift_response.json()
    assert drift_payload["alert_status"] == "stable"

    list_runs_response = client.get("/api/ep05/ai-eval/runs")
    assert list_runs_response.status_code == 200
    assert len(list_runs_response.json()) == 1

    list_drift_response = client.get("/api/ep05/ai-eval/drift")
    assert list_drift_response.status_code == 200
    assert len(list_drift_response.json()) == 1
