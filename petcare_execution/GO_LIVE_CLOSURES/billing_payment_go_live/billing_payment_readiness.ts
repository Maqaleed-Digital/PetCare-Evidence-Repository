export const BILLING_PAYMENT_READINESS = {
  billingPaymentStatus: "COMPLETE",
  coveredDomains: [
    "consultation_billing_workflow",
    "pharmacy_payment_workflow",
    "refund_reconciliation_controls",
    "payment_access_rbac_verification",
  ],
  assistiveOnlyBoundaryPreserved: true,
  humanApprovalStillRequired: true,
} as const
