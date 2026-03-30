from __future__ import annotations

import hashlib
import json
import os
import uuid
from typing import Dict, List

from petcare.ai_dashboard.service import AIDashboardService
from petcare.ai_eval.repository import FileAIEvalRepository
from petcare.ai_hitl.repository import FileAIHITLRepository
from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_resolution.repository import FileAIResolutionRepository
from petcare.ai_runtime.repository import FileAIRuntimeRepository

from .models import EvidenceExportRecord, GovernanceReportRecord, utc_now_iso
from .repository import FileAIEvidenceRepository


class AIEvidenceService:
    def __init__(
        self,
        trace_repository: FileAITraceRepository,
        hitl_repository: FileAIHITLRepository,
        eval_repository: FileAIEvalRepository,
        runtime_repository: FileAIRuntimeRepository,
        resolution_repository: FileAIResolutionRepository,
        evidence_repository: FileAIEvidenceRepository,
        dashboard_service: AIDashboardService,
    ) -> None:
        self.trace_repository = trace_repository
        self.hitl_repository = hitl_repository
        self.eval_repository = eval_repository
        self.runtime_repository = runtime_repository
        self.resolution_repository = resolution_repository
        self.evidence_repository = evidence_repository
        self.dashboard_service = dashboard_service

    def _sha256(self, payload: dict) -> str:
        content = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def _case_prompt_ids(self, case_id: str) -> List[str]:
        return sorted([item.id for item in self.trace_repository.list_case_prompts(case_id)])

    def _case_output_ids(self, case_id: str) -> List[str]:
        prompt_ids = set(self._case_prompt_ids(case_id))
        output_ids: List[str] = []
        for path in self.trace_repository.outputs_dir.glob("*.json"):
            payload = self.trace_repository._read_json(path)
            if payload.get("prompt_id") in prompt_ids:
                output_ids.append(payload["id"])
        return sorted(output_ids)

    def _case_gate_ids(self, tenant_id: str, case_id: str) -> List[str]:
        gate_ids: List[str] = []
        for path in self.hitl_repository.gates_dir.glob("*.json"):
            payload = self.hitl_repository._read_json(path)
            if payload.get("tenant_id") == tenant_id and payload.get("case_id") == case_id:
                gate_ids.append(payload["output_id"])
        return sorted(gate_ids)

    def _case_runtime_artifact_ids(self, tenant_id: str, case_id: str) -> List[str]:
        artifact_ids: List[str] = []
        for path in self.runtime_repository.intake_dir.glob("*.json"):
            payload = self.runtime_repository._read_json(path)
            if payload.get("tenant_id") == tenant_id and payload.get("case_id") == case_id:
                artifact_ids.append(payload["id"])
        for path in self.runtime_repository.copilot_dir.glob("*.json"):
            payload = self.runtime_repository._read_json(path)
            if payload.get("tenant_id") == tenant_id and payload.get("case_id") == case_id:
                artifact_ids.append(payload["id"])
        return sorted(artifact_ids)

    def _case_resolution_ids(self, tenant_id: str, case_id: str) -> List[str]:
        ids: List[str] = []
        for path in self.resolution_repository.resolutions_dir.glob("*.json"):
            payload = self.resolution_repository._read_json(path)
            if payload.get("tenant_id") == tenant_id and payload.get("case_id") == case_id:
                ids.append(payload["id"])
        return sorted(ids)

    def _case_signoff_ids(self, tenant_id: str, case_id: str) -> List[str]:
        ids: List[str] = []
        for path in self.resolution_repository.signoffs_dir.glob("*.json"):
            payload = self.resolution_repository._read_json(path)
            if payload.get("tenant_id") == tenant_id and payload.get("case_id") == case_id:
                ids.append(payload["id"])
        return sorted(ids)

    def export_case_evidence(self, *, tenant_id: str, case_id: str, export_type: str = "case_governance_pack") -> EvidenceExportRecord:
        case_view = self.dashboard_service.get_case_governance_view(tenant_id, case_id)
        report = self.generate_governance_report(
            tenant_id=tenant_id,
            scope_type="case",
            scope_id=case_id,
        )

        manifest = {
            "tenant_id": tenant_id,
            "case_id": case_id,
            "export_type": export_type,
            "prompt_log_ids": case_view.prompt_log_ids,
            "output_log_ids": case_view.output_log_ids,
            "gate_statuses": case_view.gate_statuses,
            "runtime_artifact_ids": case_view.runtime_artifact_ids,
            "resolution_ids": case_view.resolution_ids,
            "signoff_ids": case_view.signoff_ids,
            "report_id": report.id,
            "governance_state": case_view.governance_state,
        }

        record = EvidenceExportRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            case_id=case_id,
            export_type=export_type,
            prompt_log_ids=self._case_prompt_ids(case_id),
            output_log_ids=self._case_output_ids(case_id),
            gate_ids=self._case_gate_ids(tenant_id, case_id),
            runtime_artifact_ids=self._case_runtime_artifact_ids(tenant_id, case_id),
            resolution_ids=self._case_resolution_ids(tenant_id, case_id),
            signoff_ids=self._case_signoff_ids(tenant_id, case_id),
            report_id=report.id,
            manifest_hash=self._sha256(manifest),
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.evidence_repository.save_export(record)

    def generate_governance_report(self, *, tenant_id: str, scope_type: str, scope_id: str) -> GovernanceReportRecord:
        if scope_type == "tenant":
            overview = self.dashboard_service.get_governance_overview(tenant_id)
            summary_counts: Dict[str, int] = {
                "total_prompt_logs": overview.total_prompt_logs,
                "total_output_logs": overview.total_output_logs,
                "total_pending_gates": overview.total_pending_gates,
                "total_approved_gates": overview.total_approved_gates,
                "total_rejected_gates": overview.total_rejected_gates,
                "total_eval_runs": overview.total_eval_runs,
                "total_drift_alerts": overview.total_drift_alerts,
                "total_ai_intake_records": overview.total_ai_intake_records,
                "total_vet_copilot_records": overview.total_vet_copilot_records,
                "total_resolutions": overview.total_resolutions,
                "total_signoffs": overview.total_signoffs,
            }
            risk_summary = {
                "pending_gates": overview.total_pending_gates,
                "drift_alerts": overview.total_drift_alerts,
                "rejected_gates": overview.total_rejected_gates,
            }
            governance_state = "attention_required" if overview.total_pending_gates or overview.total_drift_alerts else "stable"
        elif scope_type == "case":
            case_view = self.dashboard_service.get_case_governance_view(tenant_id, scope_id)
            summary_counts = {
                "prompt_logs": len(case_view.prompt_log_ids),
                "output_logs": len(case_view.output_log_ids),
                "gate_statuses": len(case_view.gate_statuses),
                "runtime_artifacts": len(case_view.runtime_artifact_ids),
                "resolutions": len(case_view.resolution_ids),
                "signoffs": len(case_view.signoff_ids),
            }
            risk_summary = {
                "pending_gates": sum(1 for status in case_view.gate_statuses if status == "pending"),
                "approved_gates": sum(1 for status in case_view.gate_statuses if status == "approved"),
                "rejected_gates": sum(1 for status in case_view.gate_statuses if status == "rejected"),
            }
            governance_state = case_view.governance_state
        else:
            raise ValueError("unsupported_scope_type")

        payload = {
            "tenant_id": tenant_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "summary_counts": summary_counts,
            "risk_summary": risk_summary,
            "governance_state": governance_state,
        }

        record = GovernanceReportRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            scope_type=scope_type,
            scope_id=scope_id,
            summary_counts=summary_counts,
            risk_summary=risk_summary,
            governance_state=governance_state,
            report_hash=self._sha256(payload),
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.evidence_repository.save_report(record)

    def get_export(self, record_id: str) -> EvidenceExportRecord | None:
        return self.evidence_repository.get_export(record_id)

    def list_case_exports(self, case_id: str) -> list[EvidenceExportRecord]:
        return self.evidence_repository.list_case_exports(case_id)

    def get_report(self, record_id: str) -> GovernanceReportRecord | None:
        return self.evidence_repository.get_report(record_id)

    def list_reports(self) -> list[GovernanceReportRecord]:
        return self.evidence_repository.list_reports()


def build_default_ai_evidence_service() -> AIEvidenceService:
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

    trace_repository = FileAITraceRepository(trace_base_path)
    hitl_repository = FileAIHITLRepository(hitl_base_path)
    eval_repository = FileAIEvalRepository(eval_base_path)
    runtime_repository = FileAIRuntimeRepository(runtime_base_path)
    resolution_repository = FileAIResolutionRepository(resolution_base_path)
    evidence_repository = FileAIEvidenceRepository(evidence_base_path)

    dashboard_service = AIDashboardService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
    )

    return AIEvidenceService(
        trace_repository=trace_repository,
        hitl_repository=hitl_repository,
        eval_repository=eval_repository,
        runtime_repository=runtime_repository,
        resolution_repository=resolution_repository,
        evidence_repository=evidence_repository,
        dashboard_service=dashboard_service,
    )
