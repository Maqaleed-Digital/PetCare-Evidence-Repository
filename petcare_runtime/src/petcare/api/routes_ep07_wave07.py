from fastapi import APIRouter, HTTPException

from petcare.partner_network.execution_visibility_repository import ExecutionVisibilityRepository
from petcare.partner_network.orders_repository import OrdersRepository
from petcare.partner_network.settlement_preparation import (
    SettlementPreparationInput,
    SettlementPreparationRecord,
    SettlementPreparationSummary,
)
from petcare.partner_network.settlement_preparation_repository import SettlementPreparationRepository
from petcare.partner_network.settlement_preparation_service import SettlementPreparationService


router = APIRouter()

_settlement_preparation_repository = SettlementPreparationRepository()
_orders_repository = OrdersRepository()
_execution_visibility_repository = ExecutionVisibilityRepository()
_settlement_preparation_service = SettlementPreparationService(
    _settlement_preparation_repository,
    _orders_repository,
    _execution_visibility_repository,
)


@router.post("/ep07/wave07/settlement-preparation", response_model=SettlementPreparationRecord)
def prepare_settlement_record(settlement_input: SettlementPreparationInput) -> SettlementPreparationRecord:
    try:
        return _settlement_preparation_service.prepare_record(settlement_input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/ep07/wave07/settlement-preparation/partners/{partner_id}", response_model=SettlementPreparationSummary)
def summarize_partner_settlement_records(partner_id: str) -> SettlementPreparationSummary:
    try:
        return _settlement_preparation_service.summarize_partner_records(partner_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
