from __future__ import annotations

from petcare.emergency_network.routing import EmergencyRoutingRequest, route_emergency_case, select_candidates


def _request(required_capabilities=None, region="jeddah"):
    return EmergencyRoutingRequest(
        pet_id="pet-001",
        severity_level="high",
        required_capabilities=required_capabilities or [],
        location_region=region,
        requested_at="2026-03-30T12:00:00Z",
    )


def _candidate(
    clinic_id,
    eta_minutes,
    availability_status="open",
    capacity_status="available",
    emergency_ready=True,
    sla_priority=1,
    capabilities=None,
    region="jeddah",
):
    return {
        "clinic_id": clinic_id,
        "eta_minutes": eta_minutes,
        "availability_status": availability_status,
        "capacity_status": capacity_status,
        "emergency_ready": emergency_ready,
        "sla_priority": sla_priority,
        "capabilities": capabilities or [],
        "region": region,
    }


def test_select_candidates_filters_non_eligible_candidates():
    request = _request(required_capabilities=["surgery"])

    candidates = [
        _candidate("clinic-a", 12, capabilities=["surgery", "critical_care"]),
        _candidate("clinic-b", 8, capacity_status="full", capabilities=["surgery"]),
        _candidate("clinic-c", 6, emergency_ready=False, capabilities=["surgery"]),
        _candidate("clinic-d", 7, region="riyadh", capabilities=["surgery"]),
        _candidate("clinic-e", 9, capabilities=["imaging"]),
    ]

    selected = select_candidates(request=request, candidates=candidates)

    assert [item["clinic_id"] for item in selected] == ["clinic-a"]


def test_route_emergency_case_ranks_by_eta_then_capacity_then_sla():
    request = _request()

    candidates = [
        _candidate("clinic-c", 10, capacity_status="near_capacity", sla_priority=5),
        _candidate("clinic-a", 8, capacity_status="available", sla_priority=1),
        _candidate("clinic-b", 8, capacity_status="available", sla_priority=3),
    ]

    result = route_emergency_case(request=request, candidates=candidates)

    assert [item["clinic_id"] for item in result["ranked_candidates"]] == [
        "clinic-b",
        "clinic-a",
        "clinic-c",
    ]
    assert [item["rank"] for item in result["ranked_candidates"]] == [1, 2, 3]


def test_route_emergency_case_is_deterministic_for_same_input():
    request = _request()

    candidates = [
        _candidate("clinic-a", 12, capacity_status="available", sla_priority=2),
        _candidate("clinic-b", 6, capacity_status="available", sla_priority=2),
        _candidate("clinic-c", 6, capacity_status="near_capacity", sla_priority=5),
    ]

    result_one = route_emergency_case(request=request, candidates=candidates)
    result_two = route_emergency_case(request=request, candidates=candidates)

    assert result_one == result_two


def test_route_emergency_case_includes_explainability_on_every_candidate():
    request = _request()

    candidates = [
        _candidate("clinic-a", 12, sla_priority=2),
        _candidate("clinic-b", 6, sla_priority=3),
    ]

    result = route_emergency_case(request=request, candidates=candidates)

    for candidate in result["ranked_candidates"]:
        assert candidate["classification"] == "NON_AUTONOMOUS_DECISION"
        assert candidate["requires_human_action"] is True
        assert "explanation" in candidate
        assert candidate["explanation"]["summary"]
        assert candidate["explanation"]["factors"]["eta_minutes"] is not None


def test_route_emergency_case_handles_no_candidates():
    request = _request(required_capabilities=["icu"])

    candidates = [
        _candidate("clinic-a", 12, capabilities=["surgery"]),
        _candidate("clinic-b", 8, availability_status="closed", capabilities=["icu"]),
    ]

    result = route_emergency_case(request=request, candidates=candidates)

    assert result["candidate_count"] == 0
    assert result["ranked_candidates"] == []
    assert result["classification"] == "NON_AUTONOMOUS_DECISION"
    assert result["requires_human_action"] is True
