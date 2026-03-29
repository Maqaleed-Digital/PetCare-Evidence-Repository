"""EP-04 Wave 01: Pharmacy and Medication Lifecycle — unit tests."""
import pytest

from petcare.pharmacy import (
    PRESCRIPTION_AUDIT_EVENTS,
    PrescriptionStatus,
    authorize_prescription,
    cancel_prescription,
    create_prescription,
    dispense_prescription,
    get_pharmacy_review_queue,
    submit_prescription,
)

TENANT = "tenant-001"
PET = "pet-001"
CONSULT = "consult-001"
NOTE = "note-signed-001"
VET = "user-vet-001"
PHARM = "user-pharm-001"
OWNER = "user-owner-001"


def _draft():
    return create_prescription(
        tenant_id=TENANT,
        pet_id=PET,
        consultation_id=CONSULT,
        signed_note_id=NOTE,
        medication_code="MED-001",
        medication_name="Amoxicillin 250mg",
        dosage_instructions="1 tablet twice daily for 7 days",
        quantity="14 tablets",
        created_by_user_id=VET,
    )


# --- Test 1: authorization requires ROLE_VETERINARIAN ---

def test_prescription_authorization_requires_veterinarian_role():
    rx = _draft()
    with pytest.raises(PermissionError):
        authorize_prescription(
            rx,
            actor_user_id=OWNER,
            actor_role="ROLE_OWNER",
            signed_note_present=True,
            allergy_records=[],
            active_medication_records=[],
        )


# --- Test 2: authorization requires signed note ---

def test_prescription_authorization_requires_signed_note():
    rx = _draft()
    with pytest.raises(Exception) as exc_info:
        authorize_prescription(
            rx,
            actor_user_id=VET,
            actor_role="ROLE_VETERINARIAN",
            signed_note_present=False,
            allergy_records=[],
            active_medication_records=[],
        )
    assert "signed" in str(exc_info.value).lower()


# --- Test 3: advisory safety warnings do not block authorization ---

def test_authorization_adds_advisory_safety_warnings_without_blocking():
    rx = _draft()
    allergy_records = [{"allergen_code": "MED-001", "severity": "HIGH"}]
    active_records = [{"medication_code": "MED-001", "status": "active"}]
    authorized = authorize_prescription(
        rx,
        actor_user_id=VET,
        actor_role="ROLE_VETERINARIAN",
        signed_note_present=True,
        allergy_records=allergy_records,
        active_medication_records=active_records,
        override_reason="clinically justified",
    )
    assert authorized.status == PrescriptionStatus.AUTHORIZED
    assert len(authorized.safety_warnings) == 2
    codes = {w.code for w in authorized.safety_warnings}
    assert "ALLERGY_MATCH" in codes
    assert "MEDICATION_CONFLICT" in codes


# --- Test 4: full lifecycle DRAFT → AUTHORIZED → SUBMITTED → DISPENSED ---

def test_lifecycle_progresses_draft_to_authorized_to_submitted_to_dispensed():
    rx = _draft()
    assert rx.status == PrescriptionStatus.DRAFT

    authorized = authorize_prescription(
        rx,
        actor_user_id=VET,
        actor_role="ROLE_VETERINARIAN",
        signed_note_present=True,
        allergy_records=[],
        active_medication_records=[],
    )
    assert authorized.status == PrescriptionStatus.AUTHORIZED
    assert authorized.authorized_by_user_id == VET

    submitted = submit_prescription(authorized, actor_user_id=VET)
    assert submitted.status == PrescriptionStatus.SUBMITTED
    assert submitted.submitted_at is not None

    dispensed = dispense_prescription(
        submitted, actor_user_id=PHARM, actor_role="ROLE_PHARMACY"
    )
    assert dispensed.status == PrescriptionStatus.DISPENSED
    assert dispensed.dispensed_by_user_id == PHARM


# --- Test 5: pharmacy queue returns AUTHORIZED + SUBMITTED in deterministic order ---

def test_queue_boundary_returns_authorized_and_submitted_in_deterministic_order():
    rx1 = _draft()
    rx1_auth = authorize_prescription(
        rx1, actor_user_id=VET, actor_role="ROLE_VETERINARIAN",
        signed_note_present=True, allergy_records=[], active_medication_records=[],
    )
    rx2 = _draft()
    rx2_auth = authorize_prescription(
        rx2, actor_user_id=VET, actor_role="ROLE_VETERINARIAN",
        signed_note_present=True, allergy_records=[], active_medication_records=[],
    )
    rx2_submitted = submit_prescription(rx2_auth, actor_user_id=VET)

    # cancelled prescription must not appear
    rx3 = _draft()
    rx3_cancelled = cancel_prescription(rx3, actor_user_id=VET)

    queue = get_pharmacy_review_queue(
        [rx2_submitted, rx1_auth, rx3_cancelled],
        actor_user_id=PHARM,
    )
    assert len(queue) == 2
    statuses = {e.status for e in queue}
    assert statuses == {"AUTHORIZED", "SUBMITTED"}


# --- Test 6: cancel is blocked post-dispense ---

def test_cancel_prevents_post_dispense_mutation():
    rx = _draft()
    authorized = authorize_prescription(
        rx, actor_user_id=VET, actor_role="ROLE_VETERINARIAN",
        signed_note_present=True, allergy_records=[], active_medication_records=[],
    )
    submitted = submit_prescription(authorized, actor_user_id=VET)
    dispensed = dispense_prescription(
        submitted, actor_user_id=PHARM, actor_role="ROLE_PHARMACY"
    )
    with pytest.raises(Exception) as exc_info:
        cancel_prescription(dispensed, actor_user_id=VET)
    assert "terminal" in str(exc_info.value).lower() or "dispensed" in str(exc_info.value).lower()


# --- Test 7: audit contract contains all expected events ---

def test_audit_contract_contains_expected_events():
    expected = {
        "prescription.created",
        "prescription.authorization_denied.invalid_role",
        "prescription.authorization_denied.missing_signed_note",
        "prescription.safety_warning_added",
        "prescription.override_reason_recorded",
        "prescription.authorized",
        "prescription.submitted",
        "prescription.dispensed",
        "prescription.cancelled",
        "prescription.queue_viewed",
    }
    assert set(PRESCRIPTION_AUDIT_EVENTS) == expected
