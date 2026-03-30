from typing import Dict, List

from .execution_visibility import ExecutionEvent


class ExecutionVisibilityRepository:
    def __init__(self) -> None:
        self._events_by_order: Dict[str, List[ExecutionEvent]] = {}

    def append_event(self, event: ExecutionEvent) -> ExecutionEvent:
        event.validate()
        if event.order_id not in self._events_by_order:
            self._events_by_order[event.order_id] = []
        self._events_by_order[event.order_id].append(event)
        return event

    def list_events_for_order(self, order_id: str) -> List[ExecutionEvent]:
        events = self._events_by_order.get(order_id, [])
        return sorted(events, key=lambda item: (item.sequence_number, item.event_id))
