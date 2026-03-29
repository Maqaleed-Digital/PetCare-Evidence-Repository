from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Sequence

from .models import (
    ROLE_PHARMACY,
    Prescription,
    PrescriptionQueueEntry,
    PrescriptionSafetyWarning,
    PrescriptionStatus,
)


PHARMACY_REVIEW_AUDIT_EVENTS: tuple[str, ...] = (
    "prescription.review.read_model_viewed",
    "prescription.review.list_viewed",
    "prescription.review.decision_recorded",
)

PHARMACY_REVIEW_DECISIONS: tuple[str, ...] = (
    "APPROVE_FOR_DISPENSE_QUEUE",
    "ACKNOWLEDGE_WARNINGS",
    "RETURN_TO_VET_REVIEW",
)


@dataclass(frozen=True)
class DoseContext:
    species: str
    breed: str
    age_months: int
    weight_kg: float
    dose_band: str

    def to_dict(self) -> dict[str, object]:
        return {
            "species": self.species,
            "breed": self.breed,
            "age_months": self.age_months,
            "weight_kg": self.weight_kg,
            "dose_band": self.dose_band,
        }


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().split())


def build_dose_context(
    *,
    species: str,
    breed: str,
    age_months: int,
    weight_kg: float,
) -> DoseContext:
    if age_months < 0:
        raise ValueError("age_months must be >= 0")
    if weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")

    if age_months < 12 and weight_kg < 10:
        dose_band = "JUVENILE_LIGHT"
    elif weight_kg < 10:
        dose_band = "ADULT_LIGHT"
    elif weight_kg < 25:
        dose_band = "STANDARD"
    else:
        dose_band = "LARGE"

    return DoseContext(
        species=species,
        breed=breed,
        age_months=age_months,
        weight_kg=weight_kg,
        dose_band=dose_band,
    )


def evaluate_medication_safety_rules(
    prescription: Prescription,
    *,
    species: str,
    breed: str,
    age_months: int,
    weight_kg: float,
    known_contraindications: Iterable[str] = (),
) -> tuple[PrescriptionSafetyWarning, ...]:
    context = build_dose_context(
        species=species,
        breed=breed,
        age_months=age_months,
        weight_kg=weight_kg,
    )

    warnings: list[PrescriptionSafetyWarning] = []

    dosage_text = _normalize(prescription.dosage_instructions)
    medication_text = _normalize(prescription.medication_name)

    if context.dose_band in ("JUVENILE_LIGHT", "ADULT_LIGHT") and "high" in dosage_text:
        warnings.append(
            PrescriptionSafetyWarning(
                code="DOSE_MATRIX_GUARDRAIL",
                severity="MEDIUM",
                message=(
                    f"Dose context '{context.dose_band}' indicates manual verification for "
                    f"medication '{prescription.medication_name}'."
                ),
            )
        )

    for item in known_contraindications:
        normalized = _normalize(item)
        if normalized and normalized in medication_text:
            warnings.append(
                PrescriptionSafetyWarning(
                    code="CONTRAINDICATION_CONTEXT",
                    severity="HIGH",
                    message=(
                        f"Known contraindication context '{item}' matched medication "
                        f"'{prescription.medication_name}'."
                    ),
                )
            )

    unique: dict[tuple[str, str, str], PrescriptionSafetyWarning] = {}
    for warning in warnings:
        unique[(warning.code, warning.severity, warning.message)] = warning
    return tuple(unique.values())


def apply_wave03_safety_rules(
    prescription: Prescription,
    *,
    species: str,
    breed: str,
    age_months: int,
    weight_kg: float,
    known_contraindications: Iterable[str] = (),
) -> Prescription:
    additive = evaluate_medication_safety_rules(
        prescription,
        species=species,
        breed=breed,
        age_months=age_months,
        weight_kg=weight_kg,
        known_contraindications=known_contraindications,
    )

    existing = {
        (warning.code, warning.severity, warning.message): warning
        for warning in prescription.safety_warnings
    }
    for warning in additive:
        existing[(warning.code, warning.severity, warning.message)] = warning

    return replace(prescription, safety_warnings=tuple(existing.values()))


def get_pharmacy_review_read_model(prescription: Prescription) -> dict[str, object]:
    return {
        "prescription_id": prescription.prescription_id,
        "consultation_id": prescription.consultation_id,
        "pet_id": prescription.pet_id,
        "tenant_id": prescription.tenant_id,
        "status": prescription.status.value,
        "medication_name": prescription.medication_name,
        "warning_codes": sorted({warning.code for warning in prescription.safety_warnings}),
        "warning_count": len(prescription.safety_warnings),
        "authorized_at": prescription.authorized_at,
        "submitted_at": prescription.submitted_at,
        "reviewable": prescription.status in (PrescriptionStatus.AUTHORIZED, PrescriptionStatus.SUBMITTED),
    }


def list_reviewable_prescriptions(
    prescriptions: Sequence[Prescription],
) -> list[PrescriptionQueueEntry]:
    reviewable = [
        prescription
        for prescription in prescriptions
        if prescription.status in (PrescriptionStatus.AUTHORIZED, PrescriptionStatus.SUBMITTED)
    ]
    ordered = sorted(
        reviewable,
        key=lambda prescription: (
            prescription.authorized_at or "",
            prescription.submitted_at or "",
            prescription.prescription_id,
        ),
    )
    return [
        PrescriptionQueueEntry(
            prescription_id=prescription.prescription_id,
            tenant_id=prescription.tenant_id,
            pet_id=prescription.pet_id,
            consultation_id=prescription.consultation_id,
            medication_name=prescription.medication_name,
            status=prescription.status.value,
            authorized_at=prescription.authorized_at,
            submitted_at=prescription.submitted_at,
            warning_count=len(prescription.safety_warnings),
        )
        for prescription in ordered
    ]


def record_pharmacy_review_decision(
    prescription: Prescription,
    *,
    actor_user_id: str,
    actor_role: str,
    decision: str,
    review_note: str,
) -> Prescription:
    if actor_role != ROLE_PHARMACY:
        raise PermissionError("Pharmacy operator role is required for review decisions.")

    if prescription.status not in (PrescriptionStatus.AUTHORIZED, PrescriptionStatus.SUBMITTED):
        raise ValueError("Only AUTHORIZED or SUBMITTED prescriptions may receive pharmacy review decisions.")

    if decision not in PHARMACY_REVIEW_DECISIONS:
        raise ValueError("Unsupported pharmacy review decision.")

    updated = prescription.with_event(
        "prescription.review.decision_recorded",
        actor_user_id,
        {
            "decision": decision,
            "review_note": review_note,
            "status": prescription.status.value,
        },
    )
    return updated


__all__ = [
    "DoseContext",
    "PHARMACY_REVIEW_AUDIT_EVENTS",
    "PHARMACY_REVIEW_DECISIONS",
    "apply_wave03_safety_rules",
    "build_dose_context",
    "evaluate_medication_safety_rules",
    "get_pharmacy_review_read_model",
    "list_reviewable_prescriptions",
    "record_pharmacy_review_decision",
]
