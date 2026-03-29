from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.ai_hitl.repository import FileAIHITLRepository
from petcare.ai_hitl.service import AIHITLService
from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_logging.service import AITraceService


def build_services(tmp_path: Path) -> tuple[AITraceService, AIHITLService]:
    trace_repository = FileAITraceRepository(tmp_path / "ai_logging")
    hitl_repository = FileAIHITLRepository(tmp_path / "ai_hitl")
    trace_service = AITraceService(trace_repository)
    hitl_service = AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)
    return trace_service, hitl_service


def test_actionable_output_creates_pending_gate(tmp_path: Path) -> None:
    trace_service, hitl_service = build_services(tmp_path)

    prompt = trace_service.log_prompt(
        actor_id="pharm_001",
        actor_role="pharmacist",
        tenant_id="tenant_jeddah_001",
        case_id="case_hitl_001",
        pet_id="pet_001",
        prompt_text="Review interaction risk for owner@example.com",
        model_name="gpt-5.4",
        model_version="2026-03",
        provider="openai",
        context_type="pharmacy",
    )

    output = trace_service.log_output(
        prompt_id=prompt.id,
        output_text="Potential interaction. Requires pharmacist review.",
        confidence=0.86,
        risk_flags=["interaction", "review_required"],
        requires_approval=True,
        approved_by=None,
        approved_at=None,
    )

    gate = hitl_service.evaluate_output(output.id)

    assert gate.output_id == output.id
    assert gate.case_id == "case_hitl_001"
    assert gate.decision_class == "actionable"
    assert gate.requires_approval is True
    assert gate.status == "pending"
    assert gate.allowed_roles == ["pharmacist", "veterinarian"]
    assert gate.ai_execution_authority is False


def test_wrong_role_cannot_approve_actionable_output(tmp_path: Path) -> None:
    trace_service, hitl_service = build_services(tmp_path)

    prompt = trace_service.log_prompt(
        actor_id="vet_001",
        actor_role="veterinarian",
        tenant_id="tenant_jeddah_001",
        case_id="case_hitl_002",
        pet_id="pet_002",
        prompt_text="Escalate emergency red flag for +966 55 123 4567",
        model_name="claude-sonnet",
        model_version="2026-03",
        provider="anthropic",
        context_type="emergency",
    )

    output = trace_service.log_output(
        prompt_id=prompt.id,
        output_text="Emergency red flag identified",
        confidence=0.93,
        risk_flags=["emergency_red_flag"],
        requires_approval=True,
        approved_by=None,
        approved_at=None,
    )

    hitl_service.evaluate_output(output.id)

    try:
        hitl_service.decide_output(
            output_id=output.id,
            approver_id="admin_001",
            approver_role="admin",
            decision="approved",
            reason_code="manual_review_complete",
            notes="attempted by wrong role",
        )
        assert False, "Expected ValueError for disallowed approver_role"
    except ValueError as exc:
        assert "approver_role_not_allowed" in str(exc)


def test_api_round_trip_evaluate_and_approve(tmp_path: Path) -> None:
    trace_dir = tmp_path / "api_trace"
    hitl_dir = tmp_path / "api_hitl"

    os.environ["PETCARE_AI_TRACE_DIR"] = str(trace_dir)
    os.environ["PETCARE_AI_HITL_DIR"] = str(hitl_dir)

    trace_service = AITraceService(FileAITraceRepository(trace_dir))
    prompt = trace_service.log_prompt(
        actor_id="vet_002",
        actor_role="veterinarian",
        tenant_id="tenant_jeddah_001",
        case_id="case_hitl_003",
        pet_id="pet_003",
        prompt_text="Draft consultation summary for owner@example.com",
        model_name="gemini-pro",
        model_version="2026-03",
        provider="google",
        context_type="consultation",
    )
    output = trace_service.log_output(
        prompt_id=prompt.id,
        output_text="Potential diagnosis support. Review required.",
        confidence=0.88,
        risk_flags=["review_required"],
        requires_approval=True,
        approved_by=None,
        approved_at=None,
    )

    from petcare.api.routes_ep05_wave02 import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    evaluate_response = client.post(f"/api/ep05/hitl/evaluate/{output.id}")
    assert evaluate_response.status_code == 200
    gate_payload = evaluate_response.json()
    assert gate_payload["status"] == "pending"
    assert gate_payload["decision_class"] == "actionable"

    approve_response = client.post(
        "/api/ep05/hitl/decide",
        json={
            "output_id": output.id,
            "approver_id": "vet_approver_001",
            "approver_role": "veterinarian",
            "decision": "approved",
            "reason_code": "clinical_review_complete",
            "notes": "approved after review",
        },
    )
    assert approve_response.status_code == 200
    decision_payload = approve_response.json()
    assert decision_payload["decision"] == "approved"
    assert decision_payload["ai_execution_authority"] is False

    gate_response = client.get(f"/api/ep05/hitl/gates/{output.id}")
    assert gate_response.status_code == 200
    assert gate_response.json()["status"] == "approved"

    decisions_response = client.get(f"/api/ep05/hitl/outputs/{output.id}/decisions")
    assert decisions_response.status_code == 200
    assert len(decisions_response.json()["decisions"]) == 1
