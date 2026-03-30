from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionSafeguardState(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass(frozen=True)
class PauseRecord:
    execution_id: str
    paused_at: str
    paused_by: str
    reason: str


@dataclass(frozen=True)
class FailureRecord:
    execution_id: str
    failed_at: str
    failure_code: str
    reason: str


@dataclass(frozen=True)
class RetryRecord:
    execution_id: str
    retried_at: str
    retried_by: str
    reason: str


def pause_execution(
    execution_id: str,
    paused_at: str,
    paused_by: str,
    reason: str,
) -> tuple[ExecutionSafeguardState, PauseRecord]:
    return (
        ExecutionSafeguardState.PAUSED,
        PauseRecord(
            execution_id=execution_id,
            paused_at=paused_at,
            paused_by=paused_by,
            reason=reason,
        ),
    )


def cancel_execution(execution_id: str) -> ExecutionSafeguardState:
    return ExecutionSafeguardState.CANCELLED


def retry_execution(
    execution_id: str,
    retried_at: str,
    retried_by: str,
    reason: str,
) -> tuple[ExecutionSafeguardState, RetryRecord]:
    return (
        ExecutionSafeguardState.RETRYING,
        RetryRecord(
            execution_id=execution_id,
            retried_at=retried_at,
            retried_by=retried_by,
            reason=reason,
        ),
    )


def fail_execution(
    execution_id: str,
    failed_at: str,
    failure_code: str,
    reason: str,
) -> tuple[ExecutionSafeguardState, FailureRecord]:
    return (
        ExecutionSafeguardState.FAILED,
        FailureRecord(
            execution_id=execution_id,
            failed_at=failed_at,
            failure_code=failure_code,
            reason=reason,
        ),
    )
