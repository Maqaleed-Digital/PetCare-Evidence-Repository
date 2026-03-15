export const NETWORK_RISK_AND_COMPLIANCE_GOVERNANCE = {
  networkRiskAndComplianceGovernanceStatus: "pass",
  checks: [
    "network_level_risk_review_defined",
    "clinic_to_portfolio_compliance_reporting_defined",
    "audit_sampling_model_defined",
    "incident_rollup_and_escalation_defined",
    "regulatory_visibility_controls_enabled",
  ],
} as const
