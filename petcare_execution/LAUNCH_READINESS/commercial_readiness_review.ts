export const COMMERCIAL_READINESS_REVIEW = {
  status: "conditional",
  checks: [
    "booking_flow_path_defined",
    "customer_notification_path_defined",
    "payment_go_live_closure_pending",
    "partner_network_operational_closure_pending",
  ],
  unresolvedCommercialDependencyCount: 2,
  launchLimitations: [
    "billing_and_payment_go_live_closure_pending",
    "partner_network_operational_closure_pending",
  ],
} as const
