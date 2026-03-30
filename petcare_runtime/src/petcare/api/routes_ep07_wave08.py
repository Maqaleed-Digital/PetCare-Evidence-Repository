from fastapi import APIRouter, HTTPException

from petcare.partner_network.settlement_preparation_repository import SettlementPreparationRepository
from petcare.partner_network.settlement_review import (
    SettlementReviewDecisionInput,
    SettlementReviewDecisionRecord,
    SettlementReviewQueueItem,
    SettlementReviewQueueSummary,
)
from petcare.partner_network.settlement_review_repository import SettlementReviewRepository
from petcare.partner_network.settlement_review_service import SettlementReviewService


router = APIRouter()

_settlement_review_repository = SettlementReviewRepository()
_settlement_preparation_repository = SettlementPreparationRepository()
_settlement_review_service = SettlementReviewService(
    _settlement_review_repository,
    _settlement_preparation_repository,
)


@router.post("/ep07/wave08/settlement-review/{review_id}/queue/{settlement_preparation_id}", response_model=SettlementReviewQueueItem)
def enqueue_settlement_review_item(review_id: str, settlement_preparation_id: str) -> SettlementReviewQueueItem:
    try:
        return _settlement_review_service.enqueue_review_item(review_id, settlement_preparation_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ep07/wave08/settlement-review/decision", response_model=SettlementReviewDecisionRecord)
def record_settlement_review_decision(decision_input: SettlementReviewDecisionInput) -> SettlementReviewDecisionRecord:
    try:
        return _settlement_review_service.record_decision(decision_input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/ep07/wave08/settlement-review/partners/{partner_id}", response_model=SettlementReviewQueueSummary)
def summarize_partner_settlement_review_queue(partner_id: str) -> SettlementReviewQueueSummary:
    try:
        return _settlement_review_service.summarize_partner_queue(partner_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
