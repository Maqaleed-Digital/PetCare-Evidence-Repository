from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.ai_dashboard.service import AIDashboardService
from petcare.ai_eval.repository import FileAIEvalRepository
from petcare.ai_eval.service import AIEvalService
from petcare.ai_hitl.repository import FileAIHITLRepository
from petcare.ai_hitl.service import AIHITLService
from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_logging.service import AITraceService
from petcare.ai_resolution.repository import FileAIResolutionRepository
from petcare.ai_resolution.service import AIResolutionService
from petcare.ai_runtime.repository import FileAIRuntimeRepository
from petcare.ai_runtime.service import AIRuntimeService


def build_services(tmp_path: Path):
    trace_repository = FileAITraceRepository(tmp_path / "ai_logging")
    hitl_repository = FileAIHITLRepository(tmp_path / "ai_hitl")
    eval_repository = FileAIEvalRepository(tmp_path / "ai_eval")
    runtime_repository = FileAIRuntimeRepository(tmp_path / "ai_runtime")
    resolution_repository = FileAIResolutionRepository(tmp_path / "ai_resolution")

    trace_service = AITraceService(trace_repository)
    hitl_service = AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)
    eval_service = AIEvalService(eval_repository)
    runtime_service = AIRuntimeService(
        trace_service=trace_service,
        hitl_service=hitl_service,
        runtime_repository=runtime_repository,
    )
    resolution_service = AIResolutionService(
        hitl_service=hitl_service,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
    )
    dashboard_service = AIDashboardService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
    )
    return trace_service, hitl_service, eval_service, runtime_service, resolution_service, dashboard_service


def seed_case(tmp_path: Path):
    trace_service, hitl_service, eval_service, runtime_service, resolution_service, dashboard_service = build_services(tmp_path)

    intake = runtime_service.create_ai_intake(
        tenant_id="tenant_jeddah_001",
        case_id="case_dash_001",
        pet_id="pet_001",
        actor_id="owner_001",
        actor_role="owner",
        species="canine",
        symptom_summary="Dog vomiting and weakness.",
        urgency_level="high",
        red_flags=["review_required"],
        structured_questions=["Any toxin exposure?"],
    )

    draft = runtime_service.create_vet_copilot_draft(
        tenant_id="tenant_jeddah_001",
        case_id="case_dash_001",
        pet_id="pet_001",
        actor_id="vet_001",
        actor_role="veterinarian",
        soap_subjective="Owner reports vomiting.",
        soap_objective="Mild dehydration.",
        soap_assessment="Possible gastroenteritis.",
        soap_plan="Hydration and monitoring.",
        protocol_citations=["PETCARE-GI-001"],
        uncertainty_note="Needs final review.",
    )

    hitl_service.decide_output(
        output_id=draft.output_log_id,
        approver_id="vet_001",
        approver_role="veterinarian",
        decision="approved",
        reason_code="clinical_review_complete",
        notes="approved",
    )

    resolution_service.bind_approval_resolution(
        artifact_type="vet_copilot",
        artifact_id=draft.id,
        resolved_by="vet_001",
        resolved_role="veterinarian",
        resolution_action="accepted_with_review",
        resolution_notes="ready for sign-off",
    )

    resolution_service.bind_clinical_signoff(
        artifact_id=draft.id,
        veterinarian_id="vet_001",
        veterinarian_role="veterinarian",
        final_note_text="Final signed SOAP note.",
    )

    eval_service.run_evaluation(
        suite_name="species-symptom-suite",
        suite_version="2026-03",
        model_name="gpt-5.4",
        model_version="2026-03",
        provider="openai",
        case_results=[
            {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
            {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
        ],
        regression_threshold_pass_rate=0.90,
    )

    eval_service.record_drift_snapshot(
        model_name="gpt-5.4",
        model_version="2026-03",
        provider="openai",
        baseline_pass_rate=0.98,
        current_pass_rate=0.90,
        baseline_approval_alignment_rate=0.98,
        current_approval_alignment_rate=0.92,
        baseline_risk_flag_alignment_rate=0.98,
        current_risk_flag_alignment_rate=0.90,
    )

    return intake, draft, dashboard_service


def test_governance_overview_counts_governed_artifacts(tmp_path: Path) -> None:
    _, _, dashboard_service = seed_case(tmp_path)
    overview = dashboard_service.get_governance_overview("tenant_jeddah_001")

    assert overview.total_prompt_logs == 2
    assert overview.total_output_logs == 2
    assert overview.total_pending_gates == 1
    assert overview.total_approved_gates == 1
    assert overview.total_eval_runs == 1
    assert overview.total_drift_alerts == 1
    assert overview.total_ai_intake_records == 1
    assert overview.total_vet_copilot_records == 1
    assert overview.total_resolutions == 1
    assert overview.total_signoffs == 1
    assert overview.ai_execution_authority is False


def test_operational_alerts_surface_pending_and_drift_conditions(tmp_path: Path) -> None:
    _, _, dashboard_service = seed_case(tmp_path)
    alerts = dashboard_service.list_operational_alerts("tenant_jeddah_001")

    categories = sorted(item.category for item in alerts)
    assert "drift_alert" in categories
    assert "hitl_gate" in categories
    assert any(item.ai_execution_authority is False for item in alerts)


def test_case_governance_view_aggregates_read_model_state(tmp_path: Path) -> None:
    intake, draft, dashboard_service = seed_case(tmp_path)
    view = dashboard_service.get_case_governance_view("tenant_jeddah_001", "case_dash_001")

    assert intake.id in view.runtime_artifact_ids
    assert draft.id in view.runtime_artifact_ids
    assert "approved" in view.gate_statuses
    assert "pending" in view.gate_statuses
    assert len(view.signoff_ids) == 1
    assert view.latest_drift_alert_status == "alert"
    assert view.governance_state == "awaiting_review"
    assert view.ai_execution_authority is False


def test_api_round_trip_for_dashboard_read_models(tmp_path: Path) -> None:
    trace_dir = tmp_path / "api_trace"
    hitl_dir = tmp_path / "api_hitl"
    eval_dir = tmp_path / "api_eval"
    runtime_dir = tmp_path / "api_runtime"
    resolution_dir = tmp_path / "api_resolution"

    os.environ["PETCARE_AI_TRACE_DIR"] = str(trace_dir)
    os.environ["PETCARE_AI_HITL_DIR"] = str(hitl_dir)
    os.environ["PETCARE_AI_EVAL_DIR"] = str(eval_dir)
    os.environ["PETCARE_AI_RUNTIME_DIR"] = str(runtime_dir)
    os.environ["PETCARE_AI_RESOLUTION_DIR"] = str(resolution_dir)

    from petcare.api.routes_ep05_wave02 import router as hitl_router
    from petcare.api.routes_ep05_wave04 import router as runtime_router
    from petcare.api.routes_ep05_wave05 import router as resolution_router
    from petcare.api.routes_ep05_wave06 import router as dashboard_router

    trace_repository = FileAITraceRepository(trace_dir)
    hitl_repository = FileAIHITLRepository(hitl_dir)
    eval_repository = FileAIEvalRepository(eval_dir)
    runtime_repository = FileAIRuntimeRepository(runtime_dir)
    resolution_repository = FileAIResolutionRepository(resolution_dir)

    trace_service = AITraceService(trace_repository)
    hitl_service = AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)
    eval_service = AIEvalService(eval_repository)
    runtime_service = AIRuntimeService(
        trace_service=trace_service,
        hitl_service=hitl_service,
        runtime_repository=runtime_repository,
    )
    resolution_service = AIResolutionService(
        hitl_service=hitl_service,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
    )

    intake = runtime_service.create_ai_intake(
        tenant_id="tenant_jeddah_001",
        case_id="case_dash_api_001",
        pet_id="pet_010",
        actor_id="owner_010",
        actor_role="owner",
        species="feline",
        symptom_summary="Cat lethargic.",
        urgency_level="medium",
        red_flags=[],
        structured_questions=["Any vomiting?"],
    )

    draft = runtime_service.create_vet_copilot_draft(
        tenant_id="tenant_jeddah_001",
        case_id="case_dash_api_001",
        pet_id="pet_010",
        actor_id="vet_010",
        actor_role="veterinarian",
        soap_subjective="Owner reports lethargy.",
        soap_objective="Mild dehydration.",
        soap_assessment="Possible gastroenteritis.",
        soap_plan="Monitoring.",
        protocol_citations=["PETCARE-GI-010"],
        uncertainty_note="Requires final review.",
    )

    hitl_service.decide_output(
        output_id=draft.output_log_id,
        approver_id="vet_010",
        approver_role="veterinarian",
        decision="approved",
        reason_code="clinical_review_complete",
        notes="approved",
    )

    resolution_service.bind_approval_resolution(
        artifact_type="vet_copilot",
        artifact_id=draft.id,
        resolved_by="vet_010",
        resolved_role="veterinarian",
        resolution_action="accepted_with_review",
        resolution_notes="ready for sign-off",
    )

    resolution_service.bind_clinical_signoff(
        artifact_id=draft.id,
        veterinarian_id="vet_010",
        veterinarian_role="veterinarian",
        final_note_text="Final veterinarian signed SOAP note.",
    )

    eval_service.run_evaluation(
        suite_name="species-symptom-suite",
        suite_version="2026-03",
        model_name="claude-sonnet",
        model_version="2026-03",
        provider="anthropic",
        case_results=[
            {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
            {"passed": True, "approval_aligned": True, "risk_flag_aligned": True},
        ],
        regression_threshold_pass_rate=0.90,
    )

    eval_service.record_drift_snapshot(
        model_name="claude-sonnet",
        model_version="2026-03",
        provider="anthropic",
        baseline_pass_rate=0.98,
        current_pass_rate=0.91,
        baseline_approval_alignment_rate=0.98,
        current_approval_alignment_rate=0.92,
        baseline_risk_flag_alignment_rate=0.98,
        current_risk_flag_alignment_rate=0.91,
    )

    app = FastAPI()
    app.include_router(hitl_router)
    app.include_router(runtime_router)
    app.include_router(resolution_router)
    app.include_router(dashboard_router)
    client = TestClient(app)

    overview_response = client.get("/api/ep05/ai-dashboard/overview/tenant_jeddah_001")
    assert overview_response.status_code == 200
    assert overview_response.json()["total_prompt_logs"] == 2

    alerts_response = client.get("/api/ep05/ai-dashboard/alerts/tenant_jeddah_001")
    assert alerts_response.status_code == 200
    assert len(alerts_response.json()["alerts"]) >= 1

    case_response = client.get("/api/ep05/ai-dashboard/cases/tenant_jeddah_001/case_dash_api_001")
    assert case_response.status_code == 200
    assert intake.id in case_response.json()["runtime_artifact_ids"]
