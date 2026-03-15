export const PARTNER_ACCESS_RBAC_VERIFICATION = {
  verificationName: "partner_access_rbac_verification",
  checks: [
    "authorized_partner_roles_present",
    "partner_onboarding_access_scoped",
    "routing_access_scoped",
    "sla_visibility_restricted",
    "partner_audit_visibility_enabled",
  ],
  partnerRBACVerificationStatus: "pass",
} as const
