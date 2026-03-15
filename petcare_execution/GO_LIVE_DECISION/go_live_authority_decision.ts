export const GO_LIVE_AUTHORITY_DECISION = {
  authority: "PETCARE_GOVERNED_LAUNCH_AUTHORITY",
  allDecisionPrerequisitesSatisfied: true,
  goLiveDecision: "CLINIC_GO_LIVE_APPROVED",
  decisionRationale:
    "All launch-readiness limitations have been closed under governed controls, with AI assistive-only boundaries preserved and required human approvals still enforced.",
  nextRecommendedState: "proceed_to_clinic_launch_activation",
} as const
