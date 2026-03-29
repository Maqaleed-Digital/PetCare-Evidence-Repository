from __future__ import annotations

import os
import uuid
from typing import Iterable, Optional

from .models import DriftSnapshotRecord, EvalCaseRecord, EvalRunRecord, utc_now_iso
from .repository import FileAIEvalRepository


class AIEvalService:
    DEFAULT_THRESHOLDS = {
        "max_pass_rate_drop": 0.05,
        "max_approval_alignment_drop": 0.05,
        "max_risk_flag_alignment_drop": 0.05,
        "min_regression_threshold_pass_rate": 0.90,
    }

    def __init__(self, repository: FileAIEvalRepository) -> None:
        self.repository = repository

    def register_eval_case(
        self,
        *,
        species: str,
        symptom_cluster: str,
        context_type: str,
        expected_risk_flags: Iterable[str],
        expected_requires_approval: bool,
        expected_decision_class: str,
    ) -> EvalCaseRecord:
        record = EvalCaseRecord(
            id=str(uuid.uuid4()),
            species=species,
            symptom_cluster=symptom_cluster,
            context_type=context_type,
            expected_risk_flags=sorted({flag.strip() for flag in expected_risk_flags if flag and flag.strip()}),
            expected_requires_approval=expected_requires_approval,
            expected_decision_class=expected_decision_class,
            status="active",
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.repository.save_case(record)

    def run_evaluation(
        self,
        *,
        suite_name: str,
        suite_version: str,
        model_name: str,
        model_version: str,
        provider: str,
        case_results: list[dict],
        regression_threshold_pass_rate: float,
    ) -> EvalRunRecord:
        total_cases = len(case_results)
        if total_cases == 0:
            raise ValueError("case_results must not be empty")

        passed_cases = sum(1 for item in case_results if item.get("passed") is True)
        approval_matches = sum(1 for item in case_results if item.get("approval_aligned") is True)
        risk_flag_matches = sum(1 for item in case_results if item.get("risk_flag_aligned") is True)

        pass_rate = passed_cases / total_cases
        approval_alignment_rate = approval_matches / total_cases
        risk_flag_alignment_rate = risk_flag_matches / total_cases

        min_required = self.DEFAULT_THRESHOLDS["min_regression_threshold_pass_rate"]
        status = "pass" if pass_rate >= regression_threshold_pass_rate and pass_rate >= min_required else "fail"

        record = EvalRunRecord(
            id=str(uuid.uuid4()),
            suite_name=suite_name,
            suite_version=suite_version,
            model_name=model_name,
            model_version=model_version,
            provider=provider,
            total_cases=total_cases,
            passed_cases=passed_cases,
            pass_rate=round(pass_rate, 6),
            approval_alignment_rate=round(approval_alignment_rate, 6),
            risk_flag_alignment_rate=round(risk_flag_alignment_rate, 6),
            regression_threshold_pass_rate=regression_threshold_pass_rate,
            status=status,
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.repository.save_run(record)

    def record_drift_snapshot(
        self,
        *,
        model_name: str,
        model_version: str,
        provider: str,
        baseline_pass_rate: float,
        current_pass_rate: float,
        baseline_approval_alignment_rate: float,
        current_approval_alignment_rate: float,
        baseline_risk_flag_alignment_rate: float,
        current_risk_flag_alignment_rate: float,
        thresholds: Optional[dict[str, float]] = None,
    ) -> DriftSnapshotRecord:
        effective_thresholds = dict(self.DEFAULT_THRESHOLDS)
        if thresholds:
            effective_thresholds.update(thresholds)

        pass_rate_delta = round(current_pass_rate - baseline_pass_rate, 6)
        approval_alignment_delta = round(current_approval_alignment_rate - baseline_approval_alignment_rate, 6)
        risk_flag_alignment_delta = round(current_risk_flag_alignment_rate - baseline_risk_flag_alignment_rate, 6)

        alert_status = "stable"
        if (
            pass_rate_delta < -effective_thresholds["max_pass_rate_drop"]
            or approval_alignment_delta < -effective_thresholds["max_approval_alignment_drop"]
            or risk_flag_alignment_delta < -effective_thresholds["max_risk_flag_alignment_drop"]
        ):
            alert_status = "alert"

        record = DriftSnapshotRecord(
            id=str(uuid.uuid4()),
            model_name=model_name,
            model_version=model_version,
            provider=provider,
            baseline_pass_rate=baseline_pass_rate,
            current_pass_rate=current_pass_rate,
            baseline_approval_alignment_rate=baseline_approval_alignment_rate,
            current_approval_alignment_rate=current_approval_alignment_rate,
            baseline_risk_flag_alignment_rate=baseline_risk_flag_alignment_rate,
            current_risk_flag_alignment_rate=current_risk_flag_alignment_rate,
            pass_rate_delta=pass_rate_delta,
            approval_alignment_delta=approval_alignment_delta,
            risk_flag_alignment_delta=risk_flag_alignment_delta,
            alert_status=alert_status,
            thresholds=effective_thresholds,
            created_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.repository.save_drift_snapshot(record)

    def get_case(self, case_id: str) -> Optional[EvalCaseRecord]:
        return self.repository.get_case(case_id)

    def list_cases(self) -> list[EvalCaseRecord]:
        return self.repository.list_cases()

    def get_run(self, run_id: str) -> Optional[EvalRunRecord]:
        return self.repository.get_run(run_id)

    def list_runs(self) -> list[EvalRunRecord]:
        return self.repository.list_runs()

    def get_drift_snapshot(self, snapshot_id: str) -> Optional[DriftSnapshotRecord]:
        return self.repository.get_drift_snapshot(snapshot_id)

    def list_drift_snapshots(self) -> list[DriftSnapshotRecord]:
        return self.repository.list_drift_snapshots()


def build_default_eval_service() -> AIEvalService:
    base_path = os.environ.get(
        "PETCARE_AI_EVAL_DIR",
        "petcare_runtime/runtime_data/ai_eval",
    )
    repository = FileAIEvalRepository(base_path)
    return AIEvalService(repository)
