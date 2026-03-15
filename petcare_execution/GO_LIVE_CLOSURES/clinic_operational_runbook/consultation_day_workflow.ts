export const CONSULTATION_DAY_WORKFLOW = {
  workflowName: "consultation_day_workflow",
  steps: [
    "patient_check_in",
    "consultation_queue_review",
    "clinical_consultation_with_human_signoff",
    "documentation_review_and_finalize_by_vet",
    "prescription_or_follow_up_decision",
  ],
  consultationWorkflowStatus: "pass",
  humanApprovalStillRequired: true,
} as const
