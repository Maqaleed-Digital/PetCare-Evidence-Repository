from fastapi import APIRouter, HTTPException

from petcare.partner_network.orders import StructuredOrder, StructuredOrderInput
from petcare.partner_network.orders_repository import OrdersRepository
from petcare.partner_network.orders_service import OrdersService
from petcare.partner_network.pricing_repository import PricingRepository


router = APIRouter()

_orders_repository = OrdersRepository()
_pricing_repository = PricingRepository()
_orders_service = OrdersService(_orders_repository, _pricing_repository)


@router.post("/ep07/wave05/orders", response_model=StructuredOrder)
def create_order(order_input: StructuredOrderInput) -> StructuredOrder:
    try:
        return _orders_service.create_order(order_input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ep07/wave05/orders/{order_id}/validate", response_model=StructuredOrder)
def validate_order(order_id: str) -> StructuredOrder:
    try:
        return _orders_service.validate_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ep07/wave05/orders/{order_id}/route", response_model=StructuredOrder)
def route_order(order_id: str) -> StructuredOrder:
    try:
        return _orders_service.route_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
