from __future__ import annotations

import os
import uuid
from typing import Iterable, Optional

from petcare.ai_hitl.service import AIHITLService
from petcare.ai_logging.service import AITraceService

from .models import AIIntakeRecord, VetCopilotDraftRecord, utc_now_iso
from .repository import FileAIRuntimeRepository


class AIRuntimeService:
    INTAKE_DISCLAIMER = "AI intake is assistive only and requires veterinarian review before any clinical action."
    COPILOT_DISCLAIMER = "AI copilot draft is assistive only. Veterinarian approval and sign-off are mandatory."
    INTAKE_MODEL = ("openai", "gpt-5.4", "2026-03")
    COPILOT_MODEL = ("anthropic", "claude-sonnet", "2026-03")

    def __init__(
        self,
        trace_service: AITraceService,
        hitl_service: AIHITLService,
        runtime_repository: FileAIRuntimeRepository,
    ) -> None:
        self.trace_service = trace_service
        self.hitl_service = hitl_service
        self.runtime_repository = runtime_repository

    def _normalize_flags(self, flags: Iterable[str]) -> list[str]:
        return sorted({flag.strip() for flag in flags if flag and flag.strip()})

    def _normalize_lines(self, lines: Iterable[str]) -> list[str]:
        return [line.strip() for line in lines if line and line.strip()]

    def create_ai_intake(
        self,
        *,
        tenant_id: str,
        case_id: str,
        pet_id: Optional[str],
        actor_id: str,
        actor_role: str,
        species: str,
        symptom_summary: str,
        urgency_level: str,
        red_flags: Iterable[str],
        structured_questions: Iterable[str],
    ) -> AIIntakeRecord:
        provider, model_name, model_version = self.INTAKE_MODEL

        prompt = self.trace_service.log_prompt(
            actor_id=actor_id,
            actor_role=actor_role,
            tenant_id=tenant_id,
            case_id=case_id,
            pet_id=pet_id,
            prompt_text=f"AI intake for {species}: {symptom_summary}",
            model_name=model_name,
            model_version=model_version,
            provider=provider,
            context_type="triage",
        )

        normalized_red_flags = self._normalize_flags(red_flags)
        normalized_questions = self._normalize_lines(structured_questions)
        requires_approval = urgency_level in {"high", "critical"} or bool(normalized_red_flags)

        output = self.trace_service.log_output(
            prompt_id=prompt.id,
            output_text=f"Urgency={urgency_level}; red_flags={','.join(normalized_red_flags) or 'none'}; questions={len(normalized_questions)}",
            confidence=0.85,
            risk_flags=normalized_red_flags or ["review_required"],
            requires_approval=requires_approval,
            approved_by=None,
            approved_at=None,
        )

        gate = self.hitl_service.evaluate_output(output.id)

        record = AIIntakeRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            case_id=case_id,
            pet_id=pet_id,
            actor_id=actor_id,
            actor_role=actor_role,
            species=species,
            symptom_summary=self.trace_service.sanitize_text(symptom_summary),
            urgency_level=urgency_level,
            red_flags=normalized_red_flags,
            structured_questions=normalized_questions,
            disclaimer=self.INTAKE_DISCLAIMER,
            prompt_log_id=prompt.id,
            output_log_id=output.id,
            approval_gate_id=gate.output_id if gate.requires_approval else None,
            hitl_required=gate.requires_approval,
            status="pending_review" if gate.requires_approval else "drafted",
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.runtime_repository.save_intake(record)

    def create_vet_copilot_draft(
        self,
        *,
        tenant_id: str,
        case_id: str,
        pet_id: Optional[str],
        actor_id: str,
        actor_role: str,
        soap_subjective: str,
        soap_objective: str,
        soap_assessment: str,
        soap_plan: str,
        protocol_citations: Iterable[str],
        uncertainty_note: str,
    ) -> VetCopilotDraftRecord:
        provider, model_name, model_version = self.COPILOT_MODEL

        prompt = self.trace_service.log_prompt(
            actor_id=actor_id,
            actor_role=actor_role,
            tenant_id=tenant_id,
            case_id=case_id,
            pet_id=pet_id,
            prompt_text=f"Vet copilot SOAP draft for case {case_id}",
            model_name=model_name,
            model_version=model_version,
            provider=provider,
            context_type="consultation",
        )

        citations = self._normalize_lines(protocol_citations)
        output = self.trace_service.log_output(
            prompt_id=prompt.id,
            output_text="SOAP draft generated with protocol support and mandatory veterinarian review.",
            confidence=0.89,
            risk_flags=["review_required"],
            requires_approval=True,
            approved_by=None,
            approved_at=None,
        )

        gate = self.hitl_service.evaluate_output(output.id)

        record = VetCopilotDraftRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            case_id=case_id,
            pet_id=pet_id,
            actor_id=actor_id,
            actor_role=actor_role,
            soap_subjective=self.trace_service.sanitize_text(soap_subjective),
            soap_objective=self.trace_service.sanitize_text(soap_objective),
            soap_assessment=self.trace_service.sanitize_text(soap_assessment),
            soap_plan=self.trace_service.sanitize_text(soap_plan),
            protocol_citations=citations,
            uncertainty_note=self.trace_service.sanitize_text(uncertainty_note),
            disclaimer=self.COPILOT_DISCLAIMER,
            prompt_log_id=prompt.id,
            output_log_id=output.id,
            approval_gate_id=gate.output_id if gate.requires_approval else None,
            hitl_required=gate.requires_approval,
            status="pending_review" if gate.requires_approval else "drafted",
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.runtime_repository.save_copilot_draft(record)

    def get_intake(self, record_id: str) -> Optional[AIIntakeRecord]:
        return self.runtime_repository.get_intake(record_id)

    def list_case_intake(self, case_id: str) -> list[AIIntakeRecord]:
        return self.runtime_repository.list_case_intake(case_id)

    def get_vet_copilot_draft(self, record_id: str) -> Optional[VetCopilotDraftRecord]:
        return self.runtime_repository.get_copilot_draft(record_id)

    def list_case_vet_copilot_drafts(self, case_id: str) -> list[VetCopilotDraftRecord]:
        return self.runtime_repository.list_case_copilot_drafts(case_id)


def build_default_ai_runtime_service() -> AIRuntimeService:
    from petcare.ai_hitl.repository import FileAIHITLRepository
    from petcare.ai_logging.repository import FileAITraceRepository

    trace_base_path = os.environ.get(
        "PETCARE_AI_TRACE_DIR",
        "petcare_runtime/runtime_data/ai_logging",
    )
    hitl_base_path = os.environ.get(
        "PETCARE_AI_HITL_DIR",
        "petcare_runtime/runtime_data/ai_hitl",
    )
    runtime_base_path = os.environ.get(
        "PETCARE_AI_RUNTIME_DIR",
        "petcare_runtime/runtime_data/ai_runtime",
    )

    trace_repository = FileAITraceRepository(trace_base_path)
    hitl_repository = FileAIHITLRepository(hitl_base_path)
    runtime_repository = FileAIRuntimeRepository(runtime_base_path)

    trace_service = AITraceService(trace_repository)
    hitl_service = AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)

    return AIRuntimeService(
        trace_service=trace_service,
        hitl_service=hitl_service,
        runtime_repository=runtime_repository,
    )
