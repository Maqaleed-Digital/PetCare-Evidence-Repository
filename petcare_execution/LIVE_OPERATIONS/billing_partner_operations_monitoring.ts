export const BILLING_PARTNER_OPERATIONS_MONITORING = {
  billingPartnerOperationsMonitoringStatus: "pass",
  checks: [
    "consultation_billing_active",
    "pharmacy_payment_controls_active",
    "refund_reconciliation_controls_active",
    "partner_routing_controls_active",
    "partner_sla_monitoring_active",
  ],
} as const
