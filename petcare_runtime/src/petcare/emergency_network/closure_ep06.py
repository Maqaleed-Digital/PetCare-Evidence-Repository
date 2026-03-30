from __future__ import annotations

from typing import Any, Dict, Iterable, List


EP06_CLOSURE_STATUS = "EP06_GOVERNED_CLOSED"
NON_AUTONOMOUS_DECISION = "NON_AUTONOMOUS_DECISION"
OPERATOR_REVIEW_REQUIRED = "OPERATOR_REVIEW_REQUIRED"


def _sorted_strings(values: Iterable[Any]) -> List[str]:
    return sorted(str(value) for value in values)


def _validate_wave01_records(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    checked = 0
    for record in records:
        checked += 1
        assert bool(record.get("emergency_ready")) is True
        assert str(record.get("availability_status")) in {"open", "limited", "closed"}
        assert str(record.get("capacity_status")) in {"available", "near_capacity", "full"}
    return {
        "wave": "WAVE-01",
        "records_checked": checked,
        "governance_preserved": True,
    }


def _validate_wave02_query_surface(query_result: Dict[str, Any]) -> Dict[str, Any]:
    candidates = list(query_result.get("candidates") or query_result.get("items") or [])
    for candidate in candidates:
        assert bool(candidate.get("emergency_ready")) is True
        assert str(candidate.get("availability_status")) in {"open", "limited"}
        assert str(candidate.get("capacity_status")) != "full"
    return {
        "wave": "WAVE-02",
        "eligible_candidates_checked": len(candidates),
        "governance_preserved": True,
    }


def _validate_wave03_routing(routing_result: Dict[str, Any]) -> Dict[str, Any]:
    assert routing_result.get("classification") == NON_AUTONOMOUS_DECISION
    assert routing_result.get("requires_human_action") is True

    ranked_candidates = list(routing_result.get("ranked_candidates") or [])
    last_rank = 0
    seen_clinic_ids = set()

    for candidate in ranked_candidates:
        clinic_id = str(candidate.get("clinic_id") or candidate.get("partner_id") or "")
        assert clinic_id not in seen_clinic_ids
        seen_clinic_ids.add(clinic_id)

        rank = int(candidate.get("rank") or 0)
        assert rank > last_rank
        last_rank = rank

        assert candidate.get("classification") == NON_AUTONOMOUS_DECISION
        assert candidate.get("requires_human_action") is True
        explanation = dict(candidate.get("explanation") or {})
        assert bool(explanation.get("summary"))
        factors = dict(explanation.get("factors") or {})
        assert factors.get("eta_minutes") is not None

    return {
        "wave": "WAVE-03",
        "ranked_candidates_checked": len(ranked_candidates),
        "governance_preserved": True,
    }


def _validate_wave04_referral(referral_package: Dict[str, Any]) -> Dict[str, Any]:
    assert referral_package.get("decision_classification") == NON_AUTONOMOUS_DECISION
    assert referral_package.get("package_status") == OPERATOR_REVIEW_REQUIRED
    assert referral_package.get("requires_human_action") is True
    assert referral_package.get("ai_execution_authority") is False

    selected_clinic = referral_package.get("selected_clinic")
    if selected_clinic is not None:
        assert selected_clinic.get("classification") == NON_AUTONOMOUS_DECISION
        assert selected_clinic.get("requires_human_action") is True

    pre_arrival_packet = dict(referral_package.get("pre_arrival_packet") or {})
    assert "clinical_summary" in pre_arrival_packet
    assert "handoff_checklist" in pre_arrival_packet

    operator_review_surface = dict(referral_package.get("operator_review_surface") or {})
    assert operator_review_surface.get("action_required") is True

    return {
        "wave": "WAVE-04",
        "selected_clinic_present": selected_clinic is not None,
        "governance_preserved": True,
    }


def build_ep06_closure_report(
    wave01_records: Iterable[Dict[str, Any]],
    wave02_query_result: Dict[str, Any],
    wave03_routing_result: Dict[str, Any],
    wave04_referral_package: Dict[str, Any],
) -> Dict[str, Any]:
    validations = [
        _validate_wave01_records(wave01_records),
        _validate_wave02_query_surface(wave02_query_result),
        _validate_wave03_routing(wave03_routing_result),
        _validate_wave04_referral(wave04_referral_package),
    ]

    governance_assertions = [
        "availability_model_governed",
        "query_surface_filtered_to_emergency_ready_candidates",
        "routing_classified_as_non_autonomous",
        "referral_package_requires_operator_review",
        "ai_execution_authority_false",
        "requires_human_action_true",
    ]

    return {
        "epic": "EP-06",
        "closure_status": EP06_CLOSURE_STATUS,
        "governance_boundary": {
            "decision_classification": NON_AUTONOMOUS_DECISION,
            "requires_human_action": True,
            "ai_execution_authority": False,
            "operator_review_required": True,
        },
        "cross_wave_integrity": {
            "waves_validated": _sorted_strings(item["wave"] for item in validations),
            "all_validations_passed": True,
            "validation_count": len(validations),
        },
        "validations": validations,
        "governance_assertions": governance_assertions,
        "evidence_ready": True,
    }
