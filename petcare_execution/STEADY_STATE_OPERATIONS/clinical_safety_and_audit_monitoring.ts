export const CLINICAL_SAFETY_AND_AUDIT_MONITORING = {
  clinicalSafetyAndAuditMonitoringStatus: "pass",
  checks: [
    "clinical_signoff_integrity_preserved",
    "escalation_audit_capture_active",
    "adverse_event_review_path_available",
    "clinical_audit_review_cycle_active",
    "regulated_action_traceability_preserved",
  ],
} as const
