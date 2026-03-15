export const CLINICAL_READINESS_REVIEW = {
  status: "pass",
  checks: [
    "clinical_protocols_defined",
    "vet_signoff_immutability_preserved",
    "triage_escalation_rules_active",
    "medication_safety_controls_active",
    "emergency_referral_workflow_preserved",
  ],
  unresolvedClinicalSafetyConcernCount: 0,
  humanApprovalStillRequired: true,
  assistiveOnlyBoundaryPreserved: true,
} as const
