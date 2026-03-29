from petcare.pharmacy.api import (
    READ_ONLY_API_SURFACES,
    get_latest_review_summary_endpoint,
    get_operational_review_status_summary_endpoint,
    get_return_to_vet_follow_up_endpoint,
    get_review_context_endpoint,
    get_review_disposition_registry_endpoint,
    get_review_handoff_endpoint,
    get_review_history_endpoint,
    get_review_timeline_endpoint,
    list_ready_for_dispense_queue_endpoint,
    list_review_handoffs_endpoint,
    list_reviews_for_prescription_endpoint,
)
from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN
from petcare.pharmacy.repository import PharmacyRepository
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


def _repo_with_reviews():
    repo = PharmacyRepository({}, {})

    ready_prescription = submit_prescription(_authorized_prescription(), actor_user_id="user_vet_001")
    repo.add_prescription(ready_prescription)
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
    repo.add_review(ready_review)

    returned_prescription = _authorized_prescription()
    repo.add_prescription(returned_prescription)
    returned_review = start_pharmacy_review(
        returned_prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    returned_review = progress_pharmacy_review(
        returned_review,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
        decision="RETURN_TO_VET_REVIEW",
        reason_code="RETURN_TO_VET_DUE_TO_SAFETY_CONTEXT",
        note_text="Returned to vet due to safety clarification requirement.",
    )
    repo.add_review(returned_review)

    return repo, ready_prescription, ready_review, returned_prescription, returned_review


def test_wave08_api_surfaces_are_locked():
    assert READ_ONLY_API_SURFACES == (
        "get_review_context_endpoint",
        "list_reviews_for_prescription_endpoint",
        "get_review_handoff_endpoint",
        "list_review_handoffs_endpoint",
        "get_latest_review_summary_endpoint",
        "list_ready_for_dispense_queue_endpoint",
        "get_review_history_endpoint",
        "get_review_timeline_endpoint",
        "get_return_to_vet_follow_up_endpoint",
        "get_review_disposition_registry_endpoint",
        "get_operational_review_status_summary_endpoint",
    )


def test_get_review_context_endpoint_is_read_only():
    repo, _, ready_review, _, _ = _repo_with_reviews()
    payload = get_review_context_endpoint(
        repo,
        review_id=ready_review.review_id,
        actor_user_id="user_pharmacy_001",
    )
    assert payload["surface"] == "get_review_context_endpoint"
    assert payload["read_only"] is True
    assert payload["payload"]["review"] == ready_review.review_id


def test_list_reviews_for_prescription_endpoint_returns_count():
    repo, ready_prescription, ready_review, _, _ = _repo_with_reviews()
    payload = list_reviews_for_prescription_endpoint(
        repo,
        prescription_id=ready_prescription.prescription_id,
        actor_user_id="user_pharmacy_001",
    )
    assert payload["read_only"] is True
    assert payload["payload"]["count"] == 1
    assert ready_review.review_id in payload["payload"]["review_ids"]


def test_handoff_and_summary_endpoints_are_read_only():
    repo, _, ready_review, _, _ = _repo_with_reviews()

    handoff_payload = get_review_handoff_endpoint(
        repo,
        review_id=ready_review.review_id,
        actor_user_id="user_pharmacy_001",
    )
    summary_payload = get_latest_review_summary_endpoint(
        repo,
        review_id=ready_review.review_id,
        actor_user_id="user_pharmacy_001",
    )

    assert handoff_payload["read_only"] is True
    assert handoff_payload["payload"]["handoff_outcome"] == "READY_FOR_DISPENSE_QUEUE"
    assert summary_payload["read_only"] is True
    assert summary_payload["payload"]["handoff_outcome"] == "READY_FOR_DISPENSE_QUEUE"


def test_history_timeline_and_follow_up_endpoints_are_read_only():
    repo, _, _, _, returned_review = _repo_with_reviews()

    history_payload = get_review_history_endpoint(
        repo,
        review_id=returned_review.review_id,
        actor_user_id="user_pharmacy_001",
    )
    timeline_payload = get_review_timeline_endpoint(
        repo,
        review_id=returned_review.review_id,
        actor_user_id="user_pharmacy_001",
    )
    follow_up_payload = get_return_to_vet_follow_up_endpoint(
        repo,
        review_id=returned_review.review_id,
        actor_user_id="user_pharmacy_001",
    )

    assert history_payload["read_only"] is True
    assert timeline_payload["read_only"] is True
    assert follow_up_payload["read_only"] is True
    assert follow_up_payload["payload"]["follow_up_link"]["follow_up_required"] is True


def test_list_handoffs_queue_registry_and_summary_endpoints_are_read_only():
    repo, ready_prescription, _, _, _ = _repo_with_reviews()
    _ = ready_prescription

    handoffs_payload = list_review_handoffs_endpoint(
        repo,
        tenant_id="tenant_001",
        actor_user_id="user_pharmacy_001",
    )
    queue_payload = list_ready_for_dispense_queue_endpoint(
        repo,
        tenant_id="tenant_001",
        actor_user_id="user_pharmacy_001",
    )
    registry_payload = get_review_disposition_registry_endpoint(
        actor_user_id="user_pharmacy_001",
    )
    summary_payload = get_operational_review_status_summary_endpoint(
        repo,
        tenant_id="tenant_001",
        actor_user_id="user_pharmacy_001",
    )

    assert handoffs_payload["read_only"] is True
    assert len(handoffs_payload["payload"]["items"]) == 2
    assert queue_payload["read_only"] is True
    assert len(queue_payload["payload"]["items"]) == 1
    assert registry_payload["read_only"] is True
    assert summary_payload["read_only"] is True
    assert summary_payload["payload"]["total_reviews"] == 2
