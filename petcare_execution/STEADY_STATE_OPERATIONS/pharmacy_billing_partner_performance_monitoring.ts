export const PHARMACY_BILLING_PARTNER_PERFORMANCE_MONITORING = {
  pharmacyBillingPartnerPerformanceMonitoringStatus: "pass",
  checks: [
    "dispense_performance_monitoring_active",
    "billing_reconciliation_monitoring_active",
    "refund_exception_monitoring_active",
    "partner_routing_performance_monitoring_active",
    "partner_service_quality_monitoring_active",
  ],
} as const
