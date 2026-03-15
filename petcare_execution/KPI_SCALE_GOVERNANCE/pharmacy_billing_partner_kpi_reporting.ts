export const PHARMACY_BILLING_PARTNER_KPI_REPORTING = {
  pharmacyBillingPartnerKpiReportingStatus: "pass",
  metrics: [
    "dispense_performance_reporting_active",
    "billing_reconciliation_reporting_active",
    "refund_exception_reporting_active",
    "partner_routing_performance_reporting_active",
    "partner_sla_reporting_active",
  ],
} as const
