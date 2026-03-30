from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.ai_closure.repository import FileAIClosureRepository
from petcare.ai_closure.service import AIClosureService
from petcare.ai_dashboard.service import AIDashboardService
from petcare.ai_eval.repository import FileAIEvalRepository
from petcare.ai_eval.service import AIEvalService
from petcare.ai_evidence.repository import FileAIEvidenceRepository
from petcare.ai_evidence.service import AIEvidenceService
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
    evidence_repository = FileAIEvidenceRepository(tmp_path / "ai_evidence")
    closure_repository = FileAIClosureRepository(tmp_path / "ai_closure")

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
    evidence_service = AIEvidenceService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
        evidence_repository=evidence_repository,
        dashboard_service=dashboard_service,
    )
    closure_service = AIClosureService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
        evidence_repository=evidence_repository,
        closure_repository=closure_repository,
        dashboard_service=dashboard_service,
    )
    return trace_service, hitl_service, eval_service, runtime_service, resolution_service, evidence_service, closure_service


def seed_ep_ready_state(tmp_path: Path):
    _, hitl_service, eval_service, runtime_service, resolution_service, evidence_service, closure_service = build_services(tmp_path)

    intake = runtime_service.create_ai_intake(
        tenant_id="tenant_jeddah_001",
        case_id="case_closure_001",
        pet_id="pet_001",
        actor_id="owner_001",
        actor_role="owner",
        species="canine",
        symptom_summary="Dog vomiting and weakness.",
        urgency_level="medium",
        red_flags=[],
        structured_questions=["Any toxin exposure?"],
    )

    draft = runtime_service.create_vet_copilot_draft(
        tenant_id="tenant_jeddah_001",
        case_id="case_closure_001",
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
        output_id=intake.output_log_id,
        approver_id="vet_001",
        approver_role="veterinarian",
        decision="approved",
        reason_code="triage_review_complete",
        notes="approved",
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
        current_pass_rate=0.97,
        baseline_approval_alignment_rate=0.98,
        current_approval_alignment_rate=0.97,
        baseline_risk_flag_alignment_rate=0.98,
        current_risk_flag_alignment_rate=0.97,
    )

    evidence_service.generate_governance_report(
        tenant_id="tenant_jeddah_001",
        scope_type="case",
        scope_id="case_closure_001",
    )

    evidence_service.export_case_evidence(
        tenant_id="tenant_jeddah_001",
        case_id="case_closure_001",
    )

    return closure_service


def test_closure_checklist_becomes_seal_ready_when_ep05_chain_is_complete(tmp_path: Path) -> None:
    closure_service = seed_ep_ready_state(tmp_path)
    checklist = closure_service.generate_ep_closure_checklist(
        tenant_id="tenant_jeddah_001",
        epic_id="EP-05",
    )

    assert checklist.has_logging_foundation is True
    assert checklist.has_hitl_foundation is True
    assert checklist.has_eval_foundation is True
    assert checklist.has_runtime_activation is True
    assert checklist.has_resolution_binding is True
    assert checklist.has_dashboard_read_models is True
    assert checklist.has_evidence_exports is True
    assert checklist.has_governance_reports is True
    assert checklist.has_no_pending_gates is True
    assert checklist.has_no_drift_alerts is True
    assert checklist.seal_ready is True
    assert checklist.ai_execution_authority is False


def test_epic_seal_issues_deterministic_hash_when_ready(tmp_path: Path) -> None:
    closure_service = seed_ep_ready_state(tmp_path)
    seal = closure_service.seal_epic(
        tenant_id="tenant_jeddah_001",
        epic_id="EP-05",
        source_commit="f8cab6175701a1a2cfbd575bf932fcd7a08b1560",
        sealed_by="waheeb",
    )

    assert seal.epic_id == "EP-05"
    assert seal.seal_status == "sealed"
    assert len(seal.checklist_hash) == 64
    assert seal.source_commit == "f8cab6175701a1a2cfbd575bf932fcd7a08b1560"
    assert seal.ai_execution_authority is False


def test_api_round_trip_for_checklist_and_seal(tmp_path: Path) -> None:
    trace_dir = tmp_path / "api_trace"
    hitl_dir = tmp_path / "api_hitl"
    eval_dir = tmp_path / "api_eval"
    runtime_dir = tmp_path / "api_runtime"
    resolution_dir = tmp_path / "api_resolution"
    evidence_dir = tmp_path / "api_evidence"
    closure_dir = tmp_path / "api_closure"

    os.environ["PETCARE_AI_TRACE_DIR"] = str(trace_dir)
    os.environ["PETCARE_AI_HITL_DIR"] = str(hitl_dir)
    os.environ["PETCARE_AI_EVAL_DIR"] = str(eval_dir)
    os.environ["PETCARE_AI_RUNTIME_DIR"] = str(runtime_dir)
    os.environ["PETCARE_AI_RESOLUTION_DIR"] = str(resolution_dir)
    os.environ["PETCARE_AI_EVIDENCE_DIR"] = str(evidence_dir)
    os.environ["PETCARE_AI_CLOSURE_DIR"] = str(closure_dir)

    trace_repository = FileAITraceRepository(trace_dir)
    hitl_repository = FileAIHITLRepository(hitl_dir)
    eval_repository = FileAIEvalRepository(eval_dir)
    runtime_repository = FileAIRuntimeRepository(runtime_dir)
    resolution_repository = FileAIResolutionRepository(resolution_dir)
    evidence_repository = FileAIEvidenceRepository(evidence_dir)

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
    evidence_service = AIEvidenceService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
        evidence_repository=evidence_repository,
        dashboard_service=dashboard_service,
    )

    intake = runtime_service.create_ai_intake(
        tenant_id="tenant_jeddah_001",
        case_id="case_closure_api_001",
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
        case_id="case_closure_api_001",
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
        output_id=intake.output_log_id,
        approver_id="vet_010",
        approver_role="veterinarian",
        decision="approved",
        reason_code="triage_review_complete",
        notes="approved",
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
        current_pass_rate=0.97,
        baseline_approval_alignment_rate=0.98,
        current_approval_alignment_rate=0.97,
        baseline_risk_flag_alignment_rate=0.98,
        current_risk_flag_alignment_rate=0.97,
    )

    evidence_service.generate_governance_report(
        tenant_id="tenant_jeddah_001",
        scope_type="case",
        scope_id="case_closure_api_001",
    )

    evidence_service.export_case_evidence(
        tenant_id="tenant_jeddah_001",
        case_id="case_closure_api_001",
    )

    from petcare.api.routes_ep05_wave08 import router as closure_router

    app = FastAPI()
    app.include_router(closure_router)
    client = TestClient(app)

    checklist_response = client.post("/api/ep05/ai-closure/checklist/tenant_jeddah_001/EP-05")
    assert checklist_response.status_code == 200
    assert checklist_response.json()["seal_ready"] is True

    seal_response = client.post(
        "/api/ep05/ai-closure/seal",
        json={
            "tenant_id": "tenant_jeddah_001",
            "epic_id": "EP-05",
            "source_commit": "f8cab6175701a1a2cfbd575bf932fcd7a08b1560",
            "sealed_by": "waheeb",
        },
    )
    assert seal_response.status_code == 200
    assert seal_response.json()["seal_status"] == "sealed"

    list_seals_response = client.get("/api/ep05/ai-closure/seals")
    assert list_seals_response.status_code == 200
    assert len(list_seals_response.json()["records"]) == 1
