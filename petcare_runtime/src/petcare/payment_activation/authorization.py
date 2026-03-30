from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuthorizationStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    DUAL_AUTHORIZED = "dual_authorized"


class ExecutionClass(str, Enum):
    STANDARD = "standard"
    HIGH_VALUE = "high_value"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AuthorizationRecord:
    authorization_id: str
    execution_id: str
    execution_class: ExecutionClass
    status: AuthorizationStatus
    approved_by: str
    approved_at: str
    reason: str
    second_approved_by: str | None = None
    second_approved_at: str | None = None

    def __post_init__(self) -> None:
        if not self.authorization_id:
            raise ValueError("authorization_id is required")
        if not self.execution_id:
            raise ValueError("execution_id is required")
        if not self.approved_by:
            raise ValueError("approved_by is required")
        if not self.approved_at:
            raise ValueError("approved_at is required")
        if not self.reason:
            raise ValueError("reason is required")


def authorize_execution(
    authorization_id: str,
    execution_id: str,
    execution_class: ExecutionClass,
    approved_by: str,
    approved_at: str,
    reason: str,
) -> AuthorizationRecord:
    return AuthorizationRecord(
        authorization_id=authorization_id,
        execution_id=execution_id,
        execution_class=execution_class,
        status=AuthorizationStatus.AUTHORIZED,
        approved_by=approved_by,
        approved_at=approved_at,
        reason=reason,
    )


def add_second_authorization(
    record: AuthorizationRecord,
    second_approved_by: str,
    second_approved_at: str,
) -> AuthorizationRecord:
    if record.execution_class not in {ExecutionClass.HIGH_VALUE, ExecutionClass.CRITICAL}:
        raise ValueError("dual authorization not required for this execution class")
    return AuthorizationRecord(
        authorization_id=record.authorization_id,
        execution_id=record.execution_id,
        execution_class=record.execution_class,
        status=AuthorizationStatus.DUAL_AUTHORIZED,
        approved_by=record.approved_by,
        approved_at=record.approved_at,
        reason=record.reason,
        second_approved_by=second_approved_by,
        second_approved_at=second_approved_at,
    )
