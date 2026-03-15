export const REGULATORY_READINESS_REVIEW = {
  status: "pass",
  checks: [
    "consent_and_privacy_controls_present",
    "auditability_preserved",
    "data_residency_architecture_baseline_present",
    "human_review_for_regulated_actions_preserved",
    "regulatory_governance_traceability_present",
  ],
  unresolvedRegulatoryBlockerCount: 0,
} as const
