import { BILLING_PAYMENT_READINESS } from "./billing_payment_readiness"
import { CONSULTATION_BILLING_WORKFLOW } from "./consultation_billing_workflow"
import { PHARMACY_PAYMENT_WORKFLOW } from "./pharmacy_payment_workflow"
import { REFUND_RECONCILIATION_CONTROLS } from "./refund_reconciliation_controls"
import { PAYMENT_ACCESS_RBAC_VERIFICATION } from "./payment_access_rbac_verification"
import { BILLING_PAYMENT_CLOSURE_DECISION } from "./billing_payment_closure_decision"

export function buildBillingPaymentValidationPack() {
  const requiredSymbolsConfirmed =
    BILLING_PAYMENT_READINESS.billingPaymentStatus === "COMPLETE" &&
    CONSULTATION_BILLING_WORKFLOW.consultationBillingWorkflowStatus === "pass" &&
    PHARMACY_PAYMENT_WORKFLOW.pharmacyPaymentWorkflowStatus === "pass" &&
    REFUND_RECONCILIATION_CONTROLS.refundReconciliationStatus === "pass" &&
    PAYMENT_ACCESS_RBAC_VERIFICATION.paymentRBACVerificationStatus === "pass" &&
    typeof BILLING_PAYMENT_CLOSURE_DECISION.closureDecision === "string"

  return {
    packId: "PETCARE-GO-LIVE-CLOSURE-3",
    requiredSymbolsConfirmed,
    billingPaymentStatus: BILLING_PAYMENT_READINESS.billingPaymentStatus,
    consultationBillingWorkflowStatus:
      CONSULTATION_BILLING_WORKFLOW.consultationBillingWorkflowStatus,
    pharmacyPaymentWorkflowStatus:
      PHARMACY_PAYMENT_WORKFLOW.pharmacyPaymentWorkflowStatus,
    refundReconciliationStatus:
      REFUND_RECONCILIATION_CONTROLS.refundReconciliationStatus,
    paymentRBACVerificationStatus:
      PAYMENT_ACCESS_RBAC_VERIFICATION.paymentRBACVerificationStatus,
    assistiveOnlyBoundaryPreserved:
      BILLING_PAYMENT_READINESS.assistiveOnlyBoundaryPreserved,
    humanApprovalStillRequired:
      BILLING_PAYMENT_READINESS.humanApprovalStillRequired &&
      CONSULTATION_BILLING_WORKFLOW.humanApprovalStillRequired &&
      PHARMACY_PAYMENT_WORKFLOW.regulatedActionHumanControlled,
    closureDecisionPresent:
      typeof BILLING_PAYMENT_CLOSURE_DECISION.closureDecision === "string",
    closureDecision: BILLING_PAYMENT_CLOSURE_DECISION.closureDecision,
    nextRecommendedState:
      BILLING_PAYMENT_CLOSURE_DECISION.nextRecommendedState,
  } as const
}
