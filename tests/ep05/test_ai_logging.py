from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_logging.service import AITraceService


def test_prompt_logging_sanitizes_and_hashes(tmp_path: Path) -> None:
    repository = FileAITraceRepository(tmp_path / "ai_logging")
    service = AITraceService(repository)

    prompt = service.log_prompt(
        actor_id="vet_001",
        actor_role="veterinarian",
        tenant_id="tenant_jeddah_001",
        case_id="case_123",
        pet_id="pet_abc",
        prompt_text="Owner email is vet@example.com and phone is +966 55 123 4567",
        model_name="gpt-5.4",
        model_version="2026-03",
        provider="openai",
        context_type="consultation",
    )

    assert prompt.prompt_text == "Owner email is [REDACTED_EMAIL] and phone is [REDACTED_PHONE]"
    assert len(prompt.prompt_hash) == 64
    assert prompt.ai_execution_authority is False

    stored = repository.get_prompt(prompt.id)
    assert stored is not None
    assert stored.prompt_hash == prompt.prompt_hash
    assert stored.case_id == "case_123"


def test_output_logging_requires_existing_prompt(tmp_path: Path) -> None:
    repository = FileAITraceRepository(tmp_path / "ai_logging")
    service = AITraceService(repository)

    prompt = service.log_prompt(
        actor_id="pharmacy_001",
        actor_role="pharmacist",
        tenant_id="tenant_jeddah_001",
        case_id="case_rx_456",
        pet_id=None,
        prompt_text="Check medication risk for case_rx_456",
        model_name="claude-sonnet",
        model_version="2026-03",
        provider="anthropic",
        context_type="pharmacy",
    )

    output = service.log_output(
        prompt_id=prompt.id,
        output_text="Potential interaction found. Contact owner at owner@example.com",
        confidence=0.82,
        risk_flags=["interaction", "review_required", "interaction"],
        requires_approval=True,
        approved_by=None,
        approved_at=None,
    )

    assert output.output_text == "Potential interaction found. Contact owner at [REDACTED_EMAIL]"
    assert output.risk_flags == ["interaction", "review_required"]
    assert output.requires_approval is True
    assert output.ai_execution_authority is False

    trace = service.get_case_trace("case_rx_456")
    assert len(trace["prompts"]) == 1
    assert len(trace["outputs"]) == 1
    assert trace["outputs"][0].prompt_id == prompt.id


def test_api_routes_round_trip(tmp_path: Path) -> None:
    os.environ["PETCARE_AI_TRACE_DIR"] = str(tmp_path / "api_trace")

    from petcare.api.routes_ep05_wave01 import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    model_response = client.post(
        "/api/ep05/ai-logging/models",
        json={
            "model_name": "gemini-pro",
            "model_version": "2026-03",
            "provider": "google",
            "status": "active",
            "safety_level": "clinical-assistive",
        },
    )
    assert model_response.status_code == 200

    prompt_response = client.post(
        "/api/ep05/ai-logging/prompts",
        json={
            "actor_id": "admin_001",
            "actor_role": "admin",
            "tenant_id": "tenant_jeddah_001",
            "case_id": "case_trace_001",
            "pet_id": None,
            "prompt_text": "Summarize record for owner@example.com",
            "model_name": "gemini-pro",
            "model_version": "2026-03",
            "provider": "google",
            "context_type": "ops",
        },
    )
    assert prompt_response.status_code == 200
    prompt_payload = prompt_response.json()

    output_response = client.post(
        "/api/ep05/ai-logging/outputs",
        json={
            "prompt_id": prompt_payload["id"],
            "output_text": "Summary ready for owner@example.com",
            "confidence": 0.91,
            "risk_flags": ["assistive_only"],
            "requires_approval": False,
            "approved_by": None,
            "approved_at": None,
        },
    )
    assert output_response.status_code == 200

    case_trace_response = client.get("/api/ep05/ai-logging/cases/case_trace_001")
    assert case_trace_response.status_code == 200
    case_payload = case_trace_response.json()
    assert len(case_payload["prompts"]) == 1
    assert len(case_payload["outputs"]) == 1
    assert case_payload["prompts"][0]["prompt_text"] == "Summarize record for [REDACTED_EMAIL]"
