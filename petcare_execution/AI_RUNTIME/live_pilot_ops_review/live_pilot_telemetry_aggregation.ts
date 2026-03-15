export const LIVE_PILOT_TELEMETRY_AGGREGATION = {
  pilotClinicId: "pilot_clinic_001",
  cohortId: "AI_PILOT_ALPHA",
  reviewWindow: "first_cohort_review_window",
  surfaces: [
    "consultation",
    "triage",
    "pharmacy_review",
    "emergency",
  ],
  metricsTracked: [
    "sessionsReviewed",
    "assistiveSuggestionsGenerated",
    "humanApprovalsRecorded",
    "overrideEventsRecorded",
    "escalationsTriggered",
    "killSwitchAvailabilityChecks",
    "rollbackReadinessChecks",
  ],
  telemetryAggregationCompleted: true,
  assistiveOnlyBoundaryPreserved: true,
  humanApprovalStillRequired: true,
} as const
