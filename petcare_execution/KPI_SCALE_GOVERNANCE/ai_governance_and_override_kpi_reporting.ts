export const AI_GOVERNANCE_AND_OVERRIDE_KPI_REPORTING = {
  aiGovernanceAndOverrideKpiReportingStatus: "pass",
  metrics: [
    "override_rate_reporting_active",
    "assistive_only_boundary_reporting_active",
    "human_approval_compliance_reporting_active",
    "live_governance_logging_reporting_active",
    "kill_switch_and_rollback_readiness_reporting_active",
  ],
  governanceState: "governed_ai_kpi_reporting_active",
} as const
