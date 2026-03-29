from __future__ import annotations

import os
import uuid
from typing import Optional

from petcare.ai_logging.repository import FileAITraceRepository

from .models import ApprovalDecisionRecord, ApprovalGateRecord, utc_now_iso
from .repository import FileAIHITLRepository


class AIHITLService:
    HIGH_RISK_FLAGS = {
        "contraindication",
        "dose_risk",
        "emergency_red_flag",
        "interaction",
        "review_required",
    }

    CONTEXT_ROLE_MAP = {
        "consultation": ["veterinarian"],
        "emergency": ["veterinarian"],
        "pharmacy": ["pharmacist", "veterinarian"],
        "ops": ["admin"],
        "triage": ["veterinarian"],
    }

    def __init__(
        self,
        trace_repository: FileAITraceRepository,
        hitl_repository: FileAIHITLRepository,
    ) -> None:
        self.trace_repository = trace_repository
        self.hitl_repository = hitl_repository

    def _classify_decision(self, *, context_type: str, requires_approval: bool, risk_flags: list[str]) -> str:
        normalized_flags = {flag.strip() for flag in risk_flags if flag and flag.strip()}
        if requires_approval or normalized_flags.intersection(self.HIGH_RISK_FLAGS):
            return "actionable"
        if context_type in {"consultation", "pharmacy", "emergency", "triage"}:
            return "assistive"
        return "informational"

    def _allowed_roles(self, context_type: str) -> list[str]:
        return self.CONTEXT_ROLE_MAP.get(context_type, ["admin"])

    def evaluate_output(self, output_id: str) -> ApprovalGateRecord:
        output_record = self.trace_repository.get_output(output_id)
        if output_record is None:
            raise ValueError(f"Unknown output_id: {output_id}")

        prompt_record = self.trace_repository.get_prompt(output_record.prompt_id)
        if prompt_record is None:
            raise ValueError(f"Prompt not found for output_id: {output_id}")

        decision_class = self._classify_decision(
            context_type=prompt_record.context_type,
            requires_approval=output_record.requires_approval,
            risk_flags=output_record.risk_flags,
        )

        requires_approval = decision_class == "actionable"
        status = "pending" if requires_approval else "not_required"
        now = utc_now_iso()

        existing = self.hitl_repository.get_gate(output_id)
        created_at = existing.created_at if existing is not None and existing.created_at else now

        record = ApprovalGateRecord(
            output_id=output_record.id,
            prompt_id=prompt_record.id,
            case_id=prompt_record.case_id,
            tenant_id=prompt_record.tenant_id,
            context_type=prompt_record.context_type,
            decision_class=decision_class,
            requires_approval=requires_approval,
            allowed_roles=self._allowed_roles(prompt_record.context_type),
            status=status if existing is None or existing.status == "not_required" else existing.status,
            created_at=created_at,
            updated_at=now,
            ai_execution_authority=False,
        )
        return self.hitl_repository.save_gate(record)

    def get_gate(self, output_id: str) -> Optional[ApprovalGateRecord]:
        return self.hitl_repository.get_gate(output_id)

    def decide_output(
        self,
        *,
        output_id: str,
        approver_id: str,
        approver_role: str,
        decision: str,
        reason_code: str,
        notes: Optional[str],
    ) -> ApprovalDecisionRecord:
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")

        gate = self.hitl_repository.get_gate(output_id)
        if gate is None:
            raise ValueError(f"Approval gate not found for output_id: {output_id}")

        if not gate.requires_approval:
            raise ValueError(f"Approval not required for output_id: {output_id}")

        if gate.status not in {"pending", "approved", "rejected"}:
            raise ValueError(f"Unsupported gate status for output_id: {output_id}")

        if approver_role not in gate.allowed_roles:
            raise ValueError(f"approver_role_not_allowed: {approver_role}")

        decision_record = ApprovalDecisionRecord(
            id=str(uuid.uuid4()),
            output_id=output_id,
            decision=decision,
            approver_id=approver_id,
            approver_role=approver_role,
            reason_code=reason_code,
            notes=notes,
            decided_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        self.hitl_repository.save_decision(decision_record)

        updated_gate = ApprovalGateRecord(
            output_id=gate.output_id,
            prompt_id=gate.prompt_id,
            case_id=gate.case_id,
            tenant_id=gate.tenant_id,
            context_type=gate.context_type,
            decision_class=gate.decision_class,
            requires_approval=gate.requires_approval,
            allowed_roles=gate.allowed_roles,
            status=decision,
            created_at=gate.created_at,
            updated_at=decision_record.decided_at,
            ai_execution_authority=False,
        )
        self.hitl_repository.save_gate(updated_gate)
        return decision_record

    def get_case_gates(self, case_id: str) -> list[ApprovalGateRecord]:
        return self.hitl_repository.list_case_gates(case_id)

    def get_output_decisions(self, output_id: str) -> list[ApprovalDecisionRecord]:
        return self.hitl_repository.list_output_decisions(output_id)


def build_default_hitl_service() -> AIHITLService:
    trace_base_path = os.environ.get(
        "PETCARE_AI_TRACE_DIR",
        "petcare_runtime/runtime_data/ai_logging",
    )
    hitl_base_path = os.environ.get(
        "PETCARE_AI_HITL_DIR",
        "petcare_runtime/runtime_data/ai_hitl",
    )
    trace_repository = FileAITraceRepository(trace_base_path)
    hitl_repository = FileAIHITLRepository(hitl_base_path)
    return AIHITLService(trace_repository=trace_repository, hitl_repository=hitl_repository)
