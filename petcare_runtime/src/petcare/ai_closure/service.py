from __future__ import annotations

import hashlib
import json
import os
import uuid

from petcare.ai_dashboard.service import AIDashboardService
from petcare.ai_eval.repository import FileAIEvalRepository
from petcare.ai_evidence.repository import FileAIEvidenceRepository
from petcare.ai_hitl.repository import FileAIHITLRepository
from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_resolution.repository import FileAIResolutionRepository
from petcare.ai_runtime.repository import FileAIRuntimeRepository

from .models import EPClosureChecklistRecord, EPGovernanceSealRecord, utc_now_iso
from .repository import FileAIClosureRepository


class AIClosureService:
    def __init__(
        self,
        trace_repository: FileAITraceRepository,
        hitl_repository: FileAIHITLRepository,
        eval_repository: FileAIEvalRepository,
        runtime_repository: FileAIRuntimeRepository,
        resolution_repository: FileAIResolutionRepository,
        evidence_repository: FileAIEvidenceRepository,
        closure_repository: FileAIClosureRepository,
        dashboard_service: AIDashboardService,
    ) -> None:
        self.trace_repository = trace_repository
        self.hitl_repository = hitl_repository
        self.eval_repository = eval_repository
        self.runtime_repository = runtime_repository
        self.resolution_repository = resolution_repository
        self.evidence_repository = evidence_repository
        self.closure_repository = closure_repository
        self.dashboard_service = dashboard_service

    def _sha256(self, payload: dict) -> str:
        content = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def generate_ep_closure_checklist(self, *, tenant_id: str, epic_id: str = "EP-05") -> EPClosureChecklistRecord:
        overview = self.dashboard_service.get_governance_overview(tenant_id)

        has_logging_foundation = overview.total_prompt_logs > 0 and overview.total_output_logs > 0
        has_hitl_foundation = (overview.total_pending_gates + overview.total_approved_gates + overview.total_rejected_gates) > 0
        has_eval_foundation = overview.total_eval_runs > 0
        has_runtime_activation = (overview.total_ai_intake_records + overview.total_vet_copilot_records) > 0
        has_resolution_binding = (overview.total_resolutions + overview.total_signoffs) > 0
        has_dashboard_read_models = True
        has_evidence_exports = len(list(self.evidence_repository.exports_dir.glob("*.json"))) > 0
        has_governance_reports = len(self.evidence_repository.list_reports()) > 0
        has_no_pending_gates = overview.total_pending_gates == 0
        has_no_drift_alerts = overview.total_drift_alerts == 0

        seal_ready = all([
            has_logging_foundation,
            has_hitl_foundation,
            has_eval_foundation,
            has_runtime_activation,
            has_resolution_binding,
            has_dashboard_read_models,
            has_evidence_exports,
            has_governance_reports,
            has_no_pending_gates,
            has_no_drift_alerts,
        ])

        record = EPClosureChecklistRecord(
            tenant_id=tenant_id,
            epic_id=epic_id,
            has_logging_foundation=has_logging_foundation,
            has_hitl_foundation=has_hitl_foundation,
            has_eval_foundation=has_eval_foundation,
            has_runtime_activation=has_runtime_activation,
            has_resolution_binding=has_resolution_binding,
            has_dashboard_read_models=has_dashboard_read_models,
            has_evidence_exports=has_evidence_exports,
            has_governance_reports=has_governance_reports,
            has_no_pending_gates=has_no_pending_gates,
            has_no_drift_alerts=has_no_drift_alerts,
            seal_ready=seal_ready,
            generated_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.closure_repository.save_checklist(record)

    def seal_epic(
        self,
        *,
        tenant_id: str,
        epic_id: str,
        source_commit: str,
        sealed_by: str,
    ) -> EPGovernanceSealRecord:
        existing = self.closure_repository.find_seal(tenant_id, epic_id)
        if existing is not None:
            raise ValueError(f"epic_already_sealed: {epic_id}")

        checklist = self.generate_ep_closure_checklist(tenant_id=tenant_id, epic_id=epic_id)
        if not checklist.seal_ready:
            raise ValueError("closure_checklist_not_ready")

        checklist_payload = {
            "tenant_id": checklist.tenant_id,
            "epic_id": checklist.epic_id,
            "has_logging_foundation": checklist.has_logging_foundation,
            "has_hitl_foundation": checklist.has_hitl_foundation,
            "has_eval_foundation": checklist.has_eval_foundation,
            "has_runtime_activation": checklist.has_runtime_activation,
            "has_resolution_binding": checklist.has_resolution_binding,
            "has_dashboard_read_models": checklist.has_dashboard_read_models,
            "has_evidence_exports": checklist.has_evidence_exports,
            "has_governance_reports": checklist.has_governance_reports,
            "has_no_pending_gates": checklist.has_no_pending_gates,
            "has_no_drift_alerts": checklist.has_no_drift_alerts,
            "seal_ready": checklist.seal_ready,
        }

        record = EPGovernanceSealRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            epic_id=epic_id,
            seal_status="sealed",
            checklist_hash=self._sha256(checklist_payload),
            source_commit=source_commit,
            sealed_by=sealed_by,
            sealed_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.closure_repository.save_seal(record)

    def get_checklist(self, tenant_id: str, epic_id: str) -> EPClosureChecklistRecord | None:
        return self.closure_repository.get_checklist(tenant_id, epic_id)

    def get_seal(self, record_id: str) -> EPGovernanceSealRecord | None:
        return self.closure_repository.get_seal(record_id)

    def list_seals(self) -> list[EPGovernanceSealRecord]:
        return self.closure_repository.list_seals()


def build_default_ai_closure_service() -> AIClosureService:
    trace_base_path = os.environ.get(
        "PETCARE_AI_TRACE_DIR",
        "petcare_runtime/runtime_data/ai_logging",
    )
    hitl_base_path = os.environ.get(
        "PETCARE_AI_HITL_DIR",
        "petcare_runtime/runtime_data/ai_hitl",
    )
    eval_base_path = os.environ.get(
        "PETCARE_AI_EVAL_DIR",
        "petcare_runtime/runtime_data/ai_eval",
    )
    runtime_base_path = os.environ.get(
        "PETCARE_AI_RUNTIME_DIR",
        "petcare_runtime/runtime_data/ai_runtime",
    )
    resolution_base_path = os.environ.get(
        "PETCARE_AI_RESOLUTION_DIR",
        "petcare_runtime/runtime_data/ai_resolution",
    )
    evidence_base_path = os.environ.get(
        "PETCARE_AI_EVIDENCE_DIR",
        "petcare_runtime/runtime_data/ai_evidence",
    )
    closure_base_path = os.environ.get(
        "PETCARE_AI_CLOSURE_DIR",
        "petcare_runtime/runtime_data/ai_closure",
    )

    trace_repository = FileAITraceRepository(trace_base_path)
    hitl_repository = FileAIHITLRepository(hitl_base_path)
    eval_repository = FileAIEvalRepository(eval_base_path)
    runtime_repository = FileAIRuntimeRepository(runtime_base_path)
    resolution_repository = FileAIResolutionRepository(resolution_base_path)
    evidence_repository = FileAIEvidenceRepository(evidence_base_path)
    closure_repository = FileAIClosureRepository(closure_base_path)

    dashboard_service = AIDashboardService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
    )

    return AIClosureService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
        evidence_repository=evidence_repository,
        closure_repository=closure_repository,
        dashboard_service=dashboard_service,
    )
