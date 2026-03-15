export const CLINICAL_FEEDBACK_REVIEW = {
  pilotClinicId: "pilot_clinic_001",
  cohortId: "AI_PILOT_ALPHA",
  stakeholdersReviewed: [
    "veterinarians",
    "triage_operators",
    "pharmacy_review_staff",
    "emergency_coordination_staff",
  ],
  reviewFocus: [
    "clinical usefulness",
    "workflow fit",
    "clarity of assistive recommendations",
    "appropriateness of escalation prompts",
    "human approval burden",
  ],
  clinicalFeedbackReviewed: true,
  approvalBoundaryConfirmed: true,
  unresolvedSafetyConcernCount: 0,
} as const
