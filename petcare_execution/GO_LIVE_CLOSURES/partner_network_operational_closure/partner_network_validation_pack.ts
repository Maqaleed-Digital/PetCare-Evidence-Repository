import { PARTNER_NETWORK_READINESS } from "./partner_network_readiness"
import { PARTNER_ONBOARDING_WORKFLOW } from "./partner_onboarding_workflow"
import { SLA_OPERATIONAL_CONTROLS } from "./sla_operational_controls"
import { ORDER_REFERRAL_ROUTING_WORKFLOW } from "./order_referral_routing_workflow"
import { PARTNER_ACCESS_RBAC_VERIFICATION } from "./partner_access_rbac_verification"
import { PARTNER_NETWORK_CLOSURE_DECISION } from "./partner_network_closure_decision"

export function buildPartnerNetworkValidationPack() {
  const requiredSymbolsConfirmed =
    PARTNER_NETWORK_READINESS.partnerNetworkStatus === "COMPLETE" &&
    PARTNER_ONBOARDING_WORKFLOW.partnerOnboardingWorkflowStatus === "pass" &&
    SLA_OPERATIONAL_CONTROLS.slaOperationalControlsStatus === "pass" &&
    ORDER_REFERRAL_ROUTING_WORKFLOW.orderReferralRoutingStatus === "pass" &&
    PARTNER_ACCESS_RBAC_VERIFICATION.partnerRBACVerificationStatus === "pass" &&
    typeof PARTNER_NETWORK_CLOSURE_DECISION.closureDecision === "string"

  return {
    packId: "PETCARE-GO-LIVE-CLOSURE-4",
    requiredSymbolsConfirmed,
    partnerNetworkStatus: PARTNER_NETWORK_READINESS.partnerNetworkStatus,
    partnerOnboardingWorkflowStatus:
      PARTNER_ONBOARDING_WORKFLOW.partnerOnboardingWorkflowStatus,
    slaOperationalControlsStatus:
      SLA_OPERATIONAL_CONTROLS.slaOperationalControlsStatus,
    orderReferralRoutingStatus:
      ORDER_REFERRAL_ROUTING_WORKFLOW.orderReferralRoutingStatus,
    partnerRBACVerificationStatus:
      PARTNER_ACCESS_RBAC_VERIFICATION.partnerRBACVerificationStatus,
    assistiveOnlyBoundaryPreserved:
      PARTNER_NETWORK_READINESS.assistiveOnlyBoundaryPreserved,
    humanApprovalStillRequired:
      PARTNER_NETWORK_READINESS.humanApprovalStillRequired &&
      PARTNER_ONBOARDING_WORKFLOW.humanApprovalStillRequired &&
      ORDER_REFERRAL_ROUTING_WORKFLOW.regulatedActionHumanControlled,
    closureDecisionPresent:
      typeof PARTNER_NETWORK_CLOSURE_DECISION.closureDecision === "string",
    closureDecision: PARTNER_NETWORK_CLOSURE_DECISION.closureDecision,
    nextRecommendedState:
      PARTNER_NETWORK_CLOSURE_DECISION.nextRecommendedState,
  } as const
}
