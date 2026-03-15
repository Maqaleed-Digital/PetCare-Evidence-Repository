export const SERVICE_QUALITY_AND_SLA_MONITORING = {
  serviceQualityAndSlaMonitoringStatus: "pass",
  checks: [
    "consultation_service_levels_monitored",
    "triage_response_targets_monitored",
    "pharmacy_service_window_monitored",
    "partner_sla_breach_visibility_enabled",
    "service_quality_review_cycle_active",
  ],
} as const
