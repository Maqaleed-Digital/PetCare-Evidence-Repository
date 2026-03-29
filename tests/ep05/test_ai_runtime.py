from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.ai_hitl.repository import FileAIHITLRepository
from petcare.ai_hitl.service import AIHITLService
from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_logging.service import AITraceService
from petcare.ai_runtime.repository import FileAIRuntimeRepository
from petcare.ai_runtime.service import AIRuntimeService


def build_services(tmp_path: Path) -> AIRuntimeService:
    trace_repository = FileAITraceRepository(tmp_path / "ai_logging")
    hitl_repository = FileAIHITLRepository(tmp_path / "ai_hitl")
    runtime_repository = FileAIRuntimeRepository(tmp_path / "ai_runtime")
    trace_service = AITraceService(trace_repository)
    hitl_service = AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)
    return AIRuntimeService(
        trace_service=trace_service,
        hitl_service=hitl_service,
        runtime_repository=runtime_repository,
    )


def test_ai_intake_creates_trace_and_pending_review(tmp_path: Path) -> None:
    service = build_services(tmp_path)

    record = service.create_ai_intake(
        tenant_id="tenant_jeddah_001",
        case_id="case_intake_001",
        pet_id="pet_001",
        actor_id="owner_001",
        actor_role="owner",
        species="canine",
        symptom_summary="Dog vomiting and lethargy. Contact owner@example.com",
        urgency_level="high",
        red_flags=["emergency_red_flag", "review_required"],
        structured_questions=["How long has vomiting been present?", "Any toxin exposure?"],
    )

    assert record.case_id == "case_intake_001"
    assert record.hitl_required is True
    assert record.status == "pending_review"
    assert record.disclaimer.startswith("AI intake is assistive only")
    assert record.ai_execution_authority is False
    assert record.symptom_summary == "Dog vomiting and lethargy. Contact [REDACTED_EMAIL]"


def test_vet_copilot_draft_is_assistive_and_hitl_bound(tmp_path: Path) -> None:
    service = build_services(tmp_path)

    record = service.create_vet_copilot_draft(
        tenant_id="tenant_jeddah_001",
        case_id="case_copilot_001",
        pet_id="pet_002",
        actor_id="vet_001",
        actor_role="veterinarian",
        soap_subjective="Owner reports coughing and fever.",
        soap_objective="Temp elevated, mild respiratory distress.",
        soap_assessment="Possible upper respiratory infection.",
        soap_plan="Supportive care and further diagnostics.",
        protocol_citations=["PETCARE-URI-001", "PETCARE-RESP-002"],
        uncertainty_note="Differential diagnosis remains broad pending tests.",
    )

    assert record.case_id == "case_copilot_001"
    assert record.hitl_required is True
    assert record.status == "pending_review"
    assert record.protocol_citations == ["PETCARE-URI-001", "PETCARE-RESP-002"]
    assert record.disclaimer.startswith("AI copilot draft is assistive only")
    assert record.ai_execution_authority is False


def test_api_round_trip_for_ai_runtime(tmp_path: Path) -> None:
    trace_dir = tmp_path / "api_trace"
    hitl_dir = tmp_path / "api_hitl"
    runtime_dir = tmp_path / "api_runtime"

    os.environ["PETCARE_AI_TRACE_DIR"] = str(trace_dir)
    os.environ["PETCARE_AI_HITL_DIR"] = str(hitl_dir)
    os.environ["PETCARE_AI_RUNTIME_DIR"] = str(runtime_dir)

    from petcare.api.routes_ep05_wave04 import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    intake_response = client.post(
        "/api/ep05/ai-runtime/intake",
        json={
            "tenant_id": "tenant_jeddah_001",
            "case_id": "case_runtime_001",
            "pet_id": "pet_003",
            "actor_id": "owner_002",
            "actor_role": "owner",
            "species": "feline",
            "symptom_summary": "Cat not eating and hiding.",
            "urgency_level": "medium",
            "red_flags": [],
            "structured_questions": ["Is there vomiting?", "When did appetite change begin?"],
        },
    )
    assert intake_response.status_code == 200
    intake_payload = intake_response.json()
    assert intake_payload["ai_execution_authority"] is False

    copilot_response = client.post(
        "/api/ep05/ai-runtime/vet-copilot",
        json={
            "tenant_id": "tenant_jeddah_001",
            "case_id": "case_runtime_001",
            "pet_id": "pet_003",
            "actor_id": "vet_002",
            "actor_role": "veterinarian",
            "soap_subjective": "Owner reports reduced appetite.",
            "soap_objective": "Mild dehydration noted.",
            "soap_assessment": "Possible gastroenteritis.",
            "soap_plan": "Hydration and monitoring; diagnostics if worsening.",
            "protocol_citations": ["PETCARE-GI-001"],
            "uncertainty_note": "Requires veterinarian final interpretation.",
        },
    )
    assert copilot_response.status_code == 200
    copilot_payload = copilot_response.json()
    assert copilot_payload["hitl_required"] is True

    list_intake_response = client.get("/api/ep05/ai-runtime/cases/case_runtime_001/intake")
    assert list_intake_response.status_code == 200
    assert len(list_intake_response.json()["records"]) == 1

    list_copilot_response = client.get("/api/ep05/ai-runtime/cases/case_runtime_001/vet-copilot")
    assert list_copilot_response.status_code == 200
    assert len(list_copilot_response.json()["records"]) == 1
