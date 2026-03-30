from .execution_visibility import (
    DECISION_CLASSIFICATION_NON_AUTONOMOUS,
    EXECUTION_EVENT_ACCEPTED,
    EXECUTION_EVENT_COMPLETED,
    EXECUTION_EVENT_FAILED,
    EXECUTION_EVENT_IN_PROGRESS,
    ExecutionEvent,
    ExecutionEventInput,
    OrderExecutionTimeline,
)
from .execution_visibility_repository import ExecutionVisibilityRepository
from .orders import ORDER_STATUS_ROUTED
from .orders_repository import OrdersRepository


_ALLOWED_NEXT_EVENTS = {
    None: [EXECUTION_EVENT_ACCEPTED, EXECUTION_EVENT_FAILED],
    EXECUTION_EVENT_ACCEPTED: [EXECUTION_EVENT_IN_PROGRESS, EXECUTION_EVENT_FAILED],
    EXECUTION_EVENT_IN_PROGRESS: [EXECUTION_EVENT_COMPLETED, EXECUTION_EVENT_FAILED],
    EXECUTION_EVENT_COMPLETED: [],
    EXECUTION_EVENT_FAILED: [],
}


class ExecutionVisibilityService:
    def __init__(
        self,
        execution_visibility_repository: ExecutionVisibilityRepository,
        orders_repository: OrdersRepository,
    ) -> None:
        self._execution_visibility_repository = execution_visibility_repository
        self._orders_repository = orders_repository

    def record_event(self, event_input: ExecutionEventInput) -> ExecutionEvent:
        event_input.validate()

        order = self._orders_repository.get(event_input.order_id)
        if order is None:
            raise ValueError("order not found")

        if order.status != ORDER_STATUS_ROUTED:
            raise ValueError("order must be ROUTED before execution visibility events can be recorded")

        if order.partner_id != event_input.partner_id:
            raise ValueError("execution event partner mismatch")

        existing_events = self._execution_visibility_repository.list_events_for_order(event_input.order_id)
        previous_event_type = existing_events[-1].event_type if existing_events else None
        allowed_next_events = _ALLOWED_NEXT_EVENTS[previous_event_type]

        if event_input.event_type not in allowed_next_events:
            raise ValueError("invalid execution event transition")

        sequence_number = len(existing_events) + 1
        event = ExecutionEvent(
            event_id=f"{event_input.order_id}-evt-{sequence_number}",
            order_id=event_input.order_id,
            event_type=event_input.event_type,
            recorded_by=event_input.recorded_by,
            partner_id=event_input.partner_id,
            notes=event_input.notes,
            sla_reference=event_input.sla_reference,
            sequence_number=sequence_number,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            observational_only=True,
            audit_metadata={
                "timeline_mode": "append_only",
                "observational_only": True,
                "sla_reference": event_input.sla_reference,
            },
        )
        return self._execution_visibility_repository.append_event(event)

    def get_timeline(self, order_id: str) -> OrderExecutionTimeline:
        order = self._orders_repository.get(order_id)
        if order is None:
            raise ValueError("order not found")

        events = self._execution_visibility_repository.list_events_for_order(order_id)
        latest_event_type = events[-1].event_type if events else None
        latest_sla_reference = events[-1].sla_reference if events else None

        timeline = OrderExecutionTimeline(
            order_id=order_id,
            partner_id=order.partner_id,
            latest_event_type=latest_event_type,
            total_events=len(events),
            sla_reference=latest_sla_reference,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            events=events,
        )
        timeline.validate()
        return timeline
