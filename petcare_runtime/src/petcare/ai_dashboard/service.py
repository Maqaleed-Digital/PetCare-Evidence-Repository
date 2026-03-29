from __future__ import annotations

import os

from petcare.ai_eval.repository import FileAIEvalRepository
from petcare.ai_hitl.repository import FileAIHITLRepository
from petcare.ai_logging.repository import FileAITraceRepository
from petcare.ai_resolution.repository import FileAIResolutionRepository
from petcare.ai_runtime.repository import FileAIRuntimeRepository

from .models import CaseGovernanceViewRecord, GovernanceOverviewRecord, OperationalAlertRecord, utc_now_iso


class AIDashboardService:
    def __init__(
        self,
        trace_repository: FileAITraceRepository,
        hitl_repository: FileAIHITLRepository,
        eval_repository: FileAIEvalRepository,
        runtime_repository: FileAIRuntimeRepository,
        resolution_repository: FileAIResolutionRepository,
    ) -> None:
        self.trace_repository = trace_repository
        self.hitl_repository = hitl_repository
        self.eval_repository = eval_repository
        self.runtime_repository = runtime_repository
        self.resolution_repository = resolution_repository

    def get_governance_overview(self, tenant_id: str) -> GovernanceOverviewRecord:
        prompts = [
            item for item in self.trace_repository.prompts_dir.glob("*.json")
            if self.trace_repository._read_json(item).get("tenant_id") == tenant_id
        ]
        prompt_payloads = [self.trace_repository._read_json(path) for path in prompts]
        prompt_ids = {payload["id"] for payload in prompt_payloads}

        outputs = [
            self.trace_repository._read_json(path)
            for path in self.trace_repository.outputs_dir.glob("*.json")
            if self.trace_repository._read_json(path).get("prompt_id") in prompt_ids
        ]

        gates = [
            self.hitl_repository._read_json(path)
            for path in self.hitl_repository.gates_dir.glob("*.json")
            if self.hitl_repository._read_json(path).get("tenant_id") == tenant_id
        ]

        eval_runs = list(self.eval_repository.list_runs())
        drift_snapshots = list(self.eval_repository.list_drift_snapshots())

        intake_records = [
            self.runtime_repository._read_json(path)
            for path in self.runtime_repository.intake_dir.glob("*.json")
            if self.runtime_repository._read_json(path).get("tenant_id") == tenant_id
        ]
        copilot_records = [
            self.runtime_repository._read_json(path)
            for path in self.runtime_repository.copilot_dir.glob("*.json")
            if self.runtime_repository._read_json(path).get("tenant_id") == tenant_id
        ]

        resolutions = [
            self.resolution_repository._read_json(path)
            for path in self.resolution_repository.resolutions_dir.glob("*.json")
            if self.resolution_repository._read_json(path).get("tenant_id") == tenant_id
        ]
        signoffs = [
            self.resolution_repository._read_json(path)
            for path in self.resolution_repository.signoffs_dir.glob("*.json")
            if self.resolution_repository._read_json(path).get("tenant_id") == tenant_id
        ]

        return GovernanceOverviewRecord(
            tenant_id=tenant_id,
            total_prompt_logs=len(prompt_payloads),
            total_output_logs=len(outputs),
            total_pending_gates=sum(1 for item in gates if item.get("status") == "pending"),
            total_approved_gates=sum(1 for item in gates if item.get("status") == "approved"),
            total_rejected_gates=sum(1 for item in gates if item.get("status") == "rejected"),
            total_eval_runs=len(eval_runs),
            total_drift_alerts=sum(1 for item in drift_snapshots if item.alert_status == "alert"),
            total_ai_intake_records=len(intake_records),
            total_vet_copilot_records=len(copilot_records),
            total_resolutions=len(resolutions),
            total_signoffs=len(signoffs),
            generated_at=utc_now_iso(),
            ai_execution_authority=False,
        )

    def list_operational_alerts(self, tenant_id: str) -> list[OperationalAlertRecord]:
        alerts: list[OperationalAlertRecord] = []

        for gate in self.hitl_repository.gates_dir.glob("*.json"):
            payload = self.hitl_repository._read_json(gate)
            if payload.get("tenant_id") != tenant_id:
                continue
            if payload.get("status") == "pending":
                alerts.append(
                    OperationalAlertRecord(
                        tenant_id=tenant_id,
                        category="hitl_gate",
                        severity="high",
                        reference_id=payload["output_id"],
                        case_id=payload["case_id"],
                        message=f"Pending HITL approval for output {payload['output_id']}",
                        generated_at=utc_now_iso(),
                        ai_execution_authority=False,
                    )
                )

        for snapshot in self.eval_repository.list_drift_snapshots():
            if snapshot.alert_status == "alert":
                alerts.append(
                    OperationalAlertRecord(
                        tenant_id=tenant_id,
                        category="drift_alert",
                        severity="high",
                        reference_id=snapshot.id,
                        case_id="global",
                        message=f"Drift alert for {snapshot.provider}/{snapshot.model_name}/{snapshot.model_version}",
                        generated_at=utc_now_iso(),
                        ai_execution_authority=False,
                    )
                )

        for path in self.runtime_repository.copilot_dir.glob("*.json"):
            payload = self.runtime_repository._read_json(path)
            if payload.get("tenant_id") != tenant_id:
                continue
            artifact_id = payload["id"]
            signoff = self.resolution_repository.find_signoff_for_artifact("vet_copilot", artifact_id)
            if payload.get("hitl_required") and signoff is None:
                alerts.append(
                    OperationalAlertRecord(
                        tenant_id=tenant_id,
                        category="clinical_signoff",
                        severity="medium",
                        reference_id=artifact_id,
                        case_id=payload["case_id"],
                        message=f"Vet copilot artifact {artifact_id} requires sign-off binding",
                        generated_at=utc_now_iso(),
                        ai_execution_authority=False,
                    )
                )

        return alerts

    def get_case_governance_view(self, tenant_id: str, case_id: str) -> CaseGovernanceViewRecord:
        prompts = self.trace_repository.list_case_prompts(case_id)
        prompt_ids = {item.id for item in prompts}

        outputs = [
            self.trace_repository._read_json(path)
            for path in self.trace_repository.outputs_dir.glob("*.json")
            if self.trace_repository._read_json(path).get("prompt_id") in prompt_ids
        ]
        output_ids = [item["id"] for item in outputs]

        gates = [
            self.hitl_repository._read_json(path)
            for path in self.hitl_repository.gates_dir.glob("*.json")
            if self.hitl_repository._read_json(path).get("case_id") == case_id
            and self.hitl_repository._read_json(path).get("tenant_id") == tenant_id
        ]

        intake_records = [
            self.runtime_repository._read_json(path)
            for path in self.runtime_repository.intake_dir.glob("*.json")
            if self.runtime_repository._read_json(path).get("case_id") == case_id
            and self.runtime_repository._read_json(path).get("tenant_id") == tenant_id
        ]
        copilot_records = [
            self.runtime_repository._read_json(path)
            for path in self.runtime_repository.copilot_dir.glob("*.json")
            if self.runtime_repository._read_json(path).get("case_id") == case_id
            and self.runtime_repository._read_json(path).get("tenant_id") == tenant_id
        ]

        resolutions = [
            self.resolution_repository._read_json(path)
            for path in self.resolution_repository.resolutions_dir.glob("*.json")
            if self.resolution_repository._read_json(path).get("case_id") == case_id
            and self.resolution_repository._read_json(path).get("tenant_id") == tenant_id
        ]
        signoffs = [
            self.resolution_repository._read_json(path)
            for path in self.resolution_repository.signoffs_dir.glob("*.json")
            if self.resolution_repository._read_json(path).get("case_id") == case_id
            and self.resolution_repository._read_json(path).get("tenant_id") == tenant_id
        ]

        drift_snapshots = self.eval_repository.list_drift_snapshots()
        latest_drift_alert_status = drift_snapshots[-1].alert_status if drift_snapshots else "none"

        gate_statuses = [item["status"] for item in gates]
        if any(status == "pending" for status in gate_statuses):
            governance_state = "awaiting_review"
        elif copilot_records and not signoffs:
            governance_state = "awaiting_signoff"
        elif resolutions or signoffs:
            governance_state = "resolved"
        else:
            governance_state = "tracked"

        return CaseGovernanceViewRecord(
            tenant_id=tenant_id,
            case_id=case_id,
            prompt_log_ids=sorted([item.id for item in prompts]),
            output_log_ids=sorted(output_ids),
            gate_statuses=sorted(gate_statuses),
            runtime_artifact_ids=sorted([item["id"] for item in intake_records + copilot_records]),
            resolution_ids=sorted([item["id"] for item in resolutions]),
            signoff_ids=sorted([item["id"] for item in signoffs]),
            latest_drift_alert_status=latest_drift_alert_status,
            governance_state=governance_state,
            generated_at=utc_now_iso(),
            ai_execution_authority=False,
        )


def build_default_ai_dashboard_service() -> AIDashboardService:
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

    return AIDashboardService(
        trace_repository=FileAITraceRepository(trace_base_path),
        hitl_repository=FileAIHITLRepository(hitl_base_path),
        eval_repository=FileAIEvalRepository(eval_base_path),
        runtime_repository=FileAIRuntimeRepository(runtime_base_path),
        resolution_repository=FileAIResolutionRepository(resolution_base_path),
    )
