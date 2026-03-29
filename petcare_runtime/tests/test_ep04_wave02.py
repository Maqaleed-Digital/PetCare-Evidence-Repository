"""EP-04 Wave 02: advisory safety extensions and read model — unit tests."""
import pytest

from petcare.pharmacy.service import (
    authorize_prescription,
    create_prescription,
    extend_safety_warnings,
    get_prescription_read_model,
    list_prescriptions,
)
from petcare.pharmacy.models import ROLE_VETERINARIAN


def _draft(medication_name="TestMed", dosage_instructions="normal dose"):
    return create_prescription(
        tenant_id="t",
        pet_id="p",
        consultation_id="c",
        signed_note_id="n",
        medication_code="m",
        medication_name=medication_name,
        dosage_instructions=dosage_instructions,
        quantity="1",
        created_by_user_id="u",
    )


def _authorize(rx):
    return authorize_prescription(
        rx,
        actor_user_id="vet",
        actor_role=ROLE_VETERINARIAN,
        signed_note_present=True,
        allergy_records=[],
        active_medication_records=[],
    )


# --- Test 1: dose guardrail warning added when dosage contains "high" ---

def test_dose_guardrail_warning():
    rx = _draft(dosage_instructions="HIGH dose twice daily")
    rx = _authorize(rx)
    rx = extend_safety_warnings(rx)
    assert any(w.code == "DOSE_GUARDRAIL" for w in rx.safety_warnings)


# --- Test 2: dose guardrail not added for normal dosage ---

def test_dose_guardrail_not_added_for_normal_dosage():
    rx = _draft(dosage_instructions="1 tablet once daily")
    rx = _authorize(rx)
    rx = extend_safety_warnings(rx)
    assert not any(w.code == "DOSE_GUARDRAIL" for w in rx.safety_warnings)


# --- Test 3: contraindication warning added for steroid ---

def test_contraindication_warning_for_steroid():
    rx = _draft(medication_name="Prednisone steroid 5mg")
    rx = _authorize(rx)
    rx = extend_safety_warnings(rx)
    assert any(w.code == "CONTRAINDICATION" for w in rx.safety_warnings)


# --- Test 4: contraindication warning not added for non-steroid ---

def test_no_contraindication_for_non_steroid():
    rx = _draft(medication_name="Amoxicillin 250mg")
    rx = _authorize(rx)
    rx = extend_safety_warnings(rx)
    assert not any(w.code == "CONTRAINDICATION" for w in rx.safety_warnings)


# --- Test 5: read model is deterministic and contains required fields ---

def test_read_model_deterministic():
    rx = _draft()
    rm = get_prescription_read_model(rx)
    assert rm["prescription_id"] is not None
    assert rm["status"] == "DRAFT"
    assert "audit_trail" in rm
    assert "safety_warnings" in rm


# --- Test 6: list_prescriptions returns sorted read models ---

def test_list_prescriptions_sorted():
    rx1 = _draft()
    rx2 = _draft()
    result = list_prescriptions([rx2, rx1])
    assert len(result) == 2
    assert result[0]["created_at"] <= result[1]["created_at"]
