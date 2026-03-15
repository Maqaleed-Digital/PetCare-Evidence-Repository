export const CONSULTATION_BILLING_WORKFLOW = {
  workflowName: "consultation_billing_workflow",
  steps: [
    "consultation_completion_confirmed",
    "billable_event_recorded",
    "invoice_generated",
    "payment_authorization_recorded",
    "payment_status_audit_logged",
  ],
  consultationBillingWorkflowStatus: "pass",
  humanApprovalStillRequired: true,
} as const
