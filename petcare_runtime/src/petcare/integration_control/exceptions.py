from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExceptionStatus(str, Enum):
    OPEN = "open"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass(frozen=True)
class EscalationRecord:
    escalation_id: str
    escalated_by: str
    escalated_at: str
    escalation_target: str
    reason: str

    def __post_init__(self) -> None:
        if not self.escalation_id:
            raise ValueError("escalation_id is required")
        if not self.escalated_by:
            raise ValueError("escalated_by is required")
        if not self.escalated_at:
            raise ValueError("escalated_at is required")
        if not self.escalation_target:
            raise ValueError("escalation_target is required")
        if not self.reason:
            raise ValueError("reason is required")


@dataclass(frozen=True)
class ExceptionCase:
    case_id: str
    subject_id: str
    status: ExceptionStatus
    opened_at: str
    opened_by: str
    reason: str
    escalation: EscalationRecord | None = None
    resolved_at: str | None = None
    resolved_by: str | None = None

    def __post_init__(self) -> None:
        if not self.case_id:
            raise ValueError("case_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.opened_at:
            raise ValueError("opened_at is required")
        if not self.opened_by:
            raise ValueError("opened_by is required")
        if not self.reason:
            raise ValueError("reason is required")


def create_exception_case(
    case_id: str,
    subject_id: str,
    opened_at: str,
    opened_by: str,
    reason: str,
) -> ExceptionCase:
    return ExceptionCase(
        case_id=case_id,
        subject_id=subject_id,
        status=ExceptionStatus.OPEN,
        opened_at=opened_at,
        opened_by=opened_by,
        reason=reason,
    )


def escalate_exception_case(
    case: ExceptionCase,
    escalation: EscalationRecord,
) -> ExceptionCase:
    if case.status != ExceptionStatus.OPEN:
        raise ValueError("only open exceptions can be escalated")
    return ExceptionCase(
        case_id=case.case_id,
        subject_id=case.subject_id,
        status=ExceptionStatus.ESCALATED,
        opened_at=case.opened_at,
        opened_by=case.opened_by,
        reason=case.reason,
        escalation=escalation,
        resolved_at=case.resolved_at,
        resolved_by=case.resolved_by,
    )


def resolve_exception_case(
    case: ExceptionCase,
    resolved_at: str,
    resolved_by: str,
) -> ExceptionCase:
    if case.status not in {ExceptionStatus.OPEN, ExceptionStatus.ESCALATED}:
        raise ValueError("exception cannot be resolved from current state")
    return ExceptionCase(
        case_id=case.case_id,
        subject_id=case.subject_id,
        status=ExceptionStatus.RESOLVED,
        opened_at=case.opened_at,
        opened_by=case.opened_by,
        reason=case.reason,
        escalation=case.escalation,
        resolved_at=resolved_at,
        resolved_by=resolved_by,
    )
