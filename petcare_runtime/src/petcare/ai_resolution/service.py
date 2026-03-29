from __future__ import annotations

import hashlib
import os
import uuid
from typing import Optional

from petcare.ai_hitl.service import AIHITLService
from petcare.ai_runtime.repository import FileAIRuntimeRepository

from .models import ApprovalResolutionRecord, ClinicalSignoffBindingRecord, utc_now_iso
from .repository import FileAIResolutionRepository


class AIResolutionService:
    ALLOWED_RESOLUTION_ACTIONS = {
        "accepted_with_review",
        "rejected_after_review",
        "returned_for_revision",
    }

    def __init__(
        self,
        hitl_service: AIHITLService,
        runtime_repository: FileAIRuntimeRepository,
        resolution_repository: FileAIResolutionRepository,
    ) -> None:
        self.hitl_service = hitl_service
        self.runtime_repository = runtime_repository
        self.resolution_repository = resolution_repository

    def _hash_text(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _load_artifact(self, artifact_type: str, artifact_id: str) -> tuple[str, object]:
        if artifact_type == "ai_intake":
            record = self.runtime_repository.get_intake(artifact_id)
            if record is None:
                raise ValueError(f"ai_intake_not_found: {artifact_id}")
            return "ai_intake", record
        if artifact_type == "vet_copilot":
            record = self.runtime_repository.get_copilot_draft(artifact_id)
            if record is None:
                raise ValueError(f"vet_copilot_not_found: {artifact_id}")
            return "vet_copilot", record
        raise ValueError(f"unsupported_artifact_type: {artifact_type}")

    def bind_approval_resolution(
        self,
        *,
        artifact_type: str,
        artifact_id: str,
        resolved_by: str,
        resolved_role: str,
        resolution_action: str,
        resolution_notes: Optional[str],
    ) -> ApprovalResolutionRecord:
        if resolution_action not in self.ALLOWED_RESOLUTION_ACTIONS:
            raise ValueError("unsupported_resolution_action")

        normalized_type, artifact = self._load_artifact(artifact_type, artifact_id)
        existing = self.resolution_repository.find_resolution_for_artifact(normalized_type, artifact_id)
        if existing is not None:
            raise ValueError(f"resolution_already_exists_for_artifact: {artifact_id}")

        gate_id = getattr(artifact, "approval_gate_id", None)
        if not gate_id:
            raise ValueError(f"approval_gate_missing_for_artifact: {artifact_id}")

        gate = self.hitl_service.get_gate(gate_id)
        if gate is None:
            raise ValueError(f"approval_gate_not_found: {gate_id}")

        if gate.status not in {"approved", "rejected"}:
            raise ValueError(f"approval_gate_not_resolved: {gate.status}")

        if resolved_role not in gate.allowed_roles:
            raise ValueError(f"resolved_role_not_allowed: {resolved_role}")

        record = ApprovalResolutionRecord(
            id=str(uuid.uuid4()),
            tenant_id=getattr(artifact, "tenant_id"),
            case_id=getattr(artifact, "case_id"),
            artifact_type=normalized_type,
            artifact_id=artifact_id,
            output_id=getattr(artifact, "output_log_id"),
            gate_status=gate.status,
            resolved_by=resolved_by,
            resolved_role=resolved_role,
            resolution_action=resolution_action,
            resolution_notes=resolution_notes,
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.resolution_repository.save_resolution(record)

    def bind_clinical_signoff(
        self,
        *,
        artifact_id: str,
        veterinarian_id: str,
        veterinarian_role: str,
        final_note_text: str,
    ) -> ClinicalSignoffBindingRecord:
        if veterinarian_role != "veterinarian":
            raise ValueError("veterinarian_role_required")

        artifact = self.runtime_repository.get_copilot_draft(artifact_id)
        if artifact is None:
            raise ValueError(f"vet_copilot_not_found: {artifact_id}")

        existing = self.resolution_repository.find_signoff_for_artifact("vet_copilot", artifact_id)
        if existing is not None:
            raise ValueError(f"clinical_signoff_already_exists_for_artifact: {artifact_id}")

        resolution = self.resolution_repository.find_resolution_for_artifact("vet_copilot", artifact_id)
        if resolution is None:
            raise ValueError(f"approval_resolution_missing_for_artifact: {artifact_id}")

        if resolution.gate_status != "approved":
            raise ValueError(f"artifact_not_approved_for_signoff: {artifact_id}")

        record = ClinicalSignoffBindingRecord(
            id=str(uuid.uuid4()),
            tenant_id=artifact.tenant_id,
            case_id=artifact.case_id,
            artifact_type="vet_copilot",
            artifact_id=artifact_id,
            veterinarian_id=veterinarian_id,
            veterinarian_role=veterinarian_role,
            final_note_hash=self._hash_text(final_note_text.strip()),
            signoff_status="signed",
            signed_at=utc_now_iso(),
            immutable_after_signoff=True,
            ai_execution_authority=False,
        )
        return self.resolution_repository.save_signoff(record)

    def get_resolution(self, record_id: str) -> Optional[ApprovalResolutionRecord]:
        return self.resolution_repository.get_resolution(record_id)

    def list_case_resolutions(self, case_id: str) -> list[ApprovalResolutionRecord]:
        return self.resolution_repository.list_case_resolutions(case_id)

    def get_signoff(self, record_id: str) -> Optional[ClinicalSignoffBindingRecord]:
        return self.resolution_repository.get_signoff(record_id)

    def list_case_signoffs(self, case_id: str) -> list[ClinicalSignoffBindingRecord]:
        return self.resolution_repository.list_case_signoffs(case_id)


def build_default_ai_resolution_service() -> AIResolutionService:
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
    resolution_base_path = os.environ.get(
        "PETCARE_AI_RESOLUTION_DIR",
        "petcare_runtime/runtime_data/ai_resolution",
    )

    trace_repository = FileAITraceRepository(trace_base_path)
    hitl_repository = FileAIHITLRepository(hitl_base_path)
    runtime_repository = FileAIRuntimeRepository(runtime_base_path)
    resolution_repository = FileAIResolutionRepository(resolution_base_path)

    hitl_service = AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)

    return AIResolutionService(
        hitl_service=hitl_service,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
    )
