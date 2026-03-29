from petcare.pharmacy.http_adapter import ROUTE_REGISTRY, handle_request
from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN
from petcare.pharmacy.repository import PharmacyRepository
from petcare.pharmacy.review import progress_pharmacy_review, start_pharmacy_review
from petcare.pharmacy.service import authorize_prescription, create_prescription, submit_prescription


def _build_repo_with_review():
    repo = PharmacyRepository({}, {})

    draft = create_prescription(
        tenant_id="tenant_001",
        pet_id="pet_001",
        consultation_id="consult_001",
        signed_note_id="note_001",
        medication_code="MED_001",
        medication_name="Steroid HighCare",
        dosage_instructions="once daily",
        quantity="1 pack",
        created_by_user_id="user_vet_001",
    )
    authorized = authorize_prescription(
        draft,
        actor_user_id="user_vet_001",
        actor_role=ROLE_VETERINARIAN,
        signed_note_present=True,
        allergy_records=[],
        active_medication_records=[],
    )
    submitted = submit_prescription(authorized, actor_user_id="user_vet_001")
    repo.add_prescription(submitted)

    review = start_pharmacy_review(
        submitted,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
    )
    repo.add_review(review)

    return repo, review


def test_http_route_success():
    repo, review = _build_repo_with_review()
    response = handle_request(
        repo,
        path="/review/context",
        actor_user_id="user_pharmacy_001",
        params={"review_id": review.review_id},
    )
    assert response["status"] == "success"
    assert response["payload"]["payload"]["review"] == review.review_id


def test_http_route_not_found():
    repo, _ = _build_repo_with_review()
    response = handle_request(
        repo,
        path="/invalid/path",
        actor_user_id="user_pharmacy_001",
        params={},
    )
    assert response["status"] == "error"
    assert response["error"]["code"] == "ROUTE_NOT_FOUND"
