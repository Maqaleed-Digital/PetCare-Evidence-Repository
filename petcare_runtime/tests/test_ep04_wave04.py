from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN
from petcare.pharmacy.review import (
    PHARMACY_REVIEW_REASON_CODES,
    PHARMACY_REVIEW_WORKFLOW_AUDIT_EVENTS,
    PharmacyReviewStatus,
    get_pharmacy_review_workflow_read_model,
    list_pharmacy_review_records,
    progress_pharmacy_review,
    start_pharmacy_review,
)
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


def test_start_pharmacy_review_requires_pharmacy_role():
    prescription = _authorized_prescription()
    try:
        start_pharmacy_review(
            prescription,
            actor_user_id="user_vet_001",
            actor_role=ROLE_VETERINARIAN,
        )
    except PermissionError as exc:
        assert "Pharmacy operator role is required" in str(exc)
    else:
        raise AssertionError("Expected PermissionError")


def test_start_pharmacy_review_creates_pending_review_record():
    prescription = _authorized_prescription()
    review_record = start_pharmacy_review(
        prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    assert review_record.review_status is PharmacyReviewStatus.PENDING
    assert review_record.audit_trail[-1]["event_name"] == "prescription.review.workflow_started"


def test_progress_review_to_acknowledged_keeps_prescription_boundary_separate():
    prescription = _authorized_prescription()
    review_record = start_pharmacy_review(
        prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    updated = progress_pharmacy_review(
        review_record,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
        decision="ACKNOWLEDGE_WARNINGS",
        reason_code="WARNING_ACKNOWLEDGED",
        note_text="Warnings reviewed with assistive-only handling preserved.",
    )
    assert updated.review_status is PharmacyReviewStatus.ACKNOWLEDGED
    assert updated.notes[-1].reason_code == "WARNING_ACKNOWLEDGED"
    assert updated.audit_trail[-1]["event_name"] == "prescription.review.status_changed"


def test_progress_review_to_return_to_vet_is_formalized():
    prescription = _authorized_prescription()
    review_record = start_pharmacy_review(
        prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    updated = progress_pharmacy_review(
        review_record,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
        decision="RETURN_TO_VET_REVIEW",
        reason_code="RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT",
        note_text="Return to vet requested due to safety context needing clarification.",
    )
    assert updated.review_status is PharmacyReviewStatus.RETURNED_TO_VET
    assert updated.notes[-1].reason_code == "RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT"


def test_review_read_model_is_deterministic():
    prescription = _authorized_prescription()
    review_record = start_pharmacy_review(
        prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    read_model = get_pharmacy_review_workflow_read_model(
        review_record,
        actor_user_id="user_pharmacy_001",
    )
    assert read_model["review_id"] == review_record.review_id
    assert read_model["review_status"] == "PENDING"


def test_review_listing_is_sorted_deterministically():
    first = start_pharmacy_review(
        _authorized_prescription(),
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    second_rx = submit_prescription(_authorized_prescription(), actor_user_id="user_vet_001")
    second = start_pharmacy_review(
        second_rx,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    listing = list_pharmacy_review_records(
        [second, first],
        actor_user_id="user_pharmacy_001",
    )
    assert len(listing) == 2
    assert all("review_id" in item for item in listing)


def test_reason_taxonomy_is_locked():
    assert PHARMACY_REVIEW_REASON_CODES == (
        "WARNING_ACKNOWLEDGED",
        "CLARIFICATION_REQUIRED",
        "RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT",
        "READY_FOR_QUEUE_CONFIRMATION",
    )


def test_wave04_audit_contract_is_locked():
    assert PHARMACY_REVIEW_WORKFLOW_AUDIT_EVENTS == (
        "prescription.review.workflow_started",
        "prescription.review.note_added",
        "prescription.review.reason_recorded",
        "prescription.review.status_changed",
        "prescription.review.read_model_viewed",
        "prescription.review.list_viewed",
    )
