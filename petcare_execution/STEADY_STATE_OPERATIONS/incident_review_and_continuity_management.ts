export const INCIDENT_REVIEW_AND_CONTINUITY_MANAGEMENT = {
  incidentReviewAndContinuityManagementStatus: "pass",
  checks: [
    "incident_review_cycle_active",
    "emergency_escalation_review_path_active",
    "shift_handover_review_cycle_active",
    "continuity_contact_path_active",
    "operational_risk_review_visibility_enabled",
  ],
} as const
