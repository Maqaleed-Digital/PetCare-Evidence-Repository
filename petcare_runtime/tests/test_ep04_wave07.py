from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN
from petcare.pharmacy.repository import PharmacyRepository
from petcare.pharmacy.review import start_pharmacy_review
from petcare.pharmacy.service import authorize_prescription, create_prescription
from petcare.pharmacy.query import get_full_review_context, list_reviews_for_prescription


def _authorized_prescription():
    draft = create_prescription(
        tenant_id="tenant_001",
        pet_id="pet_001",
        consultation_id="consult_001",
        signed_note_id="note_signed",
        medication_code="MED001",
        medication_name="DrugX",
        dosage_instructions="Standard dose",
        quantity="1",
        created_by_user_id="user_vet",
    )
    return authorize_prescription(
        draft,
        actor_user_id="user_vet",
        actor_role=ROLE_VETERINARIAN,
        signed_note_present=True,
        allergy_records=[],
        active_medication_records=[],
    )


def test_repository_store_and_query():
    repo = PharmacyRepository({}, {})

    prescription = _authorized_prescription()
    repo.add_prescription(prescription)

    review = start_pharmacy_review(
        prescription,
        actor_user_id="pharmacy_user",
        actor_role=ROLE_PHARMACY,
    )
    repo.add_review(review)

    context = get_full_review_context(
        repo,
        review_id=review.review_id,
        actor_user_id="pharmacy_user",
    )

    assert context["prescription"] == prescription.prescription_id
    assert context["review"] == review.review_id
    assert "handoff" in context
    assert "history" in context


def test_list_reviews_for_prescription():
    repo = PharmacyRepository({}, {})

    prescription = _authorized_prescription()
    repo.add_prescription(prescription)

    review = start_pharmacy_review(
        prescription,
        actor_user_id="pharmacy_user",
        actor_role=ROLE_PHARMACY,
    )
    repo.add_review(review)

    result = list_reviews_for_prescription(
        repo,
        prescription_id=prescription.prescription_id,
        actor_user_id="pharmacy_user",
    )

    assert result["count"] == 1
    assert review.review_id in result["review_ids"]
