from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from petcare.emergency_network.referral import (
    EmergencyReferralRequest,
    build_emergency_referral_package,
)


router = APIRouter(tags=["ep06-wave04"])


class RankedCandidateModel(BaseModel):
    clinic_id: str
    rank: int
    eta_minutes: int
    availability_status: str
    capacity_status: str
    sla_priority: int
    classification: str = "NON_AUTONOMOUS_DECISION"
    requires_human_action: bool = True
    explanation: Dict[str, Any] = Field(default_factory=dict)


class EmergencyReferralPackageRequestModel(BaseModel):
    pet_id: str
    severity_level: str
    symptoms: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    last_consult_summary: Optional[str] = None
    consent_verified: bool
    operator_id: str
    requested_at: Optional[str] = None
    ranked_candidates: List[RankedCandidateModel] = Field(default_factory=list)


@router.post("/ep06/emergency-referral/package")
def build_emergency_referral(payload: EmergencyReferralPackageRequestModel) -> Dict[str, Any]:
    request = EmergencyReferralRequest(
        pet_id=payload.pet_id,
        severity_level=payload.severity_level,
        symptoms=list(payload.symptoms),
        allergies=list(payload.allergies),
        current_medications=list(payload.current_medications),
        last_consult_summary=payload.last_consult_summary,
        consent_verified=payload.consent_verified,
        operator_id=payload.operator_id,
        requested_at=payload.requested_at,
    )

    routing_result = {
        "classification": "NON_AUTONOMOUS_DECISION",
        "requires_human_action": True,
        "ranked_candidates": [candidate.model_dump() for candidate in payload.ranked_candidates],
    }

    return build_emergency_referral_package(
        request=request,
        routing_result=routing_result,
    )
