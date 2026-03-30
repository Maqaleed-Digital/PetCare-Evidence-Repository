from fastapi import APIRouter, HTTPException

from petcare.partner_network.execution_visibility import ExecutionEvent, ExecutionEventInput, OrderExecutionTimeline
from petcare.partner_network.execution_visibility_repository import ExecutionVisibilityRepository
from petcare.partner_network.execution_visibility_service import ExecutionVisibilityService
from petcare.partner_network.orders_repository import OrdersRepository


router = APIRouter()

_execution_visibility_repository = ExecutionVisibilityRepository()
_orders_repository = OrdersRepository()
_execution_visibility_service = ExecutionVisibilityService(
    _execution_visibility_repository,
    _orders_repository,
)


@router.post("/ep07/wave06/orders/execution-events", response_model=ExecutionEvent)
def record_execution_event(event_input: ExecutionEventInput) -> ExecutionEvent:
    try:
        return _execution_visibility_service.record_event(event_input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/ep07/wave06/orders/{order_id}/timeline", response_model=OrderExecutionTimeline)
def get_execution_timeline(order_id: str) -> OrderExecutionTimeline:
    try:
        return _execution_visibility_service.get_timeline(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
