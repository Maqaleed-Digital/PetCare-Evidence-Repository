export const GOVERNANCE_REVIEW_AND_REPORTING_CYCLE = {
  governanceReviewAndReportingCycleStatus: "pass",
  checks: [
    "weekly_reporting_cycle_defined",
    "monthly_governance_review_defined",
    "incident_to_kpi_feedback_loop_active",
    "clinical_and_operations_review_cycle_active",
    "executive_reporting_visibility_enabled",
  ],
} as const
