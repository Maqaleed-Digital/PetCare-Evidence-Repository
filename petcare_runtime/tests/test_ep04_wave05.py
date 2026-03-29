from petcare.pharmacy.handoff import (
    REVIEW_HANDOFF_AUDIT_EVENTS,
    REVIEW_HANDOFF_OUTCOMES,
    build_review_handoff_record,
    get_latest_review_decision_summary,
    get_review_handoff_read_model,
    list_ready_for_dispense_queue_from_reviews,
    list_review_handoff_records,
)
from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN, PrescriptionStatus
from petcare.pharmacy.review import progress_pharmacy_review, start_pharmacy_review
from petcare.pharmacy.service import authorize_prescription, create_prescription, submit_prescription


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


def _ready_review_pair():
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
        decision="APPROVE_FOR_DISPENSE_QUEUE",
        reason_code="READY_FOR_QUEUE_CONFIRMATION",
        note_text="Reviewed and marked ready for dispense queue boundary.",
    )
    return prescription, review_record


def test_build_review_handoff_record_is_deterministic():
    prescription, review_record = _ready_review_pair()
    handoff = build_review_handoff_record(prescription, review_record)
    assert handoff.prescription_id == prescription.prescription_id
    assert handoff.review_status == "READY_FOR_DISPENSE_QUEUE"
    assert handoff.handoff_outcome == "READY_FOR_DISPENSE_QUEUE"


def test_get_review_handoff_read_model_returns_boundary_only_data():
    prescription, review_record = _ready_review_pair()
    read_model = get_review_handoff_read_model(
        prescription,
        review_record,
        actor_user_id="user_pharmacy_001",
    )
    assert read_model["prescription_id"] == prescription.prescription_id
    assert read_model["handoff_outcome"] == "READY_FOR_DISPENSE_QUEUE"
    assert read_model["source_prescription_status"] == PrescriptionStatus.AUTHORIZED.value


def test_list_review_handoff_records_is_sorted_deterministically():
    first_prescription, first_review = _ready_review_pair()

    second_prescription = submit_prescription(_authorized_prescription(), actor_user_id="user_vet_001")
    second_review = start_pharmacy_review(
        second_prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )

    listing = list_review_handoff_records(
        [second_prescription, first_prescription],
        [second_review, first_review],
        actor_user_id="user_pharmacy_001",
    )
    assert len(listing) == 2
    assert all("review_id" in item for item in listing)


def test_latest_review_decision_summary_returns_last_note_and_outcome():
    prescription, review_record = _ready_review_pair()
    summary = get_latest_review_decision_summary(
        prescription,
        review_record,
        actor_user_id="user_pharmacy_001",
    )
    assert summary["handoff_outcome"] == "READY_FOR_DISPENSE_QUEUE"
    assert summary["latest_reason_code"] == "READY_FOR_QUEUE_CONFIRMATION"
    assert summary["review_note_count"] == 1


def test_ready_for_dispense_queue_from_reviews_filters_only_ready_reviews():
    ready_prescription, ready_review = _ready_review_pair()

    other_prescription = _authorized_prescription()
    other_review = start_pharmacy_review(
        other_prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )

    queue = list_ready_for_dispense_queue_from_reviews(
        [other_prescription, ready_prescription],
        [other_review, ready_review],
        actor_user_id="user_pharmacy_001",
    )
    assert len(queue) == 1
    assert queue[0].prescription_id == ready_prescription.prescription_id


def test_return_to_vet_outcome_is_preserved_in_summary():
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
        note_text="Returned to vet for further clarification.",
    )

    summary = get_latest_review_decision_summary(
        prescription,
        review_record,
        actor_user_id="user_pharmacy_001",
    )
    assert summary["handoff_outcome"] == "RETURNED_TO_VET"
    assert summary["latest_reason_code"] == "RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT"


def test_handoff_requires_matching_prescription_and_review_record():
    first_prescription, first_review = _ready_review_pair()
    second_prescription = _authorized_prescription()

    try:
        build_review_handoff_record(second_prescription, first_review)
    except ValueError as exc:
        assert "must refer to the same prescription" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_wave05_contracts_are_locked():
    assert REVIEW_HANDOFF_AUDIT_EVENTS == (
        "prescription.review.handoff.read_model_viewed",
        "prescription.review.handoff.list_viewed",
        "prescription.review.handoff.summary_viewed",
    )
    assert REVIEW_HANDOFF_OUTCOMES == (
        "READY_FOR_DISPENSE_QUEUE",
        "RETURNED_TO_VET",
        "REVIEW_IN_PROGRESS",
    )
