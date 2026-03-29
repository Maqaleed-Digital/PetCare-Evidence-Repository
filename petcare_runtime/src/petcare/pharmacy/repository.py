from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .models import Prescription
from .review import PharmacyReviewRecord


@dataclass
class PharmacyRepository:
    prescriptions: Dict[str, Prescription]
    reviews: Dict[str, PharmacyReviewRecord]

    def add_prescription(self, prescription: Prescription) -> None:
        self.prescriptions[prescription.prescription_id] = prescription

    def add_review(self, review: PharmacyReviewRecord) -> None:
        self.reviews[review.review_id] = review

    def get_prescription(self, prescription_id: str) -> Prescription:
        return self.prescriptions[prescription_id]

    def get_review(self, review_id: str) -> PharmacyReviewRecord:
        return self.reviews[review_id]

    def list_reviews_by_prescription_id(self, prescription_id: str) -> List[PharmacyReviewRecord]:
        return sorted(
            [r for r in self.reviews.values() if r.prescription_id == prescription_id],
            key=lambda r: (r.created_at, r.review_id),
        )

    def list_reviews_by_consultation_id(self, consultation_id: str) -> List[PharmacyReviewRecord]:
        return sorted(
            [r for r in self.reviews.values() if r.consultation_id == consultation_id],
            key=lambda r: (r.created_at, r.review_id),
        )

    def list_reviews_by_tenant_id(self, tenant_id: str) -> List[PharmacyReviewRecord]:
        return sorted(
            [r for r in self.reviews.values() if r.tenant_id == tenant_id],
            key=lambda r: (r.created_at, r.review_id),
        )
