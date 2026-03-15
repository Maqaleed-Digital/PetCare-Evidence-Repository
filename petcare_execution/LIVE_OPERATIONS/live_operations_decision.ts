export const LIVE_OPERATIONS_DECISION = {
  liveOperationsDecision: "CLINIC_LIVE_OPERATIONS_ACTIVE",
  decisionRationale:
    "Clinic launch is activated and all monitored live operational domains remain active under governed assistive-only and human-controlled conditions.",
  nextRecommendedState: "steady_state_live_operations_management",
} as const
