import { CLINICAL_READINESS_REVIEW } from "./clinical_readiness_review"
import { OPERATIONAL_READINESS_REVIEW } from "./operational_readiness_review"
import { TECHNOLOGY_READINESS_REVIEW } from "./technology_readiness_review"
import { REGULATORY_READINESS_REVIEW } from "./regulatory_readiness_review"
import { COMMERCIAL_READINESS_REVIEW } from "./commercial_readiness_review"

export const LAUNCH_READINESS_SCORECARD = {
  packId: "PETCARE-LAUNCH-READINESS",
  clinicalReadinessStatus: CLINICAL_READINESS_REVIEW.status,
  operationalReadinessStatus: OPERATIONAL_READINESS_REVIEW.status,
  technologyReadinessStatus: TECHNOLOGY_READINESS_REVIEW.status,
  regulatoryReadinessStatus: REGULATORY_READINESS_REVIEW.status,
  commercialReadinessStatus: COMMERCIAL_READINESS_REVIEW.status,
  launchLimitations: [
    ...OPERATIONAL_READINESS_REVIEW.launchLimitations,
    ...COMMERCIAL_READINESS_REVIEW.launchLimitations,
  ],
  launchDecision: "READY_WITH_LIMITATIONS",
  nextRecommendedState: "close_launch_limitations_and_prepare_clinic_go_live",
} as const
