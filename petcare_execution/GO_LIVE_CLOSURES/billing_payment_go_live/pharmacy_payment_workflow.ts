export const PHARMACY_PAYMENT_WORKFLOW = {
  workflowName: "pharmacy_payment_workflow",
  steps: [
    "dispense_confirmation_received",
    "chargeable_medication_items_validated",
    "payment_record_created",
    "settlement_status_recorded",
    "dispense_payment_audit_logged",
  ],
  pharmacyPaymentWorkflowStatus: "pass",
  regulatedActionHumanControlled: true,
} as const
