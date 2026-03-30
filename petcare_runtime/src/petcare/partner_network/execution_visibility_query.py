from typing import List

from .execution_visibility import (
    EXECUTION_EVENT_COMPLETED,
    EXECUTION_EVENT_FAILED,
    ExecutionEvent,
    OrderExecutionTimeline,
)


class ExecutionVisibilityQuery:
    def list_failed_events(self, events: List[ExecutionEvent]) -> List[ExecutionEvent]:
        return sorted(
            [event for event in events if event.event_type == EXECUTION_EVENT_FAILED],
            key=lambda item: (item.order_id, item.sequence_number),
        )

    def list_completed_timelines(self, timelines: List[OrderExecutionTimeline]) -> List[OrderExecutionTimeline]:
        return sorted(
            [timeline for timeline in timelines if timeline.latest_event_type == EXECUTION_EVENT_COMPLETED],
            key=lambda item: item.order_id,
        )
