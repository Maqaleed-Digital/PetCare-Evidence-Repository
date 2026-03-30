from fastapi import APIRouter, HTTPException

from petcare.partner_network.settlement_export import SettlementExportInput, SettlementExportPackage, SettlementExportSummary
from petcare.partner_network.settlement_export_repository import SettlementExportRepository
from petcare.partner_network.settlement_export_service import SettlementExportService
from petcare.partner_network.settlement_review_repository import SettlementReviewRepository


router = APIRouter()

_settlement_export_repository = SettlementExportRepository()
_settlement_review_repository = SettlementReviewRepository()
_settlement_export_service = SettlementExportService(
    _settlement_export_repository,
    _settlement_review_repository,
)


@router.post("/ep07/wave09/settlement-export", response_model=SettlementExportPackage)
def create_settlement_export_package(export_input: SettlementExportInput) -> SettlementExportPackage:
    try:
        return _settlement_export_service.create_export_package(export_input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/ep07/wave09/settlement-export/partners/{partner_id}", response_model=SettlementExportSummary)
def summarize_partner_settlement_exports(partner_id: str) -> SettlementExportSummary:
    try:
        return _settlement_export_service.summarize_partner_exports(partner_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
