export const PARTNER_ONBOARDING_WORKFLOW = {
  workflowName: "partner_onboarding_workflow",
  steps: [
    "partner_identity_and_license_submission",
    "verification_review_recorded",
    "operational_profile_created",
    "access_activation_scoped",
    "onboarding_audit_log_recorded",
  ],
  partnerOnboardingWorkflowStatus: "pass",
  humanApprovalStillRequired: true,
} as const
