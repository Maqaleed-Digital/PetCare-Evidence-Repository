from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.ai_hitl.repository import FileAIHITLRepository
from petcare.ai_hitl.service import AIHITLService
from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_logging.service import AITraceService
from petcare.ai_resolution.repository import FileAIResolutionRepository
from petcare.ai_resolution.service import AIResolutionService
from petcare.ai_runtime.repository import FileAIRuntimeRepository
from petcare.ai_runtime.service import AIRuntimeService


def build_services(tmp_path: Path) -> tuple[AIRuntimeService, AIHITLService, AIResolutionService]:
    trace_repository = FileAITraceRepository(tmp_path / "ai_logging")
    hitl_repository = FileAIHITLRepository(tmp_path / "ai_hitl")
    runtime_repository = FileAIRuntimeRepository(tmp_path / "ai_runtime")
    resolution_repository = FileAIResolutionRepository(tmp_path / "ai_resolution")

    trace_service = AITraceService(trace_repository)
    hitl_service = AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)
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
    return runtime_service, hitl_service, resolution_service


def test_approved_ai_intake_can_bind_human_resolution(tmp_path: Path) -> None:
    runtime_service, hitl_service, resolution_service = build_services(tmp_path)

    intake = runtime_service.create_ai_intake(
        tenant_id="tenant_jeddah_001",
        case_id="case_resolution_001",
        pet_id="pet_001",
        actor_id="owner_001",
        actor_role="owner",
        species="canine",
        symptom_summary="Dog vomiting and weakness.",
        urgency_level="high",
        red_flags=["review_required"],
        structured_questions=["Any toxin exposure?"],
    )

    hitl_service.decide_output(
        output_id=intake.output_log_id,
        approver_id="vet_001",
        approver_role="veterinarian",
        decision="approved",
        reason_code="triage_review_complete",
        notes="approved after veterinarian review",
    )

    resolution = resolution_service.bind_approval_resolution(
        artifact_type="ai_intake",
        artifact_id=intake.id,
        resolved_by="vet_001",
        resolved_role="veterinarian",
        resolution_action="accepted_with_review",
        resolution_notes="owner advised to attend consultation",
    )

    assert resolution.case_id == "case_resolution_001"
    assert resolution.gate_status == "approved"
    assert resolution.resolution_action == "accepted_with_review"
    assert resolution.ai_execution_authority is False


def test_vet_copilot_requires_approved_resolution_before_signoff(tmp_path: Path) -> None:
    runtime_service, hitl_service, resolution_service = build_services(tmp_path)

    draft = runtime_service.create_vet_copilot_draft(
        tenant_id="tenant_jeddah_001",
        case_id="case_resolution_002",
        pet_id="pet_002",
        actor_id="vet_001",
        actor_role="veterinarian",
        soap_subjective="Owner reports coughing.",
        soap_objective="Mild wheeze on exam.",
        soap_assessment="Possible respiratory infection.",
        soap_plan="Supportive care and diagnostics.",
        protocol_citations=["PETCARE-RESP-001"],
        uncertainty_note="Needs veterinarian final judgment.",
    )

    try:
        resolution_service.bind_clinical_signoff(
            artifact_id=draft.id,
            veterinarian_id="vet_001",
            veterinarian_role="veterinarian",
            final_note_text="Final signed SOAP note.",
        )
        assert False, "Expected approval_resolution_missing_for_artifact"
    except ValueError as exc:
        assert "approval_resolution_missing_for_artifact" in str(exc)

    hitl_service.decide_output(
        output_id=draft.output_log_id,
        approver_id="vet_001",
        approver_role="veterinarian",
        decision="approved",
        reason_code="clinical_review_complete",
        notes="draft approved",
    )

    resolution_service.bind_approval_resolution(
        artifact_type="vet_copilot",
        artifact_id=draft.id,
        resolved_by="vet_001",
        resolved_role="veterinarian",
        resolution_action="accepted_with_review",
        resolution_notes="ready for final sign-off",
    )

    signoff = resolution_service.bind_clinical_signoff(
        artifact_id=draft.id,
        veterinarian_id="vet_001",
        veterinarian_role="veterinarian",
        final_note_text="Final signed SOAP note.",
    )

    assert signoff.case_id == "case_resolution_002"
    assert signoff.signoff_status == "signed"
    assert signoff.immutable_after_signoff is True
    assert len(signoff.final_note_hash) == 64
    assert signoff.ai_execution_authority is False


def test_api_round_trip_for_resolution_and_signoff(tmp_path: Path) -> None:
    trace_dir = tmp_path / "api_trace"
    hitl_dir = tmp_path / "api_hitl"
    runtime_dir = tmp_path / "api_runtime"
    resolution_dir = tmp_path / "api_resolution"

    os.environ["PETCARE_AI_TRACE_DIR"] = str(trace_dir)
    os.environ["PETCARE_AI_HITL_DIR"] = str(hitl_dir)
    os.environ["PETCARE_AI_RUNTIME_DIR"] = str(runtime_dir)
    os.environ["PETCARE_AI_RESOLUTION_DIR"] = str(resolution_dir)

    from petcare.api.routes_ep05_wave02 import router as hitl_router
    from petcare.api.routes_ep05_wave04 import router as runtime_router
    from petcare.api.routes_ep05_wave05 import router as resolution_router

    app = FastAPI()
    app.include_router(runtime_router)
    app.include_router(hitl_router)
    app.include_router(resolution_router)
    client = TestClient(app)

    draft_response = client.post(
        "/api/ep05/ai-runtime/vet-copilot",
        json={
            "tenant_id": "tenant_jeddah_001",
            "case_id": "case_resolution_003",
            "pet_id": "pet_003",
            "actor_id": "vet_002",
            "actor_role": "veterinarian",
            "soap_subjective": "Owner reports reduced appetite.",
            "soap_objective": "Mild dehydration noted.",
            "soap_assessment": "Possible gastroenteritis.",
            "soap_plan": "Hydration and monitoring.",
            "protocol_citations": ["PETCARE-GI-001"],
            "uncertainty_note": "Requires final veterinarian review.",
        },
    )
    assert draft_response.status_code == 200
    draft_payload = draft_response.json()

    approve_response = client.post(
        "/api/ep05/hitl/decide",
        json={
            "output_id": draft_payload["output_log_id"],
            "approver_id": "vet_approver_001",
            "approver_role": "veterinarian",
            "decision": "approved",
            "reason_code": "clinical_review_complete",
            "notes": "approved after review",
        },
    )
    assert approve_response.status_code == 200

    resolution_response = client.post(
        "/api/ep05/ai-resolution/resolve",
        json={
            "artifact_type": "vet_copilot",
            "artifact_id": draft_payload["id"],
            "resolved_by": "vet_approver_001",
            "resolved_role": "veterinarian",
            "resolution_action": "accepted_with_review",
            "resolution_notes": "ready for sign-off",
        },
    )
    assert resolution_response.status_code == 200
    resolution_payload = resolution_response.json()
    assert resolution_payload["gate_status"] == "approved"

    signoff_response = client.post(
        "/api/ep05/ai-resolution/signoff",
        json={
            "artifact_id": draft_payload["id"],
            "veterinarian_id": "vet_approver_001",
            "veterinarian_role": "veterinarian",
            "final_note_text": "Final veterinarian signed SOAP note.",
        },
    )
    assert signoff_response.status_code == 200
    signoff_payload = signoff_response.json()
    assert signoff_payload["signoff_status"] == "signed"
    assert signoff_payload["immutable_after_signoff"] is True

    list_resolution_response = client.get("/api/ep05/ai-resolution/cases/case_resolution_003/resolutions")
    assert list_resolution_response.status_code == 200
    assert len(list_resolution_response.json()["records"]) == 1

    list_signoff_response = client.get("/api/ep05/ai-resolution/cases/case_resolution_003/signoffs")
    assert list_signoff_response.status_code == 200
    assert len(list_signoff_response.json()["records"]) == 1
