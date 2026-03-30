from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


NON_AUTONOMOUS_DECISION = "NON_AUTONOMOUS_DECISION"
OPERATOR_REVIEW_REQUIRED = "OPERATOR_REVIEW_REQUIRED"


@dataclass(frozen=True)
class EmergencyReferralRequest:
    pet_id: str
    severity_level: str
    symptoms: List[str]
    allergies: List[str]
    current_medications: List[str]
    last_consult_summary: Optional[str]
    consent_verified: bool
    operator_id: str
    requested_at: Optional[str] = None


def _copy_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "clinic_id": str(candidate.get("clinic_id") or candidate.get("partner_id") or ""),
        "rank": candidate.get("rank"),
        "eta_minutes": candidate.get("eta_minutes"),
        "availability_status": candidate.get("availability_status"),
        "capacity_status": candidate.get("capacity_status"),
        "sla_priority": candidate.get("sla_priority"),
        "classification": candidate.get("classification", NON_AUTONOMOUS_DECISION),
        "requires_human_action": bool(candidate.get("requires_human_action", True)),
        "explanation": dict(candidate.get("explanation") or {}),
    }


def _select_primary_candidate(routing_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    candidates = list(routing_result.get("ranked_candidates") or [])
    if not candidates:
        return None
    ordered = sorted(
        candidates,
        key=lambda item: (
            int(item.get("rank") or 10**9),
            str(item.get("clinic_id") or item.get("partner_id") or ""),
        ),
    )
    return _copy_candidate(ordered[0])


def _build_clinical_summary(request: EmergencyReferralRequest) -> Dict[str, Any]:
    return {
        "pet_id": request.pet_id,
        "severity_level": request.severity_level,
        "symptoms": list(request.symptoms),
        "allergies": list(request.allergies),
        "current_medications": list(request.current_medications),
        "last_consult_summary": request.last_consult_summary,
    }


def _build_handoff_checklist(primary_candidate: Optional[Dict[str, Any]], consent_verified: bool) -> List[Dict[str, Any]]:
    clinic_selected = primary_candidate is not None
    checklist = [
        {
            "step_code": "VERIFY_CONSENT",
            "label": "Verify referral consent before handoff",
            "completed": bool(consent_verified),
        },
        {
            "step_code": "OPERATOR_REVIEW",
            "label": "Operator reviews ranked referral recommendation",
            "completed": False,
        },
        {
            "step_code": "CLINIC_CONFIRMATION",
            "label": "Clinic acceptance must be confirmed manually",
            "completed": False,
        },
        {
            "step_code": "OWNER_INSTRUCTION",
            "label": "Owner receives manual pre-arrival instructions",
            "completed": False,
        },
        {
            "step_code": "CLINIC_SELECTED",
            "label": "Primary clinic recommendation exists",
            "completed": clinic_selected,
        },
    ]
    return checklist


def build_emergency_referral_package(
    request: EmergencyReferralRequest,
    routing_result: Dict[str, Any],
) -> Dict[str, Any]:
    primary_candidate = _select_primary_candidate(routing_result)
    fallback_candidates = [
        _copy_candidate(item)
        for item in sorted(
            list(routing_result.get("ranked_candidates") or []),
            key=lambda candidate: (
                int(candidate.get("rank") or 10**9),
                str(candidate.get("clinic_id") or candidate.get("partner_id") or ""),
            ),
        )[1:]
    ]

    packet = {
        "pet_id": request.pet_id,
        "severity_level": request.severity_level,
        "decision_classification": NON_AUTONOMOUS_DECISION,
        "package_status": OPERATOR_REVIEW_REQUIRED,
        "requires_human_action": True,
        "ai_execution_authority": False,
        "operator_id": request.operator_id,
        "requested_at": request.requested_at,
        "consent_verified": bool(request.consent_verified),
        "selected_clinic": primary_candidate,
        "fallback_candidates": fallback_candidates,
        "pre_arrival_packet": {
            "clinical_summary": _build_clinical_summary(request),
            "referral_reasoning": (primary_candidate or {}).get("explanation", {}),
            "logistics": {
                "recommended_eta_minutes": (primary_candidate or {}).get("eta_minutes"),
                "recommended_clinic_id": (primary_candidate or {}).get("clinic_id"),
            },
            "handoff_checklist": _build_handoff_checklist(primary_candidate, request.consent_verified),
        },
        "operator_review_surface": {
            "summary": "Manual operator review required before referral handoff",
            "selected_rank": (primary_candidate or {}).get("rank"),
            "candidate_count": len(list(routing_result.get("ranked_candidates") or [])),
            "action_required": True,
        },
    }

    return packet
