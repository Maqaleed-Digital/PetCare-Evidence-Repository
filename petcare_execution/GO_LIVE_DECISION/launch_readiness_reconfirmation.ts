export const LAUNCH_READINESS_RECONFIRMATION = {
  launchReadinessReconfirmed: true,
  readinessPillars: [
    "clinical",
    "technology",
    "regulatory",
    "operational",
    "commercial",
  ],
  priorDecisionSuperseded: "READY_WITH_LIMITATIONS",
  currentReadinessState: "ALL_LIMITATIONS_CLOSED",
} as const
