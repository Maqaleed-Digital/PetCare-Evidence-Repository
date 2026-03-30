from dataclasses import dataclass, field
from typing import Dict, List, Optional


EXECUTION_EVENT_ACCEPTED = "ACCEPTED"
EXECUTION_EVENT_IN_PROGRESS = "IN_PROGRESS"
EXECUTION_EVENT_COMPLETED = "COMPLETED"
EXECUTION_EVENT_FAILED = "FAILED"

DECISION_CLASSIFICATION_NON_AUTONOMOUS = "NON_AUTONOMOUS_DECISION"


@dataclass(frozen=True)
class ExecutionEventInput:
    order_id: str
    event_type: str
    recorded_by: str
    partner_id: str
    notes: Optional[str] = None
    sla_reference: Optional[str] = None

    def validate(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if self.event_type not in {
            EXECUTION_EVENT_ACCEPTED,
            EXECUTION_EVENT_IN_PROGRESS,
            EXECUTION_EVENT_COMPLETED,
            EXECUTION_EVENT_FAILED,
        }:
            raise ValueError("invalid execution event type")
        if not self.recorded_by.strip():
            raise ValueError("recorded_by is required")
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")


@dataclass(frozen=True)
class ExecutionEvent:
    event_id: str
    order_id: str
    event_type: str
    recorded_by: str
    partner_id: str
    notes: Optional[str]
    sla_reference: Optional[str]
    sequence_number: int
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS
    ai_execution_authority: bool = False
    observational_only: bool = True
    audit_metadata: Dict[str, object] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id is required")
        if self.sequence_number < 1:
            raise ValueError("sequence_number must be at least 1")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")
        if not self.observational_only:
            raise ValueError("execution visibility must remain observational only")


@dataclass(frozen=True)
class OrderExecutionTimeline:
    order_id: str
    partner_id: str
    latest_event_type: Optional[str]
    total_events: int
    sla_reference: Optional[str]
    decision_classification: str
    ai_execution_authority: bool
    events: List[ExecutionEvent] = field(default_factory=list)

    def validate(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if self.total_events != len(self.events):
            raise ValueError("total_events must equal number of timeline events")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")
