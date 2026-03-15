export const PHARMACY_HANDOFF_WORKFLOW = {
  workflowName: "pharmacy_handoff_workflow",
  steps: [
    "approved_prescription_received",
    "pharmacy_operator_review",
    "dispense_or_hold_decision_by_authorized_operator",
    "audit_log_recorded",
    "owner_handoff_or_delivery_preparation",
  ],
  pharmacyHandoffWorkflowStatus: "pass",
  regulatedActionHumanControlled: true,
} as const
