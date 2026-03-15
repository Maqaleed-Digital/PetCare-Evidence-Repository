export const OVERRIDE_ANALYTICS = {
  pilotClinicId: "pilot_clinic_001",
  cohortId: "AI_PILOT_ALPHA",
  overrideDimensions: [
    "recommendation_replaced",
    "escalation_adjusted_by_human",
    "suggestion_rejected",
    "documentation_draft_corrected",
  ],
  overrideAnalyticsCompleted: true,
  humanOverrideAlwaysAvailable: true,
  overrideReasonCodesRequired: true,
  highRiskOverridePatternDetected: false,
} as const
