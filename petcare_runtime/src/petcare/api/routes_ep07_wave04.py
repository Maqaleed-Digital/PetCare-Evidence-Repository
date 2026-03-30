from fastapi import APIRouter, HTTPException

from petcare.partner_network.pricing import PricingInput, PricingOutput, PricingRule
from petcare.partner_network.pricing_repository import PricingRepository
from petcare.partner_network.pricing_service import PricingService


router = APIRouter()

_pricing_repository = PricingRepository()
_pricing_service = PricingService(_pricing_repository)


@router.post("/ep07/wave04/pricing/rules", response_model=PricingRule)
def create_pricing_rule(rule: PricingRule) -> PricingRule:
    try:
        return _pricing_service.create_rule(rule)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ep07/wave04/pricing/calculate", response_model=PricingOutput)
def calculate_pricing(pricing_input: PricingInput) -> PricingOutput:
    try:
        return _pricing_service.calculate_offer(pricing_input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
