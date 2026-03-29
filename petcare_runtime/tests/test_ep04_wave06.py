from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN
from petcare.pharmacy.review import progress_pharmacy_review, start_pharmacy_review
from petcare.pharmacy.service import authorize_prescription, create_prescription, submit_prescription
from petcare.pharmacy.visibility import (
    REVIEW_ACCESS_AUDIT_EVENTS,
    REVIEW_DISPOSITION_REGISTRY,
    RETURN_TO_VET_REASON_CODES,
    get_operational_review_status_summary,
    get_return_to_vet_follow_up_link,
    get_review_disposition_registry,
    get_review_history_read_model,
    list_review_timeline_entries,
)


def _authorized_prescription():
    draft = create_prescription(
        tenant_id="tenant_001",
        pet_id="pet_001",
        consultation_id="consult_001",
        signed_note_id="note_signed_001",
        medication_code="MED_001",
        medication_name="Steroid HighCare",
        dosage_instructions="HIGH dose twice daily",
        quantity="1 pack",
        created_by_user_id="user_vet_creator",
    )
    return authorize_prescription(
        draft,
        actor_user_id="user_vet_001",
        actor_role=ROLE_VETERINARIAN,
        signed_note_present=True,
        allergy_records=[],
        active_medication_records=[],
    )


def _returned_review_pair():
    prescription = _authorized_prescription()
    review_record = start_pharmacy_review(
        prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    review_record = progress_pharmacy_review(
        review_record,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
        decision="RETURN_TO_VET_REVIEW",
        reason_code="RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT",
        note_text="Returned to vet due to safety clarification requirement.",
    )
    return prescription, review_record


def test_review_history_read_model_contains_access_audit():
    prescription, review_record = _returned_review_pair()
    _ = prescription
    payload = get_review_history_read_model(
        review_record,
        actor_user_id="user_pharmacy_001",
    )
    assert payload["review_id"] == review_record.review_id
    assert payload["access_audit"]["event_name"] == "prescription.review.history_viewed"


def test_review_timeline_entries_are_deterministic():
    prescription, review_record = _returned_review_pair()
    _ = prescription
    payload = list_review_timeline_entries(
        review_record,
        actor_user_id="user_pharmacy_001",
    )
    assert payload["access_audit"]["event_name"] == "prescription.review.timeline_viewed"
    assert len(payload["timeline"]) >= 3
    assert all("event_name" in item for item in payload["timeline"])


def test_return_to_vet_follow_up_link_is_formalized():
    prescription, review_record = _returned_review_pair()
    payload = get_return_to_vet_follow_up_link(
        prescription,
        review_record,
        actor_user_id="user_pharmacy_001",
    )
    assert payload["follow_up_link"]["follow_up_required"] is True
    assert payload["follow_up_link"]["follow_up_reason_code"] == "RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT"
    assert payload["access_audit"]["event_name"] == "prescription.review.follow_up_link_viewed"


def test_disposition_registry_helper_is_locked():
    payload = get_review_disposition_registry(
        actor_user_id="user_pharmacy_001",
    )
    assert payload["registry"] == [dict(item) for item in REVIEW_DISPOSITION_REGISTRY]
    assert payload["access_audit"]["event_name"] == "prescription.review.disposition_registry_viewed"


def test_operational_review_status_summary_is_deterministic():
    returned_prescription, returned_review = _returned_review_pair()

    ready_prescription = submit_prescription(_authorized_prescription(), actor_user_id="user_vet_001")
    ready_review = start_pharmacy_review(
        ready_prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    ready_review = progress_pharmacy_review(
        ready_review,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
        decision="APPROVE_FOR_DISPENSE_QUEUE",
        reason_code="READY_FOR_QUEUE_CONFIRMATION",
        note_text="Ready for dispense queue boundary.",
    )

    payload = get_operational_review_status_summary(
        [ready_prescription, returned_prescription],
        [ready_review, returned_review],
        actor_user_id="user_pharmacy_001",
    )
    assert payload["total_reviews"] == 2
    assert payload["review_status_counts"]["READY_FOR_DISPENSE_QUEUE"] == 1
    assert payload["review_status_counts"]["RETURNED_TO_VET"] == 1
    assert payload["handoff_outcome_counts"]["READY_FOR_DISPENSE_QUEUE"] == 1
    assert payload["handoff_outcome_counts"]["RETURNED_TO_VET"] == 1
    assert payload["access_audit"]["event_name"] == "prescription.review.operational_summary_viewed"


def test_return_to_vet_follow_up_requires_identity_match():
    prescription, review_record = _returned_review_pair()
    other = _authorized_prescription()
    try:
        get_return_to_vet_follow_up_link(
            other,
            review_record,
            actor_user_id="user_pharmacy_001",
        )
    except ValueError as exc:
        assert "must refer to the same prescription" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_wave06_contracts_are_locked():
    assert REVIEW_ACCESS_AUDIT_EVENTS == (
        "prescription.review.history_viewed",
        "prescription.review.timeline_viewed",
        "prescription.review.follow_up_link_viewed",
        "prescription.review.disposition_registry_viewed",
        "prescription.review.operational_summary_viewed",
    )
    assert RETURN_TO_VET_REASON_CODES == (
        "CLARIFICATION_REQUIRED",
        "RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT",
    )
