export const PILOT_COHORT_CLOSURE_DECISION = {
  pilotClinicId: "pilot_clinic_001",
  cohortId: "AI_PILOT_ALPHA",
  decisionInputs: [
    "telemetryAggregationCompleted",
    "clinicalFeedbackReviewed",
    "overrideAnalyticsCompleted",
    "safetyCheckpointStatus",
    "assistiveOnlyBoundaryPreserved",
    "humanApprovalStillRequired",
  ],
  cohortClosureDecision: "READY_FOR_COHORT_CLOSURE",
  rationale:
    "Pilot review complete with preserved assistive-only controls, active human approval, completed telemetry aggregation, completed override review, and passing safety checkpoint.",
  nextRecommendedState: "ready_for_launch_readiness_pack",
} as const
