import { LAUNCH_READINESS_RECONFIRMATION } from "./launch_readiness_reconfirmation"
import { AI_GOVERNANCE_RECONFIRMATION } from "./ai_governance_reconfirmation"
import { CLINICAL_OPERATIONS_RECONFIRMATION } from "./clinical_operations_reconfirmation"
import { COMMERCIAL_OPERATIONS_RECONFIRMATION } from "./commercial_operations_reconfirmation"
import { GO_LIVE_AUTHORITY_DECISION } from "./go_live_authority_decision"

export function buildGoLiveDecisionValidationPack() {
  const requiredSymbolsConfirmed =
    LAUNCH_READINESS_RECONFIRMATION.launchReadinessReconfirmed === true &&
    AI_GOVERNANCE_RECONFIRMATION.aiGovernanceReconfirmed === true &&
    CLINICAL_OPERATIONS_RECONFIRMATION.clinicalOperationsReconfirmed === true &&
    COMMERCIAL_OPERATIONS_RECONFIRMATION.commercialOperationsReconfirmed === true &&
    typeof GO_LIVE_AUTHORITY_DECISION.goLiveDecision === "string"

  return {
    packId: "PETCARE-CLINIC-GO-LIVE-DECISION",
    requiredSymbolsConfirmed,
    launchReadinessReconfirmed:
      LAUNCH_READINESS_RECONFIRMATION.launchReadinessReconfirmed,
    aiGovernanceReconfirmed:
      AI_GOVERNANCE_RECONFIRMATION.aiGovernanceReconfirmed,
    clinicalOperationsReconfirmed:
      CLINICAL_OPERATIONS_RECONFIRMATION.clinicalOperationsReconfirmed,
    commercialOperationsReconfirmed:
      COMMERCIAL_OPERATIONS_RECONFIRMATION.commercialOperationsReconfirmed,
    goLiveDecisionPresent:
      typeof GO_LIVE_AUTHORITY_DECISION.goLiveDecision === "string",
    goLiveDecision: GO_LIVE_AUTHORITY_DECISION.goLiveDecision,
    nextRecommendedState:
      GO_LIVE_AUTHORITY_DECISION.nextRecommendedState,
  } as const
}
