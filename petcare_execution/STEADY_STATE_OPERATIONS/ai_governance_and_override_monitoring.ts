export const AI_GOVERNANCE_AND_OVERRIDE_MONITORING = {
  aiGovernanceAndOverrideMonitoringStatus: "pass",
  checks: [
    "assistive_only_boundary_preserved",
    "human_approval_enforced",
    "override_reason_capture_active",
    "live_governance_logging_active",
    "kill_switch_and_rollback_readiness_preserved",
  ],
  liveAiGovernanceState: "governed_override_monitoring_active",
} as const
