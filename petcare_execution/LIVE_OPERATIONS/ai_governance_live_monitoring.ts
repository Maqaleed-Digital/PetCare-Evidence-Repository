export const AI_GOVERNANCE_LIVE_MONITORING = {
  aiGovernanceLiveMonitoringStatus: "pass",
  checks: [
    "assistive_only_boundary_preserved",
    "human_approval_enforced",
    "governed_logging_active",
    "kill_switch_available",
    "rollback_available",
  ],
  liveAiState: "governed_assistive_operations_active",
} as const
