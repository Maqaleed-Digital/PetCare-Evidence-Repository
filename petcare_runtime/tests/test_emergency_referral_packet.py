from __future__ import annotations

from petcare.emergency_network.referral import (
    EmergencyReferralRequest,
    build_emergency_referral_package,
)


def _request(consent_verified=True):
    return EmergencyReferralRequest(
        pet_id="pet-001",
        severity_level="critical",
        symptoms=["respiratory distress", "collapse"],
        allergies=["penicillin"],
        current_medications=["med-a"],
        last_consult_summary="Recent emergency escalation from tele-vet consult.",
        consent_verified=consent_verified,
        operator_id="operator-123",
        requested_at="2026-03-30T14:00:00Z",
    )


def _candidate(
    clinic_id: str,
    rank: int,
    eta_minutes: int,
    availability_status: str = "open",
    capacity_status: str = "available",
    sla_priority: int = 1,
):
    return {
        "clinic_id": clinic_id,
        "rank": rank,
        "eta_minutes": eta_minutes,
        "availability_status": availability_status,
        "capacity_status": capacity_status,
        "sla_priority": sla_priority,
        "classification": "NON_AUTONOMOUS_DECISION",
        "requires_human_action": True,
        "explanation": {
            "summary": f"{clinic_id} selected based on ETA and readiness",
            "factors": {
                "eta_minutes": eta_minutes,
                "capacity_status": capacity_status,
                "availability_status": availability_status,
                "sla_priority": sla_priority,
                "emergency_ready": True,
            },
            "reasons": [
                f"ETA {eta_minutes} minutes",
                f"capacity {capacity_status}",
                f"status {availability_status}",
                f"SLA priority {sla_priority}",
            ],
        },
    }


def test_build_emergency_referral_package_selects_top_ranked_candidate():
    request = _request()
    routing_result = {
        "ranked_candidates": [
            _candidate("clinic-b", rank=2, eta_minutes=12),
            _candidate("clinic-a", rank=1, eta_minutes=8),
        ]
    }

    result = build_emergency_referral_package(request=request, routing_result=routing_result)

    assert result["selected_clinic"]["clinic_id"] == "clinic-a"
    assert result["selected_clinic"]["rank"] == 1
    assert result["operator_review_surface"]["action_required"] is True


def test_build_emergency_referral_package_preserves_assistive_boundary():
    request = _request()
    routing_result = {
        "ranked_candidates": [
            _candidate("clinic-a", rank=1, eta_minutes=8),
        ]
    }

    result = build_emergency_referral_package(request=request, routing_result=routing_result)

    assert result["decision_classification"] == "NON_AUTONOMOUS_DECISION"
    assert result["package_status"] == "OPERATOR_REVIEW_REQUIRED"
    assert result["requires_human_action"] is True
    assert result["ai_execution_authority"] is False


def test_build_emergency_referral_package_includes_pre_arrival_packet_and_reasoning():
    request = _request()
    routing_result = {
        "ranked_candidates": [
            _candidate("clinic-a", rank=1, eta_minutes=8),
            _candidate("clinic-b", rank=2, eta_minutes=11),
        ]
    }

    result = build_emergency_referral_package(request=request, routing_result=routing_result)

    assert result["pre_arrival_packet"]["clinical_summary"]["pet_id"] == "pet-001"
    assert result["pre_arrival_packet"]["referral_reasoning"]["summary"]
    assert result["pre_arrival_packet"]["logistics"]["recommended_clinic_id"] == "clinic-a"
    assert len(result["fallback_candidates"]) == 1
    assert result["fallback_candidates"][0]["clinic_id"] == "clinic-b"


def test_build_emergency_referral_package_handles_no_candidates():
    request = _request()
    routing_result = {
        "ranked_candidates": []
    }

    result = build_emergency_referral_package(request=request, routing_result=routing_result)

    assert result["selected_clinic"] is None
    assert result["fallback_candidates"] == []
    assert result["operator_review_surface"]["candidate_count"] == 0
    assert result["pre_arrival_packet"]["logistics"]["recommended_clinic_id"] is None


def test_build_emergency_referral_package_is_deterministic():
    request = _request(consent_verified=False)
    routing_result = {
        "ranked_candidates": [
            _candidate("clinic-a", rank=1, eta_minutes=8),
            _candidate("clinic-b", rank=2, eta_minutes=11),
        ]
    }

    result_one = build_emergency_referral_package(request=request, routing_result=routing_result)
    result_two = build_emergency_referral_package(request=request, routing_result=routing_result)

    assert result_one == result_two
    checklist = result_one["pre_arrival_packet"]["handoff_checklist"]
    consent_step = [item for item in checklist if item["step_code"] == "VERIFY_CONSENT"][0]
    assert consent_step["completed"] is False
