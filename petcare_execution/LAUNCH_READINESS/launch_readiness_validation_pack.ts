import { CLINICAL_READINESS_REVIEW } from "./clinical_readiness_review"
import { OPERATIONAL_READINESS_REVIEW } from "./operational_readiness_review"
import { TECHNOLOGY_READINESS_REVIEW } from "./technology_readiness_review"
import { REGULATORY_READINESS_REVIEW } from "./regulatory_readiness_review"
import { COMMERCIAL_READINESS_REVIEW } from "./commercial_readiness_review"
import { LAUNCH_READINESS_SCORECARD } from "./launch_readiness_scorecard"

export function buildLaunchReadinessValidationPack() {
  const requiredSymbolsConfirmed =
    CLINICAL_READINESS_REVIEW.status === "pass" &&
    typeof OPERATIONAL_READINESS_REVIEW.status === "string" &&
    TECHNOLOGY_READINESS_REVIEW.status === "pass" &&
    REGULATORY_READINESS_REVIEW.status === "pass" &&
    typeof COMMERCIAL_READINESS_REVIEW.status === "string" &&
    typeof LAUNCH_READINESS_SCORECARD.launchDecision === "string"

  return {
    packId: "PETCARE-LAUNCH-READINESS",
    requiredSymbolsConfirmed,
    clinicalReadinessStatus: CLINICAL_READINESS_REVIEW.status,
    operationalReadinessStatus: OPERATIONAL_READINESS_REVIEW.status,
    technologyReadinessStatus: TECHNOLOGY_READINESS_REVIEW.status,
    regulatoryReadinessStatus: REGULATORY_READINESS_REVIEW.status,
    commercialReadinessStatus: COMMERCIAL_READINESS_REVIEW.status,
    assistiveOnlyBoundaryPreserved:
      CLINICAL_READINESS_REVIEW.assistiveOnlyBoundaryPreserved === true,
    humanApprovalStillRequired:
      CLINICAL_READINESS_REVIEW.humanApprovalStillRequired === true,
    launchDecisionPresent:
      typeof LAUNCH_READINESS_SCORECARD.launchDecision === "string",
    launchDecision: LAUNCH_READINESS_SCORECARD.launchDecision,
    launchLimitationsDocumented:
      LAUNCH_READINESS_SCORECARD.launchLimitations.length > 0,
    nextRecommendedState:
      LAUNCH_READINESS_SCORECARD.nextRecommendedState,
  } as const
}
