export const LAUNCH_ACTIVATION_DECISION = {
  launchDecision: "CLINIC_LAUNCH_ACTIVATED",
  decisionRationale:
    "Clinic launch activation recorded after final go-live approval, full closure of launch limitations, and reconfirmation of governed operational and AI controls.",
  nextRecommendedState: "clinic_launch_live_operations",
} as const
