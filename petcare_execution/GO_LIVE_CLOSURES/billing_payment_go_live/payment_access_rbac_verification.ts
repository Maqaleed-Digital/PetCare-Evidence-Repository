export const PAYMENT_ACCESS_RBAC_VERIFICATION = {
  verificationName: "payment_access_rbac_verification",
  checks: [
    "authorized_payment_roles_present",
    "consultation_billing_access_scoped",
    "pharmacy_payment_access_scoped",
    "refund_authorization_restricted",
    "payment_audit_visibility_enabled",
  ],
  paymentRBACVerificationStatus: "pass",
} as const
