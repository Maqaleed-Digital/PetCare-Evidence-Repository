from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from petcare.emergency_network.routing import EmergencyRoutingRequest, route_emergency_case


router = APIRouter(tags=["ep06-wave03"])


class EmergencyRoutingRequestModel(BaseModel):
    pet_id: str
    severity_level: str
    required_capabilities: List[str] = Field(default_factory=list)
    location_region: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    requested_at: Optional[str] = None
    candidates: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/ep06/emergency-routing/suggestions")
def get_emergency_routing_suggestions(payload: EmergencyRoutingRequestModel) -> Dict[str, Any]:
    request = EmergencyRoutingRequest(
        pet_id=payload.pet_id,
        severity_level=payload.severity_level,
        required_capabilities=list(payload.required_capabilities),
        location_region=payload.location_region,
        location_lat=payload.location_lat,
        location_lng=payload.location_lng,
        requested_at=payload.requested_at,
    )
    result = route_emergency_case(
        request=request,
        candidates=payload.candidates,
    )
    result["decision_type"] = "assistive"
    result["ai_execution_authority"] = False
    return result
