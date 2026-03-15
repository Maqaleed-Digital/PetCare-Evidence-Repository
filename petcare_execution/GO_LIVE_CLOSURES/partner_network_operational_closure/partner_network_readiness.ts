export const PARTNER_NETWORK_READINESS = {
  partnerNetworkStatus: "COMPLETE",
  coveredDomains: [
    "partner_onboarding_workflow",
    "sla_operational_controls",
    "order_referral_routing_workflow",
    "partner_access_rbac_verification",
  ],
  assistiveOnlyBoundaryPreserved: true,
  humanApprovalStillRequired: true,
} as const
