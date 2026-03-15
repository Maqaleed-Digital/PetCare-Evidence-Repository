export const SCALE_READINESS_GOVERNANCE = {
  scaleReadinessGovernanceStatus: "pass",
  checks: [
    "multi_clinic_readiness_review_path_defined",
    "service_capacity_review_visibility_enabled",
    "governance_scaling_controls_defined",
    "partner_network_scaling_review_defined",
    "operating_model_scale_review_active",
  ],
} as const
