from __future__ import annotations

from petcare.emergency_network.closure_ep06 import build_ep06_closure_report


def _wave01_records():
    return [
        {
            "clinic_id": "clinic-a",
            "availability_status": "open",
            "capacity_status": "available",
            "emergency_ready": True,
        },
        {
            "clinic_id": "clinic-b",
            "availability_status": "limited",
            "capacity_status": "near_capacity",
            "emergency_ready": True,
        },
    ]


def _wave02_query_result():
    return {
        "candidates": [
            {
                "clinic_id": "clinic-a",
                "availability_status": "open",
                "capacity_status": "available",
                "emergency_ready": True,
            },
            {
                "clinic_id": "clinic-b",
                "availability_status": "limited",
                "capacity_status": "near_capacity",
                "emergency_ready": True,
            },
        ]
    }


def _wave03_routing_result():
    return {
        "classification": "NON_AUTONOMOUS_DECISION",
        "requires_human_action": True,
        "ranked_candidates": [
            {
                "clinic_id": "clinic-a",
                "rank": 1,
                "eta_minutes": 8,
                "classification": "NON_AUTONOMOUS_DECISION",
                "requires_human_action": True,
                "explanation": {
                    "summary": "ETA 8 minutes; capacity available; status open; SLA priority 3; emergency ready true",
                    "factors": {
                        "eta_minutes": 8,
                        "capacity_status": "available",
                        "availability_status": "open",
                        "sla_priority": 3,
                        "emergency_ready": True,
                    },
                },
            },
            {
                "clinic_id": "clinic-b",
                "rank": 2,
                "eta_minutes": 12,
                "classification": "NON_AUTONOMOUS_DECISION",
                "requires_human_action": True,
                "explanation": {
                    "summary": "ETA 12 minutes; capacity near_capacity; status limited; SLA priority 2; emergency ready true",
                    "factors": {
                        "eta_minutes": 12,
                        "capacity_status": "near_capacity",
                        "availability_status": "limited",
                        "sla_priority": 2,
                        "emergency_ready": True,
                    },
                },
            },
        ],
    }


def _wave04_referral_package():
    return {
        "decision_classification": "NON_AUTONOMOUS_DECISION",
        "package_status": "OPERATOR_REVIEW_REQUIRED",
        "requires_human_action": True,
        "ai_execution_authority": False,
        "selected_clinic": {
            "clinic_id": "clinic-a",
            "rank": 1,
            "classification": "NON_AUTONOMOUS_DECISION",
            "requires_human_action": True,
        },
        "pre_arrival_packet": {
            "clinical_summary": {
                "pet_id": "pet-001",
                "severity_level": "critical",
            },
            "handoff_checklist": [
                {
                    "step_code": "VERIFY_CONSENT",
                    "completed": True,
                }
            ],
        },
        "operator_review_surface": {
            "action_required": True,
            "candidate_count": 2,
        },
    }


def test_build_ep06_closure_report_validates_all_waves():
    result = build_ep06_closure_report(
        wave01_records=_wave01_records(),
        wave02_query_result=_wave02_query_result(),
        wave03_routing_result=_wave03_routing_result(),
        wave04_referral_package=_wave04_referral_package(),
    )

    assert result["epic"] == "EP-06"
    assert result["closure_status"] == "EP06_GOVERNED_CLOSED"
    assert result["cross_wave_integrity"]["all_validations_passed"] is True
    assert result["cross_wave_integrity"]["validation_count"] == 4
    assert result["cross_wave_integrity"]["waves_validated"] == [
        "WAVE-01",
        "WAVE-02",
        "WAVE-03",
        "WAVE-04",
    ]
    assert result["evidence_ready"] is True


def test_build_ep06_closure_report_preserves_non_autonomous_boundary():
    result = build_ep06_closure_report(
        wave01_records=_wave01_records(),
        wave02_query_result=_wave02_query_result(),
        wave03_routing_result=_wave03_routing_result(),
        wave04_referral_package=_wave04_referral_package(),
    )

    boundary = result["governance_boundary"]

    assert boundary["decision_classification"] == "NON_AUTONOMOUS_DECISION"
    assert boundary["requires_human_action"] is True
    assert boundary["ai_execution_authority"] is False
    assert boundary["operator_review_required"] is True


def test_build_ep06_closure_report_contains_expected_assertions():
    result = build_ep06_closure_report(
        wave01_records=_wave01_records(),
        wave02_query_result=_wave02_query_result(),
        wave03_routing_result=_wave03_routing_result(),
        wave04_referral_package=_wave04_referral_package(),
    )

    assertions = set(result["governance_assertions"])

    assert "availability_model_governed" in assertions
    assert "query_surface_filtered_to_emergency_ready_candidates" in assertions
    assert "routing_classified_as_non_autonomous" in assertions
    assert "referral_package_requires_operator_review" in assertions
    assert "ai_execution_authority_false" in assertions
    assert "requires_human_action_true" in assertions


def test_build_ep06_closure_report_is_deterministic():
    result_one = build_ep06_closure_report(
        wave01_records=_wave01_records(),
        wave02_query_result=_wave02_query_result(),
        wave03_routing_result=_wave03_routing_result(),
        wave04_referral_package=_wave04_referral_package(),
    )

    result_two = build_ep06_closure_report(
        wave01_records=_wave01_records(),
        wave02_query_result=_wave02_query_result(),
        wave03_routing_result=_wave03_routing_result(),
        wave04_referral_package=_wave04_referral_package(),
    )

    assert result_one == result_two


def test_build_ep06_closure_report_accepts_no_selected_clinic_when_referral_requires_review():
    referral_package = _wave04_referral_package()
    referral_package["selected_clinic"] = None
    referral_package["operator_review_surface"]["candidate_count"] = 0

    result = build_ep06_closure_report(
        wave01_records=_wave01_records(),
        wave02_query_result=_wave02_query_result(),
        wave03_routing_result=_wave03_routing_result(),
        wave04_referral_package=referral_package,
    )

    wave04_validation = [item for item in result["validations"] if item["wave"] == "WAVE-04"][0]
    assert wave04_validation["selected_clinic_present"] is False
