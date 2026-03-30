from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from petcare.emergency_network.explainability import build_explanation
from petcare.emergency_network.ranking import rank_candidates


NON_AUTONOMOUS_DECISION = "NON_AUTONOMOUS_DECISION"


@dataclass(frozen=True)
class EmergencyRoutingRequest:
    pet_id: str
    severity_level: str
    required_capabilities: List[str]
    location_region: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    requested_at: Optional[str] = None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _normalize_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _capabilities_match(candidate: Dict[str, Any], required_capabilities: List[str]) -> bool:
    if not required_capabilities:
        return True
    candidate_capabilities = {
        _normalize_text(item)
        for item in (candidate.get("capabilities") or [])
    }
    required = {_normalize_text(item) for item in required_capabilities}
    return required.issubset(candidate_capabilities)


def _region_match(candidate: Dict[str, Any], request: EmergencyRoutingRequest) -> bool:
    if not request.location_region:
        return True
    candidate_region = _normalize_text(candidate.get("region"))
    requested_region = _normalize_text(request.location_region)
    return candidate_region == requested_region


def _is_eligible(candidate: Dict[str, Any], request: EmergencyRoutingRequest) -> bool:
    availability_status = _normalize_text(candidate.get("availability_status"))
    capacity_status = _normalize_text(candidate.get("capacity_status"))
    emergency_ready = bool(candidate.get("emergency_ready"))

    if availability_status not in {"open", "limited"}:
        return False
    if capacity_status == "full":
        return False
    if not emergency_ready:
        return False
    if not _capabilities_match(candidate, request.required_capabilities):
        return False
    if not _region_match(candidate, request):
        return False
    return True


def _coerce_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    coerced = dict(candidate)
    coerced["clinic_id"] = str(candidate.get("clinic_id") or candidate.get("partner_id") or "")
    coerced["eta_minutes"] = _normalize_int(candidate.get("eta_minutes"), default=10**9)
    coerced["sla_priority"] = _normalize_int(candidate.get("sla_priority"), default=0)
    coerced["availability_status"] = _normalize_text(candidate.get("availability_status"))
    coerced["capacity_status"] = _normalize_text(candidate.get("capacity_status"))
    coerced["emergency_ready"] = bool(candidate.get("emergency_ready"))
    coerced["capabilities"] = list(candidate.get("capabilities") or [])
    return coerced


def select_candidates(
    request: EmergencyRoutingRequest,
    candidates: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    eligible: List[Dict[str, Any]] = []
    for candidate in candidates:
        coerced = _coerce_candidate(candidate)
        if _is_eligible(coerced, request):
            eligible.append(coerced)
    return eligible


def route_emergency_case(
    request: EmergencyRoutingRequest,
    candidates: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    eligible = select_candidates(request=request, candidates=candidates)
    ranked = rank_candidates(eligible)

    for candidate in ranked:
        candidate["classification"] = NON_AUTONOMOUS_DECISION
        candidate["requires_human_action"] = True
        candidate["explanation"] = build_explanation(candidate)

    return {
        "pet_id": request.pet_id,
        "severity_level": request.severity_level,
        "classification": NON_AUTONOMOUS_DECISION,
        "requires_human_action": True,
        "candidate_count": len(ranked),
        "ranked_candidates": ranked,
    }
