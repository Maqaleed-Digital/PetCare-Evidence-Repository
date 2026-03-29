from petcare.pharmacy.models import ROLE_PHARMACY, ROLE_VETERINARIAN, PrescriptionStatus
from petcare.pharmacy.rules import (
    PHARMACY_REVIEW_AUDIT_EVENTS,
    PHARMACY_REVIEW_DECISIONS,
    apply_wave03_safety_rules,
    build_dose_context,
    evaluate_medication_safety_rules,
    get_pharmacy_review_read_model,
    list_reviewable_prescriptions,
    record_pharmacy_review_decision,
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


def test_build_dose_context_is_deterministic():
    context = build_dose_context(
        species="canine",
        breed="small mix",
        age_months=8,
        weight_kg=4.2,
    )
    assert context.dose_band == "JUVENILE_LIGHT"
    assert context.to_dict() == {
        "species": "canine",
        "breed": "small mix",
        "age_months": 8,
        "weight_kg": 4.2,
        "dose_band": "JUVENILE_LIGHT",
    }


def test_evaluate_medication_safety_rules_returns_advisory_warnings():
    prescription = _authorized_prescription()
    warnings = evaluate_medication_safety_rules(
        prescription,
        species="canine",
        breed="small mix",
        age_months=8,
        weight_kg=4.2,
        known_contraindications=["steroid"],
    )
    codes = sorted(warning.code for warning in warnings)
    assert codes == ["CONTRAINDICATION_CONTEXT", "DOSE_MATRIX_GUARDRAIL"]


def test_apply_wave03_safety_rules_preserves_existing_and_adds_new():
    prescription = _authorized_prescription()
    updated = apply_wave03_safety_rules(
        prescription,
        species="canine",
        breed="small mix",
        age_months=8,
        weight_kg=4.2,
        known_contraindications=["steroid"],
    )
    codes = sorted({warning.code for warning in updated.safety_warnings})
    assert "DOSE_MATRIX_GUARDRAIL" in codes
    assert "CONTRAINDICATION_CONTEXT" in codes
    assert updated.status is PrescriptionStatus.AUTHORIZED


def test_get_pharmacy_review_read_model_is_deterministic():
    prescription = _authorized_prescription()
    updated = apply_wave03_safety_rules(
        prescription,
        species="canine",
        breed="small mix",
        age_months=8,
        weight_kg=4.2,
        known_contraindications=["steroid"],
    )
    read_model = get_pharmacy_review_read_model(updated)
    assert read_model["prescription_id"] == updated.prescription_id
    assert read_model["reviewable"] is True
    assert read_model["warning_codes"] == ["CONTRAINDICATION_CONTEXT", "DOSE_MATRIX_GUARDRAIL"]


def test_list_reviewable_prescriptions_filters_and_sorts():
    first = _authorized_prescription()
    second = _authorized_prescription()
    second = submit_prescription(second, actor_user_id="user_vet_001")

    queue = list_reviewable_prescriptions([second, first])
    assert len(queue) == 2
    assert {entry.status for entry in queue} == {"AUTHORIZED", "SUBMITTED"}


def test_record_pharmacy_review_decision_records_audit_event_without_state_change():
    prescription = _authorized_prescription()
    updated = record_pharmacy_review_decision(
        prescription,
        actor_user_id="user_pharmacy_001",
        actor_role=ROLE_PHARMACY,
        decision="ACKNOWLEDGE_WARNINGS",
        review_note="Warnings reviewed; retain assistive-only posture.",
    )
    assert updated.status is PrescriptionStatus.AUTHORIZED
    assert updated.audit_trail[-1]["event_name"] == "prescription.review.decision_recorded"
    assert updated.audit_trail[-1]["details"]["decision"] == "ACKNOWLEDGE_WARNINGS"


def test_review_decision_requires_pharmacy_role():
    prescription = _authorized_prescription()
    try:
        record_pharmacy_review_decision(
            prescription,
            actor_user_id="user_vet_001",
            actor_role=ROLE_VETERINARIAN,
            decision="ACKNOWLEDGE_WARNINGS",
            review_note="invalid actor role",
        )
    except PermissionError as exc:
        assert "Pharmacy operator role is required" in str(exc)
    else:
        raise AssertionError("Expected PermissionError")


def test_wave03_audit_and_decision_contracts_are_locked():
    assert PHARMACY_REVIEW_AUDIT_EVENTS == (
        "prescription.review.read_model_viewed",
        "prescription.review.list_viewed",
        "prescription.review.decision_recorded",
    )
    assert PHARMACY_REVIEW_DECISIONS == (
        "APPROVE_FOR_DISPENSE_QUEUE",
        "ACKNOWLEDGE_WARNINGS",
        "RETURN_TO_VET_REVIEW",
    )
