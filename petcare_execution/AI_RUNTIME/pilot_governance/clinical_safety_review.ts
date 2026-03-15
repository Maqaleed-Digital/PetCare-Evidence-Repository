export interface ClinicalSafetyReview {
  clinicId: string
  reviewBoard: string
  approved: boolean
  notes?: string
  assistiveOnly: true
}

export const CLINICAL_SAFETY_REVIEWS: ClinicalSafetyReview[] = [
  {
    clinicId: "pilot_clinic_001",
    reviewBoard: "PetCare Clinical Safety Board",
    approved: true,
    assistiveOnly: true
  }
]
