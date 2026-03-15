import { LIVE_PILOT_TELEMETRY_AGGREGATION } from "./live_pilot_telemetry_aggregation"
import { CLINICAL_FEEDBACK_REVIEW } from "./clinical_feedback_review"
import { OVERRIDE_ANALYTICS } from "./override_analytics"
import { SAFETY_REVIEW_CHECKPOINT } from "./safety_review_checkpoint"
import { PILOT_COHORT_CLOSURE_DECISION } from "./pilot_cohort_closure_decision"

export function buildLivePilotOpsReviewValidationPack() {
  const requiredSymbolsConfirmed =
    LIVE_PILOT_TELEMETRY_AGGREGATION.telemetryAggregationCompleted &&
    CLINICAL_FEEDBACK_REVIEW.clinicalFeedbackReviewed &&
    OVERRIDE_ANALYTICS.overrideAnalyticsCompleted &&
    SAFETY_REVIEW_CHECKPOINT.safetyCheckpointStatus === "pass" &&
    typeof PILOT_COHORT_CLOSURE_DECISION.cohortClosureDecision === "string"

  return {
    packId: "PETCARE-AI-LIVE-2",
    pilotClinicId: "pilot_clinic_001",
    cohortId: "AI_PILOT_ALPHA",
    requiredSymbolsConfirmed,
    telemetryAggregationCompleted:
      LIVE_PILOT_TELEMETRY_AGGREGATION.telemetryAggregationCompleted,
    clinicalFeedbackReviewed:
      CLINICAL_FEEDBACK_REVIEW.clinicalFeedbackReviewed,
    overrideAnalyticsCompleted:
      OVERRIDE_ANALYTICS.overrideAnalyticsCompleted,
    safetyCheckpointStatus:
      SAFETY_REVIEW_CHECKPOINT.safetyCheckpointStatus,
    assistiveOnlyBoundaryPreserved:
      LIVE_PILOT_TELEMETRY_AGGREGATION.assistiveOnlyBoundaryPreserved &&
      SAFETY_REVIEW_CHECKPOINT.assistiveOnlyBoundaryPreserved,
    humanApprovalStillRequired:
      LIVE_PILOT_TELEMETRY_AGGREGATION.humanApprovalStillRequired &&
      SAFETY_REVIEW_CHECKPOINT.humanApprovalStillRequired &&
      OVERRIDE_ANALYTICS.humanOverrideAlwaysAvailable,
    cohortClosureDecisionPresent:
      typeof PILOT_COHORT_CLOSURE_DECISION.cohortClosureDecision === "string",
    cohortClosureDecision:
      PILOT_COHORT_CLOSURE_DECISION.cohortClosureDecision,
    nextRecommendedState:
      PILOT_COHORT_CLOSURE_DECISION.nextRecommendedState,
  } as const
}
