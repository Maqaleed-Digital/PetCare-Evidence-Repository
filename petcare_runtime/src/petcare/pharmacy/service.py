from __future__ import annotations
from dataclasses import replace
from typing import Any

from .models import (
    ROLE_PHARMACY,
    ROLE_VETERINARIAN,
    Prescription,
    PrescriptionQueueEntry,
    PrescriptionSafetyWarning,
    PrescriptionStatus,
    new_prescription_id,
    utc_now,
)


class PrescriptionStateError(ValueError):
    pass


def create_prescription(
    *,
    tenant_id: str,
    pet_id: str,
    consultation_id: str,
    signed_note_id: str,
    medication_code: str,
    medication_name: str,
    dosage_instructions: str,
    quantity: str,
    created_by_user_id: str,
    ai_contribution: str | None = None,
) -> Prescription:
    rx = Prescription(
        prescription_id=new_prescription_id(),
        tenant_id=tenant_id,
        pet_id=pet_id,
        consultation_id=consultation_id,
        signed_note_id=signed_note_id,
        medication_code=medication_code,
        medication_name=medication_name,
        dosage_instructions=dosage_instructions,
        quantity=quantity,
        status=PrescriptionStatus.DRAFT,
        created_by_user_id=created_by_user_id,
        created_at=utc_now(),
        ai_contribution=ai_contribution,
        safety_warnings=(),
        audit_trail=(),
    )
    return rx.with_event("prescription.created", actor_user_id=created_by_user_id)


def _build_safety_warnings(
    medication_code: str,
    allergy_records: list[dict],
    active_medication_records: list[dict],
) -> list[PrescriptionSafetyWarning]:
    warnings: list[PrescriptionSafetyWarning] = []
    for record in allergy_records:
        if record.get("allergen_code") == medication_code:
            warnings.append(
                PrescriptionSafetyWarning(
                    code="ALLERGY_MATCH",
                    severity="HIGH",
                    message=f"Pet has recorded allergy to {medication_code}",
                )
            )
    for record in active_medication_records:
        if record.get("medication_code") == medication_code:
            warnings.append(
                PrescriptionSafetyWarning(
                    code="MEDICATION_CONFLICT",
                    severity="MEDIUM",
                    message=f"Active medication conflict detected for {medication_code}",
                )
            )
    return warnings


def authorize_prescription(
    prescription: Prescription,
    *,
    actor_user_id: str,
    actor_role: str,
    signed_note_present: bool,
    allergy_records: list[dict],
    active_medication_records: list[dict],
    override_reason: str | None = None,
) -> Prescription:
    if actor_role != ROLE_VETERINARIAN:
        rx = prescription.with_event(
            "prescription.authorization_denied.invalid_role",
            actor_user_id=actor_user_id,
        )
        raise PermissionError("authorization requires ROLE_VETERINARIAN")

    if prescription.status != PrescriptionStatus.DRAFT:
        raise PrescriptionStateError(
            f"prescription must be DRAFT to authorize; current status: {prescription.status.value}"
        )

    if not signed_note_present:
        rx = prescription.with_event(
            "prescription.authorization_denied.missing_signed_note",
            actor_user_id=actor_user_id,
        )
        raise PrescriptionStateError("authorization requires a signed consultation note")

    warnings = _build_safety_warnings(
        prescription.medication_code,
        allergy_records,
        active_medication_records,
    )

    rx = prescription
    for warning in warnings:
        rx = rx.with_event(
            "prescription.safety_warning_added",
            actor_user_id=actor_user_id,
            details=warning.to_dict(),
        )

    if override_reason is not None:
        rx = rx.with_event(
            "prescription.override_reason_recorded",
            actor_user_id=actor_user_id,
            details={"override_reason": override_reason},
        )

    rx = replace(
        rx,
        status=PrescriptionStatus.AUTHORIZED,
        authorized_by_user_id=actor_user_id,
        authorized_at=utc_now(),
        safety_warnings=tuple(warnings),
        override_reason=override_reason,
    )
    return rx.with_event("prescription.authorized", actor_user_id=actor_user_id)


def submit_prescription(
    prescription: Prescription,
    *,
    actor_user_id: str,
) -> Prescription:
    if prescription.status != PrescriptionStatus.AUTHORIZED:
        raise PrescriptionStateError(
            f"prescription must be AUTHORIZED to submit; current status: {prescription.status.value}"
        )
    rx = replace(prescription, status=PrescriptionStatus.SUBMITTED, submitted_at=utc_now())
    return rx.with_event("prescription.submitted", actor_user_id=actor_user_id)


def dispense_prescription(
    prescription: Prescription,
    *,
    actor_user_id: str,
    actor_role: str,
) -> Prescription:
    if actor_role != ROLE_PHARMACY:
        raise PermissionError("dispense requires ROLE_PHARMACY")
    if prescription.status != PrescriptionStatus.SUBMITTED:
        raise PrescriptionStateError(
            f"prescription must be SUBMITTED to dispense; current status: {prescription.status.value}"
        )
    rx = replace(
        prescription,
        status=PrescriptionStatus.DISPENSED,
        dispensed_by_user_id=actor_user_id,
        dispensed_at=utc_now(),
    )
    return rx.with_event("prescription.dispensed", actor_user_id=actor_user_id)


def cancel_prescription(
    prescription: Prescription,
    *,
    actor_user_id: str,
) -> Prescription:
    if prescription.status in (PrescriptionStatus.DISPENSED, PrescriptionStatus.CANCELLED):
        raise PrescriptionStateError(
            f"cannot cancel a prescription in terminal state: {prescription.status.value}"
        )
    rx = replace(prescription, status=PrescriptionStatus.CANCELLED, cancelled_at=utc_now())
    return rx.with_event("prescription.cancelled", actor_user_id=actor_user_id)


def get_pharmacy_review_queue(
    prescriptions: list[Prescription],
    *,
    actor_user_id: str,
) -> list[PrescriptionQueueEntry]:
    eligible = [
        p for p in prescriptions
        if p.status in (PrescriptionStatus.AUTHORIZED, PrescriptionStatus.SUBMITTED)
    ]
    eligible.sort(
        key=lambda p: (
            p.authorized_at or "",
            p.submitted_at or "",
            p.prescription_id,
        )
    )
    return [
        PrescriptionQueueEntry(
            prescription_id=p.prescription_id,
            tenant_id=p.tenant_id,
            pet_id=p.pet_id,
            consultation_id=p.consultation_id,
            medication_name=p.medication_name,
            status=p.status.value,
            authorized_at=p.authorized_at,
            submitted_at=p.submitted_at,
            warning_count=len(p.safety_warnings),
        )
        for p in eligible
    ]
